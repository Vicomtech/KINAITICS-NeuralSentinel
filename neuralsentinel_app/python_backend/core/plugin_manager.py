import importlib
import os
import sys
import yaml
from pathlib import Path

from interfaces import BaseEvaluator, BaseVisualizer

class PluginManager:
    def __init__(self, logger):
        self.logger = logger
        self.plugins = {}

    def load_plugins(self, plugins_dir: str):
        plugins_path = Path(plugins_dir)
        for plugin_dir in plugins_path.iterdir():
            if not plugin_dir.is_dir() or plugin_dir.name == 'plugin_base':
                continue
            try:
                config = self._load_config(plugin_dir)
                module = self._import_plugin(plugin_dir, config)
                evaluator = module.Evaluator(self.logger)
                visualizer = module.Visualizer() if hasattr(module, 'Visualizer') else None
                self.plugins[config['name']] = {
                    'evaluator': evaluator,
                    'visualizer': visualizer,
                    'config': config
                }
            except Exception as e:
                self.logger(f"Error loading plugin {plugin_dir.name}: {str(e)}")

    def _load_config(self, plugin_dir: Path) -> dict:
        config_file = plugin_dir / 'plugin.yaml'
        with open(config_file, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)

    def _import_plugin(self, plugin_dir: Path, config: dict):
        module_path = f"python_backend.plugins.{plugin_dir.name}"
        return importlib.import_module(module_path)

import os
import sys
import importlib.util

def discover_plugins(plugins_dir):
    """
    Scans python_backend/plugins/*, looks for evaluator.py in each subfolder,
    and dynamically imports it to return the list of modules.
    """
    plugin_modules = []
    for entry in os.scandir(plugins_dir):
        if not entry.is_dir() or entry.name.startswith('__'):
            continue

        evaluator_path = os.path.join(entry.path, 'evaluator.py')
        if not os.path.exists(evaluator_path):
            # no evaluator.py, skip
            continue

        # We create a spec and load the module from the evaluator.py file
        spec = importlib.util.spec_from_file_location(
            f"{entry.name}.evaluator",
            evaluator_path
        )
        module = importlib.util.module_from_spec(spec)
        try:
            spec.loader.exec_module(module)
            plugin_modules.append(module)
        except Exception as e:
            # If a plugin fails, we report it via stderr and continue
            print(f"Error loading plugin {entry.name}: {e}", file=sys.stderr)

    return plugin_modules


__all__ = ["PluginManager", "discover_plugins"]
