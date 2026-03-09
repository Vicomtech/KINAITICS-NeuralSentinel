from flask import Blueprint, request, jsonify, current_app
from pathlib import Path
import json
from datetime import datetime
import uuid
import os
import math
import numpy as np

bp = Blueprint('evaluations', __name__, url_prefix='/api/evaluations')

def _sanitize_for_json(obj):
    """Recursively replace NaN/Inf float values so json.dump never fails."""
    if (obj is None or isinstance(obj, (bool, str, int))):
        return obj
    if isinstance(obj, (np.ndarray, list, tuple)):
        return [_sanitize_for_json(v) for v in obj]
    if isinstance(obj, dict):
        return {str(k): _sanitize_for_json(v) for k, v in obj.items()}
    if isinstance(obj, (np.float32, np.float64, float)):
        val = float(obj)
        if math.isnan(val): return None
        if math.isinf(val): return 1e308 if val > 0 else -1e308
        return val
    if isinstance(obj, (np.int32, np.int64, np.integer)):
        return int(obj)
    return str(obj)


active_evaluations = {}

class LogRedirector:
    def __init__(self, eval_id, original_stream):
        self.eval_id = eval_id
        self.original_stream = original_stream

    def write(self, data):
        # Filter out obvious server/request logs to avoid flooding the monitor
        # but keep it permissive for user prints
        is_request_log = any(x in data for x in ["GET /api/", "POST /api/", "DEBUG:werkzeug", "INFO:werkzeug"])
        
        if data.strip() and not is_request_log:
            timestamp = datetime.now().strftime("%H:%M:%S")
            # Ensure we don't add multiple timestamps if data already has one from a previous write
            log_entry = f"[{timestamp}] {data.strip()}"
            if self.eval_id in active_evaluations:
                if 'logs' not in active_evaluations[self.eval_id]:
                    active_evaluations[self.eval_id]['logs'] = []
                active_evaluations[self.eval_id]['logs'].append(log_entry)
        
        # Always write to the original stream (terminal)
        self.original_stream.write(data)

    def flush(self):
        self.original_stream.flush()

@bp.route('/', methods=['POST'])
def create_evaluation():
    """Create a new evaluation"""
    try:
        data = request.get_json()
        
        model_id = data.get('model_id')
        dataset_id = data.get('dataset_id')
        metrics = data.get('metrics', [])
        
        if not model_id or not dataset_id:
            return jsonify({'error': 'Model and dataset are required'}), 400
        
        if not metrics:
            return jsonify({'error': 'At least one metric must be selected'}), 400
        
        # Generate evaluation ID
        eval_id = str(uuid.uuid4())
        
        # Create evaluation metadata
        evaluation = {
            'id': eval_id,
            'model_id': model_id,
            'dataset_id': dataset_id,
            'metrics': metrics,
            'status': 'pending',
            'progress': 0,
            'created_at': datetime.now().isoformat(),
            'started_at': None,
            'completed_at': None,
            'results': None,
            'error': None,
            'results': None,
            'error': None,
            'metric_statuses': {m: {'status': 'pending', 'progress': 0} for m in metrics},
            'logs': [],
            'cancelled': False
        }
        
        # Store in active evaluations
        active_evaluations[eval_id] = evaluation
        
        # Save to history
        history_file = current_app.config['EVALUATIONS_DIR'] / 'history.json'
        if history_file.exists():
            with open(history_file, 'r') as f:
                history = json.load(f)
        else:
            history = []
        
        history.append(evaluation)
        
        with open(history_file, 'w') as f:
            json.dump(_sanitize_for_json(history), f, indent=2)
        
        return jsonify(evaluation), 201
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/<eval_id>/start', methods=['POST'])
def start_evaluation(eval_id):
    """Start running an evaluation"""
    try:
        if eval_id not in active_evaluations:
            return jsonify({'error': 'Evaluation not found'}), 404
        
        evaluation = active_evaluations[eval_id]
        
        if evaluation['status'] != 'pending':
            return jsonify({'error': f'Evaluation already {evaluation["status"]}'}), 400
        
        # Update status
        evaluation['status'] = 'running'
        evaluation['started_at'] = datetime.now().isoformat()
        evaluation['progress'] = 10
        
        # Run evaluation in background with app context
        import threading
        from flask import current_app
        
        app = current_app._get_current_object()
        thread = threading.Thread(target=run_evaluation_with_context, args=(eval_id, app))
        thread.daemon = True
        thread.start()
        
        return jsonify(evaluation), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

