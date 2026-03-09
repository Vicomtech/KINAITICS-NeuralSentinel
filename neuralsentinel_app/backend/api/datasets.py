from flask import Blueprint, request, jsonify, current_app
from pathlib import Path
import json
from datetime import datetime
import uuid
import os
import numpy as np
from werkzeug.utils import secure_filename

bp = Blueprint('datasets', __name__, url_prefix='/api/datasets')

@bp.route('/', methods=['GET'])
def get_datasets():
    """Get all datasets"""
    try:
        metadata_file = current_app.config['DATASETS_DIR'] / 'metadata.json'
        
        if not metadata_file.exists():
            return jsonify([]), 200
        
        with open(metadata_file, 'r') as f:
            datasets = json.load(f)
        
        return jsonify(datasets), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/upload', methods=['POST'])
def upload_dataset():
    """Upload a new dataset with data and optional labels"""
    try:
        if 'data_file' not in request.files:
            return jsonify({'error': 'No data file provided'}), 400
        
        data_file = request.files['data_file']
        labels_file = request.files.get('labels_file')  # Optional
        name = request.form.get('name', '')
        description = request.form.get('description', '')
        
        if data_file.filename == '':
            return jsonify({'error': 'Empty filename'}), 400
        
        if not (data_file.filename.endswith('.npy') or data_file.filename.endswith('.npz')):
            return jsonify({'error': 'Only .npy and .npz files are allowed'}), 400
        
        # Validate labels file if provided
        if labels_file and labels_file.filename:
            if not (labels_file.filename.endswith('.npy') or labels_file.filename.endswith('.npz')):
                return jsonify({'error': 'Labels file must be .npy or .npz'}), 400
        
        # Generate unique ID
        dataset_id = str(uuid.uuid4())
        
        # Save data file
        data_filename = secure_filename(f"{dataset_id}_data.npy")
        data_path = current_app.config['DATASETS_DIR'] / data_filename
        data_file.save(data_path)
        
        # Save labels file if provided
        labels_filename = None
        labels_path = None
        has_labels = False
        
        if labels_file and labels_file.filename:
            labels_filename = secure_filename(f"{dataset_id}_labels.npy")
            labels_path = current_app.config['DATASETS_DIR'] / labels_filename
            labels_file.save(labels_path)
            has_labels = True
            
            # Validate that data and labels have same length
            try:
                data_array = np.load(data_path, allow_pickle=True)
                labels_array = np.load(labels_path, allow_pickle=True)
                
                if len(data_array) != len(labels_array):
                    # Clean up files
                    os.remove(data_path)
                    os.remove(labels_path)
                    return jsonify({
                        'error': f'Data and labels length mismatch: {len(data_array)} vs {len(labels_array)}'
                    }), 400
            except Exception as e:
                # Clean up files
                os.remove(data_path)
                if labels_path and os.path.exists(labels_path):
                    os.remove(labels_path)
                return jsonify({'error': f'Error validating files: {str(e)}'}), 400
        
        # Get file size
        file_size = os.path.getsize(data_path)
        if labels_path:
            file_size += os.path.getsize(labels_path)
        
        # Create metadata
        metadata = {
            'id': dataset_id,
            'name': name,
            'description': description,
            'data_file': data_filename,
            'labels_file': labels_filename,
            'has_labels': has_labels,
            'format': '.npy',
            'size': file_size,
            'upload_date': datetime.now().isoformat()
        }
        
        # Save metadata
        metadata_file = current_app.config['DATASETS_DIR'] / 'metadata.json'
        if metadata_file.exists():
            with open(metadata_file, 'r') as f:
                all_metadata = json.load(f)
        else:
            all_metadata = []
        
        all_metadata.append(metadata)
        
        with open(metadata_file, 'w') as f:
            json.dump(all_metadata, f, indent=2)
        
        return jsonify(metadata), 201
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/<dataset_id>', methods=['GET'])
def get_dataset(dataset_id):
    """Get a specific dataset"""
    try:
        metadata_file = current_app.config['DATASETS_DIR'] / 'metadata.json'
        
        if not metadata_file.exists():
            return jsonify({'error': 'Dataset not found'}), 404
        
        with open(metadata_file, 'r') as f:
            datasets = json.load(f)
        
        dataset = next((d for d in datasets if d['id'] == dataset_id), None)
        
        if not dataset:
            return jsonify({'error': 'Dataset not found'}), 404
        
        return jsonify(dataset), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/<dataset_id>', methods=['DELETE'])
