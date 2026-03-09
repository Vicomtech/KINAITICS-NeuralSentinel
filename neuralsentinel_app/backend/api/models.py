from flask import Blueprint, request, jsonify, current_app
from werkzeug.utils import secure_filename
import os
import json
import uuid
from datetime import datetime
from pathlib import Path

bp = Blueprint('models', __name__)

def get_metadata_file():
    """Get path to models metadata file"""
    return current_app.config['MODELS_DIR'] / 'metadata.json'

def load_metadata():
    """Load models metadata"""
    metadata_file = get_metadata_file()
    if metadata_file.exists():
        with open(metadata_file, 'r') as f:
            return json.load(f)
    return []

def save_metadata(metadata):
    """Save models metadata"""
    metadata_file = get_metadata_file()
    with open(metadata_file, 'w') as f:
        json.dump(metadata, f, indent=2)

@bp.route('', methods=['GET'])
def get_models():
    """Get all models"""
    try:
        metadata = load_metadata()
        return jsonify(metadata), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/<model_id>', methods=['GET'])
def get_model(model_id):
    """Get specific model"""
    try:
        metadata = load_metadata()
        model = next((m for m in metadata if m['id'] == model_id), None)
        
        if not model:
            return jsonify({'error': 'Model not found'}), 404
        
        return jsonify(model), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/upload', methods=['POST'])
def upload_model():
    """Upload a new model"""
    try:
        # Validate request
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'Empty filename'}), 400
        
        name = request.form.get('name')
        framework = request.form.get('framework', 'tensorflow')
        description = request.form.get('description', '')
        
        if not name:
            return jsonify({'error': 'Model name is required'}), 400
        
        # Generate unique ID
        model_id = str(uuid.uuid4())
        
        # Save file
        filename = secure_filename(file.filename)
        file_ext = Path(filename).suffix
        save_path = current_app.config['MODELS_DIR'] / f"{model_id}{file_ext}"
        file.save(save_path)
        
        # Get file size
        file_size = os.path.getsize(save_path)
        
        # Create metadata entry
        model_data = {
            'id': model_id,
            'name': name,
            'framework': framework,
            'format': file_ext,
            'path': str(save_path),
            'size': file_size,
            'upload_date': datetime.now().isoformat(),
            'metadata': {
                'description': description,
                'original_filename': filename
            }
        }
        
        # Save metadata
        metadata = load_metadata()
        metadata.append(model_data)
        save_metadata(metadata)
        
        return jsonify(model_data), 201
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/<model_id>', methods=['DELETE'])
def delete_model(model_id):
    """Delete a model"""
    try:
        metadata = load_metadata()
        model = next((m for m in metadata if m['id'] == model_id), None)
        
        if not model:
            return jsonify({'error': 'Model not found'}), 404
        
        # Delete file
        model_path = Path(model['path'])
        if model_path.exists():
            os.remove(model_path)
        
        # Remove from metadata
        metadata = [m for m in metadata if m['id'] != model_id]
        save_metadata(metadata)
        
        return jsonify({'message': 'Model deleted successfully'}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500
@bp.route('/<model_id>/architecture', methods=['GET'])
def get_model_architecture(model_id):
    """Get model architecture details"""
    try:
        metadata = load_metadata()
        model_meta = next((m for m in metadata if m['id'] == model_id), None)
        
        if not model_meta:
            return jsonify({'error': 'Model not found'}), 404
            
        model_path = Path(model_meta['path'])
        if not model_path.exists():
            return jsonify({'error': 'Model file not found'}), 404
            
        framework = model_meta.get('framework', 'unknown').lower()
        architecture = {}
        
        if framework == 'tensorflow':
            import tensorflow as tf
            import contextlib
            import io
            
            try:
                # Load model
                model = tf.keras.models.load_model(str(model_path))
                
                # Get config (JSON structure)
                architecture['config'] = json.loads(model.to_json())
                
                # Get summary as string
                stream = io.StringIO()
                with contextlib.redirect_stdout(stream):
                    model.summary()
                architecture['summary'] = stream.getvalue()
                
            except Exception as e:
                return jsonify({'error': f'Failed to load TensorFlow model: {str(e)}'}), 500
                
        elif framework == 'pytorch':
            import torch
            
            try:
                # Load model (usually loads structure + weights if full model saved)
                # Note: This is tricky for PyTorch as it often needs class definition
                # We'll try torch.load and see if we can get structure
                try:
                    model = torch.load(str(model_path), map_location='cpu')
                    architecture['summary'] = str(model)
                    
                    # Try to get state dict keys if it's just weights
                    if isinstance(model, dict) and 'state_dict' in model:
                        architecture['summary'] = "State Dict Key-Values:\n" + "\n".join(model['state_dict'].keys())
                    elif isinstance(model, dict):
                        architecture['summary'] = "Dictionary Keys:\n" + "\n".join(model.keys())
                        
                except Exception as e:
                    # Fallback
                    architecture['summary'] = f"Could not fully load PyTorch model structure.\nError: {str(e)}\n\n(Note: PyTorch models often require original class definitions to be loaded)"
                    
            except Exception as e:
                return jsonify({'error': f'Failed to load PyTorch model: {str(e)}'}), 500
        
        else:
            return jsonify({'error': f'Unsupported framework: {framework}'}), 400
            
        return jsonify(architecture), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500
