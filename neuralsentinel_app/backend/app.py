from flask import Flask, jsonify, request
from flask_cors import CORS
import os
import sys
from pathlib import Path

# Add backend directory to path
sys.path.insert(0, str(Path(__file__).parent))

from core.plugin_system import PluginManager
from api import models, datasets, evaluations, plugins

app = Flask(__name__)
CORS(app)  # Enable CORS for Electron frontend

# Configuration
app.config['DATA_DIR'] = Path(__file__).parent.parent / 'data'
app.config['MODELS_DIR'] = app.config['DATA_DIR'] / 'models'
app.config['DATASETS_DIR'] = app.config['DATA_DIR'] / 'datasets'
app.config['EVALUATIONS_DIR'] = app.config['DATA_DIR'] / 'evaluations'
app.config['PLUGINS_DIR'] = Path(__file__).parent / 'plugins'
app.config['MAX_UPLOAD_SIZE'] = 1024 * 1024 * 1024  # 1GB

# Create data directories
for dir_path in [app.config['MODELS_DIR'], app.config['DATASETS_DIR'], app.config['EVALUATIONS_DIR']]:
    os.makedirs(dir_path, exist_ok=True)

# Initialize plugin manager
plugin_manager = PluginManager(str(app.config['PLUGINS_DIR']))
app.config['PLUGIN_MANAGER'] = plugin_manager

# Register blueprints
app.register_blueprint(models.bp, url_prefix='/api/models')
app.register_blueprint(datasets.bp, url_prefix='/api/datasets')
app.register_blueprint(evaluations.bp, url_prefix='/api/evaluations')
app.register_blueprint(plugins.bp, url_prefix='/api/plugins')

@app.route('/')
def index():
    return jsonify({
        'name': 'ML Auditor API',
        'version': '1.0.0',
        'status': 'running'
    })

@app.route('/api/health')
def health():
    return jsonify({
        'status': 'healthy',
        'plugins_loaded': len(plugin_manager.plugins),
        'data_dir': str(app.config['DATA_DIR'])
    })

@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Internal server error', 'message': str(error)}), 500

if __name__ == '__main__':
    print(f"ML Auditor Backend starting...")
    print(f"Data directory: {app.config['DATA_DIR']}")
    print(f"Plugins loaded: {len(plugin_manager.plugins)}")
    
    app.run(host='127.0.0.1', port=5000, debug=True)
