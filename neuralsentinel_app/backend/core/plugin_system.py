import importlib.util
import importlib.machinery
import inspect
import os
import re
import sys
import subprocess
from pathlib import Path
from typing import Dict, List, Set
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
        # Requirement files already installed during this process run, so we
        # don't shell out to pip again on every reload.
        self._installed_requirements: Set[str] = set()

        self.discover_plugins()
    
    def _is_compiled_extension(self, file_path: Path) -> bool:
        """Check if a file is a compiled Python extension (.so or .pyd)"""
        name = file_path.name
        return name.endswith('.pyd') or (name.endswith('.so') and name != '__init__.so')
    
    def _get_module_name(self, file_path: Path) -> str:
        """Extract the correct module name for importlib.
        
        For .py files: use the path-based name for uniqueness.
        For compiled extensions (.so/.pyd): use just the base module name 
        (before the platform suffix) because compiled modules export 
        PyInit_<name> and the module name must match exactly.
        """
        if self._is_compiled_extension(file_path):
            # Compiled extension: extract base module name
            # e.g. "basic_iterative_method.cp311-win_amd64.pyd" -> "basic_iterative_method"
            # e.g. "basic_iterative_method.cpython-311-x86_64-linux-gnu.so" -> "basic_iterative_method"
            name = file_path.name
            # The module name is everything before the first '.' if there are platform tags,
            # or before the extension if it's just "name.pyd" / "name.so"
            base_name = name.split('.')[0]
            return base_name
        else:
            # .py file: use path-based name for uniqueness
            try:
                rel_path = file_path.relative_to(self.plugins_dir)
                module_name = str(rel_path).replace(os.sep, '_').replace('.py', '')
            except ValueError:
                module_name = file_path.stem
            return module_name
    
    def discover_plugins(self):
        """Scan plugins directory recursively and load all valid plugins"""
        if not self.plugins_dir.exists():
            print(f"Plugins directory not found: {self.plugins_dir}")
            return

        # Install any dependencies declared by plugin packs before importing
        # the compiled metrics, so imports like cv2/seaborn succeed instead of
        # the plugin being skipped.
        self._install_pack_requirements()

        # Helper to ignore some directories
        def is_ignored(path: Path) -> bool:
            return any(part.startswith('.') or part == '__pycache__' or part == 'venv' for part in path.parts)

        # Recursively find all python files (.py) and compiled extensions (.so, .pyd)
        plugin_extensions = ['*.py', '*.so', '*.pyd']
        for ext_pattern in plugin_extensions:
            for file_path in self.plugins_dir.rglob(ext_pattern):
                if is_ignored(file_path):
                    continue
                
                if file_path.name == '__init__.py':
                    continue

                try:
                    self.load_plugin(file_path)
                except Exception as e:
                    print(f"[Plugin Discovery] Skipping {file_path.name}: {type(e).__name__}: {e}")

    def _install_pack_requirements(self):
        """Install dependencies declared by plugin packs before loading them.

        Each plugin pack may ship a ``requirements.txt`` next to its compiled
        metrics (and optionally a private ``.whl``). Before importing the
        plugins we install those requirements into the running interpreter so
        imports such as ``cv2``/``seaborn`` succeed instead of the plugin being
        skipped.

        The full dependency tree is resolved (no ``--no-deps``) so transitive
        deps the compiled metrics need at import time -- e.g. ``numba`` /
        ``llvmlite`` / ``pynndescent`` pulled in by ``umap-learn`` -- are
        installed too. ``--find-links <pack_dir>`` resolves a bundled private
        wheel offline. A ``.deps_installed`` marker is written on success so an
        unchanged pack is not reinstalled on every reload/restart.

        Caveat (Windows): if pip must replace a base package the live backend
        has already imported (e.g. numpy/scipy) to satisfy a pin, the install
        can fail with locked-file errors. Reload right after a fresh backend
        start, or with the backend stopped, to avoid that.
        """
        def is_ignored(path: Path) -> bool:
            return any(part.startswith('.') or part == '__pycache__' or part == 'venv' for part in path.parts)

        for req_file in self.plugins_dir.rglob('requirements.txt'):
            if is_ignored(req_file):
                continue

            pack_dir = req_file.parent
            resolved = str(req_file.resolve())

            # Already handled in this process run.
            if resolved in self._installed_requirements:
                continue

            # Skip if a previous successful install is still up to date.
            marker = pack_dir / '.deps_installed'
            try:
                if marker.exists() and marker.stat().st_mtime >= req_file.stat().st_mtime:
                    self._installed_requirements.add(resolved)
                    continue
            except OSError:
                pass

            cmd = [sys.executable, '-m', 'pip', 'install',
                   '--find-links', str(pack_dir), '-r', str(req_file)]
            print(f"[Plugin Deps] Installing requirements for pack '{pack_dir.name}': {' '.join(cmd)}")
            try:
                result = subprocess.run(cmd, capture_output=True, text=True)
            except Exception as e:
                print(f"[Plugin Deps] Failed to launch pip for {pack_dir}: {e}")
                continue

            if result.returncode == 0:
                print(f"[Plugin Deps] Requirements installed for pack '{pack_dir.name}'")
                self._installed_requirements.add(resolved)
                try:
                    marker.write_text('ok', encoding='utf-8')
                except OSError as e:
                    print(f"[Plugin Deps] Could not write marker {marker}: {e}")
            else:
                print(f"[Plugin Deps] pip install FAILED for pack '{pack_dir.name}' "
                      f"(code {result.returncode}):\n{result.stderr[-2000:]}")

    def load_plugin(self, file_path: Path, category: str = None):
        """Load a single plugin from file (.py, .so or .pyd)"""
        module_name = self._get_module_name(file_path)

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
