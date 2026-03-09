import importlib.util
import inspect
import os
from pathlib import Path
from typing import Dict, List
from plugins.base import MetricPlugin

class PluginManager:
    """Manages discovery, loading, and validation of metric plugins"""
    
    def __init__(self, plugins_dir: str):
        self.plugins_dir = Path(plugins_dir)
        self.plugins: Dict[str, MetricPlugin] = {}
        self.plugin_paths: Dict[str, Path] = {}  # Track file paths
        self.plugins_by_type: Dict[str, List[str]] = {
            'security': [],
            'privacy': [],
            'fairness': []
        }
        
        self.discover_plugins()
    
    def discover_plugins(self):
        """Scan plugins directory recursively and load all valid plugins"""
        if not self.plugins_dir.exists():
            print(f"Plugins directory not found: {self.plugins_dir}")
            return
        
        # Helper to ignore some directories
        def is_ignored(path: Path) -> bool:
            return any(part.startswith('.') or part == '__pycache__' or part == 'venv' for part in path.parts)

        # Recursively find all python files
        for file_path in self.plugins_dir.rglob('*.py'):
            if is_ignored(file_path):
                continue
            
            if file_path.name == '__init__.py':
                continue

            try:
                # We pass 'unknown' initially, the actual category is determined by the plugin manifest
                self.load_plugin(file_path)
            except Exception as e:
                print(f"[Plugin Discovery] Skipping {file_path.name}: {type(e).__name__}: {e}")

    def load_plugin(self, file_path: Path, category: str = None):
        """Load a single plugin from file"""
        # Create unique module name based on relative path to ensure no conflicts
        try:
            rel_path = file_path.relative_to(self.plugins_dir)
            module_name = str(rel_path).replace(os.sep, '_').replace('.py', '')
        except ValueError:
            module_name = file_path.stem

        # Import module
        spec = importlib.util.spec_from_file_location(module_name, file_path)
        if spec is None or spec.loader is None:
             print(f"Could not load spec for {file_path}")
             return

        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        
        # Find MetricPlugin subclasses
        for name, obj in inspect.getmembers(module, inspect.isclass):
            if issubclass(obj, MetricPlugin) and obj is not MetricPlugin:
                try:
                    # Instantiate plugin
                    plugin_instance = obj()
                    
                    # Validate manifest
                    manifest = plugin_instance.manifest()
                    self.validate_manifest(manifest)
                    
                    # Register plugin using category from manifest
                    plugin_name = manifest['name']
                    plugin_type = manifest['type']

                    self.plugins[plugin_name] = plugin_instance
                    self.plugin_paths[plugin_name] = file_path # Store path
                    
                    if plugin_type not in self.plugins_by_type:
                         self.plugins_by_type[plugin_type] = []
                         
                    if plugin_name not in self.plugins_by_type[plugin_type]:
                        self.plugins_by_type[plugin_type].append(plugin_name)
                    
                    # Store library name if applicable
                    try:
                        rel_path = file_path.relative_to(self.plugins_dir)
                        parts = rel_path.parts
                        if len(parts) > 1 and parts[0] != 'custom':
                             # Store private attribute for internal use
                             plugin_instance._library = parts[0]
                    except Exception:
                        pass
                    
                    print(f"Loaded plugin: {plugin_name} ({plugin_type}) from {file_path.name}")
                    
                except Exception as e:
                    print(f"Error instantiating plugin {name} from {file_path.name}: {e}")

    def delete_plugin(self, plugin_name: str):
        """Delete a plugin and its source file"""
        if plugin_name not in self.plugins:
            raise ValueError(f"Plugin {plugin_name} not found")
            
        file_path = self.plugin_paths.get(plugin_name)
        if not file_path or not file_path.exists():
            raise FileNotFoundError(f"Source file for {plugin_name} not found")
            
        # Remove file
        try:
            os.remove(file_path)
            print(f"Deleted plugin file: {file_path}")
            
            # Try to remove parent directory if empty (for libraries)
            parent_dir = file_path.parent
            if parent_dir != self.plugins_dir:
                 try:
                     # Check if empty (ignoring __pycache__)
                     has_files = False
                     for item in parent_dir.iterdir():
                         if item.name != '__pycache__' and not item.name.startswith('.'):
                             has_files = True
                             break
                     
                     if not has_files:
                         import shutil
                         shutil.rmtree(parent_dir) # Remove directory including pycache
                         print(f"Deleted empty library directory: {parent_dir}")
                         
                         # Check grandparent too (e.g. plugins/mylib/security/ -> plugins/mylib/)
                         grandparent = parent_dir.parent
                         if grandparent != self.plugins_dir:
                             has_files_gp = False
                             for item in grandparent.iterdir():
                                 if item.name != '__pycache__' and not item.name.startswith('.'):
                                     has_files_gp = True
                                     break
                             if not has_files_gp:
                                 shutil.rmtree(grandparent)
                                 print(f"Deleted empty library root: {grandparent}")

                 except Exception as e:
                     print(f"Could not clean up directories: {e}")

        except Exception as e:
            raise OSError(f"Failed to delete file: {e}")

        # Reload plugins to update state
        self.reload_plugins()

    # ... rest of methods ...
    
    def validate_manifest(self, manifest: dict):
        """Validate plugin manifest has required fields"""
        required_fields = ['name', 'type', 'version', 'description', 'parameters']
        
        for field in required_fields:
            if field not in manifest:
                raise ValueError(f"Missing required field: {field}")
        
        if manifest['type'] not in ['security', 'privacy', 'fairness']:
            raise ValueError(f"Invalid plugin type: {manifest['type']}")
    
    def get_plugin(self, name: str) -> MetricPlugin:
        """Get plugin by name"""
        return self.plugins.get(name)
    
    def get_plugins_by_type(self, plugin_type: str) -> List[str]:
        """Get all plugin names for a specific type"""
        return self.plugins_by_type.get(plugin_type, [])
    



    
    def get_all_plugins(self) -> Dict[str, dict]:
        """Get all plugins with their manifests"""
        plugins_data = {}
        for name, plugin in self.plugins.items():
            manifest = plugin.manifest()
            # Inject library info if present
            if hasattr(plugin, '_library'):
                manifest['library'] = plugin._library
            plugins_data[name] = manifest
        return plugins_data
    
    def reload_plugins(self):
        """Reload all plugins"""
        self.plugins.clear()
        for type_list in self.plugins_by_type.values():
            type_list.clear()
        
        self.discover_plugins()