def run_evaluation_with_context(eval_id, app):
    """Wrapper to run evaluation with Flask app context"""
    with app.app_context():
        import sys
        eval_id_val = eval_id # local copy
        original_stdout = sys.stdout
        original_stderr = sys.stderr
        sys.stdout = LogRedirector(eval_id_val, original_stdout)
        sys.stderr = LogRedirector(eval_id_val, original_stderr)
        try:
            # Import metrics here to ensure they use the redirected stdout if they were not imported yet
            # Actually they are already imported by PluginManager, but print() looks at sys.stdout at runtime.
            run_evaluation(eval_id_val)
        finally:
            # Restore
            sys.stdout = original_stdout
            sys.stderr = original_stderr

def run_evaluation(eval_id):
    """Background task to run evaluation"""
    evaluation = active_evaluations.get(eval_id)
    if not evaluation:
        return
    
    try:
        from flask import current_app
        
        # Load model metadata
        model_id = evaluation['model_id']
        dataset_id = evaluation['dataset_id']
        
        models_metadata_file = current_app.config['MODELS_DIR'] / 'metadata.json'
        
        if not models_metadata_file.exists():
            evaluation['status'] = 'error'
            evaluation['error'] = 'Models metadata not found'
            evaluation['completed_at'] = datetime.now().isoformat()
            return
            
        with open(models_metadata_file, 'r') as f:
            models = json.load(f)
        model = next((m for m in models if m['id'] == model_id), None)
        
        if not model:
            evaluation['status'] = 'error'
            evaluation['error'] = 'Model not found'
            evaluation['completed_at'] = datetime.now().isoformat()
            return
        
        # Load dataset metadata
        datasets_metadata_file = current_app.config['DATASETS_DIR'] / 'metadata.json'
        
        if not datasets_metadata_file.exists():
            evaluation['status'] = 'error'
            evaluation['error'] = 'Datasets metadata not found'
            evaluation['completed_at'] = datetime.now().isoformat()
            return
            
        with open(datasets_metadata_file, 'r') as f:
            datasets = json.load(f)
        dataset = next((d for d in datasets if d['id'] == dataset_id), None)
        
        if not dataset:
            evaluation['status'] = 'error'
            evaluation['error'] = 'Dataset not found'
            evaluation['completed_at'] = datetime.now().isoformat()
            return
        
        evaluation['progress'] = 30
        
        # Load actual dataset
        import numpy as np
        
        data_path = current_app.config['DATASETS_DIR'] / dataset['data_file']
        
        if not os.path.exists(data_path):
            evaluation['status'] = 'error'
            evaluation['error'] = f'Dataset file not found: {dataset["data_file"]}'
            evaluation['completed_at'] = datetime.now().isoformat()
            return
            
        X_test = np.load(data_path, allow_pickle=True)
        
        y_test = None
        if dataset.get('has_labels') and dataset.get('labels_file'):
            labels_path = current_app.config['DATASETS_DIR'] / dataset['labels_file']
            if os.path.exists(labels_path):
                y_test = np.load(labels_path, allow_pickle=True)
        
        evaluation['progress'] = 50
        
        # Load model ONCE before the loop
        print(f"DEBUG: Loading model {model['name']}...")
        import tensorflow as tf_loader
        try:
            loaded_model = tf_loader.keras.models.load_model(str(model['path']))
            print(f"DEBUG: Model loaded successfully")
        except Exception as e:
            print(f"ERROR: Failed to load model: {str(e)}")
            evaluation['status'] = 'error'
            evaluation['error'] = f'Error loading model: {str(e)}'
            evaluation['completed_at'] = datetime.now().isoformat()
            return

        plugin_manager = current_app.config['PLUGIN_MANAGER']
        results = {}
        evaluation['progress'] = 60
        
        num_metrics = len(evaluation['metrics'])
        for idx, metric_name in enumerate(evaluation['metrics']):
            # Check for cancellation
            if evaluation.get('cancelled') or evaluation.get('status') == 'cancelled':
                print(f"DEBUG: Evaluation {eval_id} cancelled.")
                break

            evaluation['metric_statuses'][metric_name] = {'status': 'running', 'progress': 0}
            try:
                # Simulate progress updates for the metric
                evaluation['metric_statuses'][metric_name]['progress'] = 10
                evaluation['progress'] = 50 + int((idx + 0.1) * (40 / num_metrics))
                
                # Update progress intermediate
                evaluation['metric_statuses'][metric_name]['progress'] = 30
                import time
                time.sleep(0.5) # Simulate some work
                evaluation['metric_statuses'][metric_name]['progress'] = 60
                
                # Find plugin (Case-insensitive search)
                plugin = None
                plugin_category = 'unknown'
                
                # DEBUG INFO
                print(f"DEBUG: Searching for plugin '{metric_name}'")
                
                # PluginManager structure:
                # self.plugins = { 'name': instance }  <-- Flat dictionary
                # self.plugins_by_type = { 'category': ['name1', 'name2'] }
                
                # 1. Direct Search in flat dictionary (Best case)
                if metric_name in plugin_manager.plugins:
                    plugin = plugin_manager.plugins[metric_name]
                    # Determine category from manifest
                    plugin_category = plugin.manifest().get('type', 'unknown')
                    print(f"DEBUG: Found direct match: {metric_name} ({plugin_category})")
                
                # 2. Case-insensitive Search in flat dictionary
                else:
                    print("DEBUG: Direct match failed, trying case-insensitive...")
                    for p_name, p_instance in plugin_manager.plugins.items():
                        # Check keys: name, display_name
                        manifest = p_instance.manifest()
                        possible_names = [
                            p_name.lower(),
                            manifest.get('name', '').lower(),
                            manifest.get('display_name', '').lower()
                        ]
                        
                        if metric_name.lower() in possible_names:
                            plugin = p_instance
                            plugin_category = manifest.get('type', 'unknown')
                            print(f"DEBUG: Found fuzzy match: {p_name} ({plugin_category})")
                            break
                
                if not plugin:
                    print(f"ERROR: Plugin '{metric_name}' definitely NOT found.")
                    print(f"DEBUG: Available plugins: {list(plugin_manager.plugins.keys())}")
                    
                    results[metric_name] = {
                        'status': 'error',
                        'error': f'Plugin {metric_name} not found.',
                        'category': 'unknown'
                    }
                    continue
                
                # Execute Plugin
                plugin.build(loaded_model, {})
                
                # Call the metric — pass labels if available
                import inspect
                sig = inspect.signature(plugin.__call__)
                params = list(sig.parameters.keys())
                if y_test is not None and any(p in params for p in ('labels', 'y_test')):
                    metric_result = plugin(X_test, y_test)
                else:
                    metric_result = plugin(X_test)
                
                # Handle visualization
                viz_path = None
                if hasattr(plugin, 'view'):
                    try:
                        import matplotlib
                        matplotlib.use('Agg')
                        import matplotlib.pyplot as plt
                        
                        fig = plugin.view()
                        if fig:
                            eval_images_dir = current_app.config['EVALUATIONS_DIR'] / eval_id / 'images'
                            os.makedirs(eval_images_dir, exist_ok=True)
                            
                            safe_name = "".join([c for c in metric_name if c.isalpha() or c.isdigit() or c==' ']).rstrip().replace(" ", "_")
                            image_filename = f"{safe_name}.png"
                            image_path = eval_images_dir / image_filename
                            
                            fig.savefig(image_path, bbox_inches='tight')
                            plt.close(fig)
                            viz_path = f'/api/evaluations/{eval_id}/images/{image_filename}'
                    except Exception as ve:
                        print(f"Visualization error for {metric_name}: {ve}")
                
                # Normalize score to 0-100 scale if it's in 0-1 range
                raw_score = metric_result.get('score', 0.0)
                if isinstance(raw_score, (int, float)) and 0 <= raw_score <= 1:
                    score = raw_score * 100
                else:
                    score = raw_score

                results[metric_name] = {
                    'status': 'completed',
                    'score': score,
                    'category': plugin_category,
                    'details': metric_result.get('details', {}),
                    'warnings': metric_result.get('warnings', []),
                    'recommendations': metric_result.get('recommendations', []),
                    'visualization': viz_path
                }
                evaluation['metric_statuses'][metric_name] = {'status': 'completed', 'progress': 100}
                
            except Exception as e:
                results[metric_name] = {
                    'status': 'error',
                    'error': str(e),
                    'category': 'unknown'
                }
                evaluation['metric_statuses'][metric_name] = {'status': 'error', 'progress': 0, 'error': str(e)}
        
        evaluation['progress'] = 95
        
        # Update evaluation with results
        evaluation['status'] = 'completed'
        evaluation['completed_at'] = datetime.now().isoformat()
        evaluation['progress'] = 100
        evaluation['results'] = results
        
        # Save final results with logs
        results_dir = current_app.config['EVALUATIONS_DIR']
        os.makedirs(results_dir, exist_ok=True)
        
        results_file = results_dir / f'{eval_id}_results.json'
        with open(results_file, 'w') as f:
            json.dump(_sanitize_for_json(evaluation), f, indent=2)
        
        # Update history
        history_file = results_dir / 'history.json'
        
        if history_file.exists():
            with open(history_file, 'r') as f:
                history = json.load(f)
        else:
            history = []
        
        # Update or append
        found = False
        for i, item in enumerate(history):
            if item['id'] == eval_id:
                history[i] = evaluation
                found = True
                break
        
        if not found:
            history.append(evaluation)
        
        with open(history_file, 'w') as f:
            json.dump(_sanitize_for_json(history), f, indent=2)
        
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        
        evaluation['status'] = 'error'
        evaluation['error'] = f'{str(e)}\n\nDetails:\n{error_details}'
        evaluation['completed_at'] = datetime.now().isoformat()
        evaluation['progress'] = 0
        
        print(f"Error in evaluation {eval_id}:")
        print(error_details)

