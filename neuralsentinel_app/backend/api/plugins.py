from flask import Blueprint, jsonify, current_app, request

bp = Blueprint('plugins', __name__)

@bp.route('', methods=['GET'])
def get_plugins():
    """Get all plugins"""
    try:
        plugin_manager = current_app.config['PLUGIN_MANAGER']
        all_plugins = plugin_manager.get_all_plugins()
        
        # Format response
        plugins_list = []
        for name, manifest in all_plugins.items():
            plugins_list.append({
                'name': name,
                **manifest
            })
        
        return jsonify(plugins_list), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/reload', methods=['POST'])
def reload_plugins():
    """Reload all plugins"""
    try:
        plugin_manager = current_app.config['PLUGIN_MANAGER']
        plugin_manager.reload_plugins()
        
        return jsonify({
            'message': 'Plugins reloaded successfully',
            'count': len(plugin_manager.plugins)
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/<plugin_name>', methods=['GET'])
def get_plugin(plugin_name):
    """Get specific plugin info"""
    try:
        plugin_manager = current_app.config['PLUGIN_MANAGER']
        plugin = plugin_manager.get_plugin(plugin_name)
        
        if not plugin:
            return jsonify({'error': 'Plugin not found'}), 404
        
        return jsonify(plugin.manifest()), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/<plugin_name>', methods=['DELETE'])
def delete_plugin(plugin_name):
    """Delete a plugin"""
    try:
        plugin_manager = current_app.config['PLUGIN_MANAGER']
        
        # Check if plugin exists
        if not plugin_manager.get_plugin(plugin_name):
             return jsonify({'error': 'Plugin not found'}), 404
        
        # Delete using plugin manager
        plugin_manager.delete_plugin(plugin_name)
        
        return jsonify({
            'message': f'Plugin {plugin_name} deleted successfully',
            'plugins_loaded': len(plugin_manager.plugins)
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/upload', methods=['POST'])
def upload_plugin():
    """Upload a new plugin file or library (zip)"""
    from werkzeug.utils import secure_filename
    import os
    import zipfile
    
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
        
        file = request.files['file']
        # category is now optional/ignored as plugins self-declare via manifest
        category = request.form.get('category', 'custom') 
        
        if file.filename == '':
            return jsonify({'error': 'Empty filename'}), 400
        
        filename = secure_filename(file.filename)
        plugins_root = current_app.config['PLUGINS_DIR']
        
        if filename.endswith('.zip'):
             # Handle Library Upload
             library_name = filename[:-4]
             target_dir = plugins_root / library_name
             
             # Create temp file
             temp_zip_path = plugins_root / filename
             
             print(f"[Plugin Upload] Saving ZIP to: {temp_zip_path}")
             file.save(str(temp_zip_path))
             
             try:
                 # Create target directory
                 os.makedirs(str(target_dir), exist_ok=True)
                 
                 # Unzip
                 print(f"[Plugin Upload] Extracting to: {target_dir}")
                 with zipfile.ZipFile(str(temp_zip_path), 'r') as zip_ref:
                     zip_ref.extractall(str(target_dir))
                 
                 # Clean up zip
                 os.remove(str(temp_zip_path))
                 print(f"[Plugin Upload] Cleaned up temp ZIP")
                 
                 # Reload plugins to discover new ones
                 plugin_manager = current_app.config['PLUGIN_MANAGER']
                 print(f"[Plugin Upload] Reloading plugins...")
                 plugin_manager.reload_plugins()
                 print(f"[Plugin Upload] Now have {len(plugin_manager.plugins)} plugins loaded")
                 
                 return jsonify({
                     'message': f'Library {library_name} uploaded and extracted successfully',
                     'path': str(target_dir),
                     'plugins_loaded': len(plugin_manager.plugins)
                 }), 201
                 
             except Exception as e:
                 print(f"[Plugin Upload] Error processing ZIP: {e}")
                 import traceback
                 traceback.print_exc()
                 if os.path.exists(str(temp_zip_path)):
                     os.remove(str(temp_zip_path))
                 return jsonify({'error': f'Failed to process zip: {str(e)}'}), 500

        elif filename.endswith('.py'):
            # Handle Single File Upload
            # Save to a 'custom' directory to keep things organized
            target_dir = plugins_root / 'custom'
            os.makedirs(str(target_dir), exist_ok=True)
            
            save_path = target_dir / filename
            print(f"[Plugin Upload] Saving .py file to: {save_path}")
            file.save(str(save_path))
            
            # Reload
            plugin_manager = current_app.config['PLUGIN_MANAGER']
            plugin_manager.reload_plugins()
            
            return jsonify({
                'message': 'Plugin uploaded successfully',
                'filename': filename,
                'path': str(save_path)
            }), 201
            
        else:
             return jsonify({'error': 'Only .py or .zip files are allowed'}), 400
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500