def delete_dataset(dataset_id):
    """Delete a dataset"""
    try:
        metadata_file = current_app.config['DATASETS_DIR'] / 'metadata.json'
        
        if not metadata_file.exists():
            return jsonify({'error': 'Dataset not found'}), 404
        
        with open(metadata_file, 'r') as f:
            datasets = json.load(f)
        
        dataset = next((d for d in datasets if d['id'] == dataset_id), None)
        
        if not dataset:
            return jsonify({'error': 'Dataset not found'}), 404
        
        # Delete data file
        data_path = current_app.config['DATASETS_DIR'] / dataset['data_file']
        if os.path.exists(data_path):
            os.remove(data_path)
        
        # Delete labels file if exists
        if dataset.get('labels_file'):
            labels_path = current_app.config['DATASETS_DIR'] / dataset['labels_file']
            if os.path.exists(labels_path):
                os.remove(labels_path)
        
        # Remove from metadata
        datasets = [d for d in datasets if d['id'] != dataset_id]
        
        with open(metadata_file, 'w') as f:
            json.dump(datasets, f, indent=2)
        
        return jsonify({'message': 'Dataset deleted'}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500
@bp.route('/<dataset_id>/preview', methods=['GET'])
def get_dataset_preview(dataset_id):
    """Get dataset preview (images or tabular data)"""
    try:
        metadata_file = current_app.config['DATASETS_DIR'] / 'metadata.json'
        
        if not metadata_file.exists():
            return jsonify({'error': 'Dataset not found'}), 404
            
        with open(metadata_file, 'r') as f:
            datasets = json.load(f)
        
        dataset = next((d for d in datasets if d['id'] == dataset_id), None)
        
        if not dataset:
            return jsonify({'error': 'Dataset not found'}), 404
            
        data_path = current_app.config['DATASETS_DIR'] / dataset['data_file']
        if not data_path.exists():
            return jsonify({'error': 'Data file not found'}), 404
            
        # Load subset of data
        try:
            # We use mmap_mode='r' to avoid loading everything if possible for .npy
            if str(data_path).endswith('.npy'):
                data = np.load(data_path, mmap_mode='r')
            else:
                data = np.load(data_path)
                if isinstance(data, np.lib.npyio.NpzFile):
                    # For npz, usually 'arr_0' or 'x_test' etc. We try keys.
                    keys = list(data.keys())
                    if 'x_test' in keys:
                        data = data['x_test']
                    elif 'x_train' in keys:
                        data = data['x_train']
                    elif 'arr_0' in keys:
                        data = data['arr_0']
                    else:
                        data = data[keys[0]]

            # Convert to numpy if it's not
            data = np.array(data)
            
            shape = data.shape
            preview_limit = 20
            subset = data[:preview_limit]
            
            # Detect Image Data (4D: N, H, W, C or N, C, H, W)
            # Or 3D (N, H, W) for grayscale
            is_image = False
            if len(shape) == 4 or len(shape) == 3:
                # Check bounds (0-1 or 0-255) to be sure? 
                # Heuristic: dimension sizes.
                # If last dim is 1 or 3, likely channels (H, W, C)
                # If second idm is 1 or 3, likely channels (C, H, W)
                is_image = True
            
            response = {
                'shape': shape,
                'dtype': str(data.dtype),
                'type': 'tabular',
                'data': []
            }
            
            if is_image:
                response['type'] = 'images'
                import base64
                import io
                from PIL import Image
                
                images_base64 = []
                
                for i in range(len(subset)):
                    img_arr = subset[i]
                    
                    # Normalize to 0-255 uint8
                    if img_arr.max() <= 1.0:
                        img_arr = (img_arr * 255).astype(np.uint8)
                    else:
                        img_arr = img_arr.astype(np.uint8)
                    
                    # Handle channels first (C, H, W) -> (H, W, C)
                    if len(img_arr.shape) == 3 and (img_arr.shape[0] == 1 or img_arr.shape[0] == 3):
                        img_arr = np.transpose(img_arr, (1, 2, 0))
                    
                    # Handle grayscale (H, W, 1) -> (H, W) for PIL
                    if len(img_arr.shape) == 3 and img_arr.shape[2] == 1:
                        img_arr = img_arr.reshape(img_arr.shape[0], img_arr.shape[1])
                    
                    try:
                        img = Image.fromarray(img_arr)
                        # Resize for thumbnail if too big
                        img.thumbnail((150, 150))
                        
                        buffer = io.BytesIO()
                        img.save(buffer, format='PNG')
                        img_str = base64.b64encode(buffer.getvalue()).decode('utf-8')
                        images_base64.append(img_str)
                    except Exception as img_err:
                        print(f"Error converting image {i}: {img_err}")
                        # Fallback or skip
                
                response['data'] = images_base64
                
            else:
                # Tabular data
                # Flatten complex structures or just send first 20 rows
                if len(shape) > 2:
                     # Flatten for table view if high dim but not image
                     subset = subset.reshape(subset.shape[0], -1)
                
                # Convert to list for JSON
                response['data'] = subset.tolist()
                
            return jsonify(response), 200
            
        except Exception as e:
            return jsonify({'error': f'Failed to process data file: {str(e)}'}), 500
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500