@bp.route('/<eval_id>/logs', methods=['GET'])
def get_evaluation_logs(eval_id):
    """Get live logs for an evaluation"""
    try:
        since = int(request.args.get('since', 0))
        
        # Check active evaluations
        if eval_id in active_evaluations:
            logs = active_evaluations[eval_id].get('logs', [])
            return jsonify({
                'logs': logs[since:],
                'next_index': len(logs)
            }), 200
        
        # Check in history/results file if finished
        results_file = current_app.config['EVALUATIONS_DIR'] / f'{eval_id}_results.json'
        if results_file.exists():
            with open(results_file, 'r') as f:
                results = json.load(f)
            logs = results.get('logs', [])
            return jsonify({
                'logs': logs[since:],
                'next_index': len(logs)
            }), 200
            
        return jsonify({'error': 'Evaluation not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/<eval_id>/status', methods=['GET'])
def get_evaluation_status(eval_id):
    """Get status of an evaluation"""
    try:
        if eval_id in active_evaluations:
            return jsonify(_sanitize_for_json(active_evaluations[eval_id])), 200
        
        # Check in history
        history_file = current_app.config['EVALUATIONS_DIR'] / 'history.json'
        if history_file.exists():
            with open(history_file, 'r') as f:
                history = json.load(f)
            
            evaluation = next((e for e in history if e['id'] == eval_id), None)
            if evaluation:
                return jsonify(evaluation), 200
        
        return jsonify({'error': 'Evaluation not found'}), 404
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/history', methods=['GET'])
def get_evaluation_history():
    """Get all evaluation history"""
    try:
        history_file = current_app.config['EVALUATIONS_DIR'] / 'history.json'
        
        if not history_file.exists():
            return jsonify([]), 200
        
        with open(history_file, 'r') as f:
            history = json.load(f)
        
        return jsonify(history), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/<eval_id>/results', methods=['GET'])
def get_evaluation_results(eval_id):
    """Get detailed results of an evaluation"""
    try:
        results_file = current_app.config['EVALUATIONS_DIR'] / f'{eval_id}_results.json'
        
        if not results_file.exists():
            # Try to get from active evaluations
            if eval_id in active_evaluations:
                return jsonify(active_evaluations[eval_id]), 200
            return jsonify({'error': 'Results not found'}), 404
        
        with open(results_file, 'r') as f:
            results = json.load(f)
        
        return jsonify(results), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/<eval_id>/cancel', methods=['POST'])
def cancel_evaluation(eval_id):
    """Cancel a running evaluation"""
    try:
        if eval_id in active_evaluations:
            evaluation = active_evaluations[eval_id]
            if evaluation['status'] == 'running':
                evaluation['status'] = 'cancelled'
                evaluation['cancelled'] = True
                evaluation['completed_at'] = datetime.now().isoformat()
                evaluation['error'] = 'Evaluación cancelada por el usuario.'
                print(f"DEBUG: Cancellation requested for {eval_id}")
                return jsonify({'message': 'Evaluation cancellation requested'}), 200
            else:
                return jsonify({'error': f'Cannot cancel evaluation in status {evaluation["status"]}'}), 400
        
        return jsonify({'error': 'Active evaluation not found'}), 404
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/<eval_id>', methods=['DELETE'])
def delete_evaluation(eval_id):
    """Delete an evaluation result"""
    try:
        # Check active evaluations first
        if eval_id in active_evaluations:
            return jsonify({'error': 'Cannot delete a running evaluation'}), 400
            
        history_dir = current_app.config['EVALUATIONS_DIR']
        
        # 1. Remove specific results file
        eval_file = history_dir / f"{eval_id}_results.json"
        if eval_file.exists():
            os.remove(eval_file)
            
        # 2. Update history.json
        history_file = history_dir / 'history.json'
        if history_file.exists():
            with open(history_file, 'r') as f:
                history = json.load(f)
            
            # Filter out the deleted evaluation
            new_history = [e for e in history if e['id'] != eval_id]
            
            if len(new_history) < len(history):
                with open(history_file, 'w') as f:
                    json.dump(_sanitize_for_json(new_history), f, indent=2)
            else:
                return jsonify({'error': 'Evaluation not found in history'}), 404
        else:
            return jsonify({'error': 'History file not found'}), 404
            
        return jsonify({'message': 'Evaluation deleted successfully'}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

def _load_eval_context(eval_id):
    """Helper to load evaluation context (model, dataset)"""
    from flask import current_app
    import json
    import os
    
    # 1. Find Evaluation
    evaluation = None
    if eval_id in active_evaluations:
        evaluation = active_evaluations[eval_id]
    else:
        history_file = current_app.config['EVALUATIONS_DIR'] / 'history.json'
        if history_file.exists():
            with open(history_file, 'r') as f:
                history = json.load(f)
            evaluation = next((e for e in history if e['id'] == eval_id), None)
            
    if not evaluation:
        raise ValueError("Evaluation not found")

    # 2. Load Metadata
    model_id = evaluation['model_id']
    dataset_id = evaluation['dataset_id']
    
    models_file = current_app.config['MODELS_DIR'] / 'metadata.json'
    if not models_file.exists():
         raise ValueError("Models metadata not found")
    with open(models_file, 'r') as f:
        models = json.load(f)
    model = next((m for m in models if m['id'] == model_id), None)
    
    datasets_file = current_app.config['DATASETS_DIR'] / 'metadata.json'
    if not datasets_file.exists():
         raise ValueError("Datasets metadata not found")
    with open(datasets_file, 'r') as f:
        datasets = json.load(f)
    dataset = next((d for d in datasets if d['id'] == dataset_id), None)

    if not model or not dataset:
         raise ValueError("Model or Dataset not found")

    # 3. Load Data
    import numpy as np
    data_path = current_app.config['DATASETS_DIR'] / dataset['data_file']
    if not os.path.exists(data_path):
        raise ValueError(f"Data file not found: {data_path}")
        
    X_test = np.load(data_path, allow_pickle=True)
    
    y_test = None
    if dataset.get('has_labels') and dataset.get('labels_file'):
        labels_path = current_app.config['DATASETS_DIR'] / dataset['labels_file']
        if os.path.exists(labels_path):
            y_test = np.load(labels_path, allow_pickle=True)
            
    return evaluation, model, dataset, X_test, y_test

@bp.route('/<eval_id>/visualize/<metric_name>', methods=['GET'])
def get_metric_visualization(eval_id, metric_name):
    """Generate and return visualization for a specific metric"""
    try:
        # Load context
        evaluation, model, dataset, X_test, y_test = _load_eval_context(eval_id)
        
        # Load Plugin
        plugin_manager = current_app.config['PLUGIN_MANAGER']
        plugin = None
        
        # Logic to find plugin (copied/adapted from run_evaluation)
        if metric_name in plugin_manager.plugins:
            plugin = plugin_manager.plugins[metric_name]
        else:
             for p_name, p_instance in plugin_manager.plugins.items():
                manifest = p_instance.manifest()
                possible_names = [
                    p_name.lower(),
                    manifest.get('name', '').lower(),
                    manifest.get('display_name', '').lower()
                ]
                if metric_name.lower() in possible_names:
                    plugin = p_instance
                    break
        
        if not plugin:
            return jsonify({'error': f'Plugin {metric_name} not found'}), 404
            
        if not hasattr(plugin, 'view'):
             return jsonify({'error': 'Plugin does not support visualization'}), 400

        # Execute View
        try:
            # Load the actual TF model from disk
            import tensorflow as tf_loader
            loaded_model = tf_loader.keras.models.load_model(str(model['path']))
            plugin.build(loaded_model, {})
            
            # We must run __call__() to populate plugin state before view()
            import inspect
            sig = inspect.signature(plugin.__call__)
            params = list(sig.parameters.keys())
            if y_test is not None and any(p in params for p in ('labels', 'y_test')):
                plugin(X_test, y_test)
            else:
                plugin(X_test)
                
        except Exception as e:
            import traceback
            error_details = traceback.format_exc()
            print(f"ERROR preparing plugin {metric_name} for visualization:")
            print(error_details)
            # Continue anyway, maybe view() handles it or fails gracefully
            pass 

        # Prepare Matplotlib Backend BEFORE view()
        import matplotlib
        matplotlib.use('Agg')
        import matplotlib.pyplot as plt

        try:
             fig = plugin.view()
        except Exception as e:
             return jsonify({'error': f'Plugin view() error: {str(e)}'}), 500

        if not fig:
             return jsonify({'error': 'Visualization generation failed (no figure returned)'}), 500
             
        import io
        import base64
        
        buf = io.BytesIO()
        fig.savefig(buf, format='png', bbox_inches='tight')
        buf.seek(0)
        img_base64 = base64.b64encode(buf.read()).decode('utf-8')
        plt.close(fig)
        
        return jsonify({'image': img_base64}), 200

    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

@bp.route('/<eval_id>/images/<filename>', methods=['GET'])
def get_evaluation_image(eval_id, filename):
    """Serve evaluation images"""
    try:
        from flask import current_app, send_from_directory
        eval_images_dir = current_app.config['EVALUATIONS_DIR'] / eval_id / 'images'
        return send_from_directory(eval_images_dir, filename)
    except Exception as e:
        return jsonify({'error': str(e)}), 404
