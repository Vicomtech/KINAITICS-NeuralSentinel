from flask import Blueprint, jsonify, current_app, request

bp = Blueprint('plugins', __name__)


def _install_pack_dependencies(target_dir):
    """Install private dependencies bundled inside an uploaded plugin pack.

    If the extracted pack contains a ``requirements.txt`` and/or one or more
    ``.whl`` files (e.g. a private ``neuralstrength`` wheel), install them into
    the *current* Python environment so the pack's plugins can import them.

    Installation runs with ``--no-deps`` on purpose: the backend process is
    already running, and on Windows pip cannot replace/downgrade packages that
    the live interpreter has imported (it fails with OSError while renaming
    locked ``.pyc``/dist-info files). The pack therefore only adds the private
    wheel itself; all third-party dependencies of the premium metrics must be
    provisioned in the base environment (backend/requirements.txt), which is
    installed once while the backend is stopped.

    ``--find-links <pack_dir>`` lets a bundled requirements.txt resolve the
    private wheel offline from inside the pack.

    Returns a summary dict, or None if there was nothing to install.
    """
    import subprocess
    import sys
    from pathlib import Path

    target_dir = Path(target_dir)
    req_file = target_dir / 'requirements.txt'
    wheels = sorted(target_dir.rglob('*.whl'))

    if not req_file.exists() and not wheels:
        return None

    cmd = [sys.executable, '-m', 'pip', 'install', '--no-deps',
           '--find-links', str(target_dir)]
    if req_file.exists():
        cmd += ['-r', str(req_file)]
    else:
        cmd += [str(w) for w in wheels]

    print(f"[Plugin Upload] Installing pack dependencies: {' '.join(cmd)}")
    result = subprocess.run(cmd, capture_output=True, text=True)

    summary = {
        'returncode': result.returncode,
        'requirements': req_file.name if req_file.exists() else None,
        'wheels': [w.name for w in wheels],
        # Keep only the tail so the HTTP response stays small.
        'stdout_tail': result.stdout[-2000:],
        'stderr_tail': result.stderr[-2000:],
    }
    if result.returncode != 0:
        print(f"[Plugin Upload] pip install FAILED (code {result.returncode}):\n{result.stderr[-2000:]}")
    else:
        print("[Plugin Upload] pip install OK")
    return summary

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

                 # Install any private dependencies bundled in the pack
                 # (requirements.txt / *.whl) BEFORE discovering the plugins,
                 # so imports like `neuralstrength` resolve during reload.
                 install_summary = _install_pack_dependencies(target_dir)
                 if install_summary and install_summary['returncode'] != 0:
                     return jsonify({
                         'error': 'Pack extracted but dependency installation failed. '
                                  'The plugins were not loaded.',
                         'path': str(target_dir),
                         'install': install_summary,
                     }), 500

                 # Reload plugins to discover new ones
                 plugin_manager = current_app.config['PLUGIN_MANAGER']
                 print(f"[Plugin Upload] Reloading plugins...")
                 plugin_manager.reload_plugins()
                 print(f"[Plugin Upload] Now have {len(plugin_manager.plugins)} plugins loaded")

                 return jsonify({
                     'message': f'Library {library_name} uploaded and extracted successfully',
                     'path': str(target_dir),
                     'plugins_loaded': len(plugin_manager.plugins),
                     'install': install_summary,
                 }), 201
                 
             except Exception as e:
                 print(f"[Plugin Upload] Error processing ZIP: {e}")
                 import traceback
                 traceback.print_exc()
                 if os.path.exists(str(temp_zip_path)):
                     os.remove(str(temp_zip_path))
                 return jsonify({'error': f'Failed to process zip: {str(e)}'}), 500

        elif filename.endswith('.whl'):
            # Standalone wheel upload: install a private library (e.g. neuralstrength)
            # into the backend venv without shipping any plugin files.
            import subprocess
            import sys
            target_dir = plugins_root / '_wheels'
            os.makedirs(str(target_dir), exist_ok=True)
            save_path = target_dir / filename
            file.save(str(save_path))

            print(f"[Plugin Upload] Installing wheel: {save_path}")
            result = subprocess.run(
                [sys.executable, '-m', 'pip', 'install', '--no-deps', str(save_path)],
                capture_output=True, text=True
            )
            if result.returncode != 0:
                print(f"[Plugin Upload] Wheel install FAILED:\n{result.stderr[-2000:]}")
                return jsonify({
                    'error': 'Wheel installation failed.',
                    'stderr_tail': result.stderr[-2000:],
                }), 500

            # Reload so plugins that depend on the new library can now load.
            plugin_manager = current_app.config['PLUGIN_MANAGER']
            plugin_manager.reload_plugins()

            return jsonify({
                'message': f'Wheel {filename} installed successfully',
                'plugins_loaded': len(plugin_manager.plugins),
                'stdout_tail': result.stdout[-2000:],
            }), 201

        elif filename.endswith('.py') or filename.endswith('.so') or filename.endswith('.pyd'):
            # Handle Single File Upload (.py script, .so/.pyd compiled plugin)
            # Save to a 'custom' directory to keep things organized
            target_dir = plugins_root / 'custom'
            os.makedirs(str(target_dir), exist_ok=True)
            
            save_path = target_dir / filename
            ext = os.path.splitext(filename)[1]
            print(f"[Plugin Upload] Saving {ext} file to: {save_path}")
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
             return jsonify({'error': 'Only .py, .so, .pyd, .whl or .zip files are allowed'}), 400
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500
