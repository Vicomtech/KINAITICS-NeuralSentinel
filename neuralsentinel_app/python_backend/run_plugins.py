import warnings
warnings.filterwarnings('ignore', category=FutureWarning)
warnings.filterwarnings("ignore", module="tensorflow")
warnings.filterwarnings("ignore", module="foolbox")
import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'
import sys
import json
import argparse
import yaml

# Adding the required directories to the Python path for module discovery
base_dir   = os.path.dirname(os.path.abspath(__file__))  # Path to the python_backend directory
parent_dir = os.path.dirname(base_dir)                   # Parent directory
core_dir   = os.path.join(base_dir, "core")              # Path to the core directory
plugins_dir= os.path.join(base_dir, "plugins")           # Path to the plugins directory

# Ensure that the necessary paths are in sys.path for importing modules
for p in (parent_dir, base_dir, core_dir):
    if p not in sys.path:
        sys.path.insert(0, p)

from plugin_manager import discover_plugins

def simple_logger(*args, **kwargs):
    # A simple logger that prints to stderr
    print(*args, file=sys.stderr, **kwargs)

def load_config(path):
    # Loads configuration from the YAML file if it exists
    if not os.path.exists(path):
        return {}
    with open(path, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f) or {}

def filter_plugins_by_config(modules, cfg_list):
    """
    Filters the plugins based on the provided configuration list.
    If no configuration is provided, it returns all modules.
    """
    if not cfg_list:
        return modules
    
    enabled = []
    for mod in modules:
        Ev = getattr(mod, "Evaluator", None)
        if not Ev: continue
        name = Ev(simple_logger).meta.get("name", mod.__name__)
        conf = next((p for p in cfg_list if p["name"] == name), {})
        if conf.get("enabled", False):
            enabled.append(mod)
    return enabled

def evaluate_plugins(plugin_modules, input_data, plugin_cfg_list):
    """
    Executes only the allowed functions for each plugin and flattens the results
    if the plugin has only one function.
    """
    aggregated = {}
    for mod in plugin_modules:
        Ev = getattr(mod, "Evaluator", None)
        if not Ev:
            continue

        inst = Ev(simple_logger)
        meta = getattr(inst, "meta", {})
        name = meta.get("name", mod.__name__)
        conf = next((p for p in plugin_cfg_list if p["name"] == name), {})
        allowed = conf.get("functions", [])
        funcs   = meta.get("functions", {})

        plugin_data = {}
        # Iterate ONLY over the allowed functions
        for fn in allowed:
            f = funcs.get(fn)
            if not f:
                simple_logger(f"[WARN] Function {fn} not found in {name}")
                continue
            try:
                res = f(input_data)
            except Exception as e:
                simple_logger(f"[ERROR] {name}.{fn}: {e}")
                res = {"error": str(e)}

            # If only ONE function, do not nest the result under its name
            if len(allowed) == 1:
                plugin_data = res or {}
            else:
                plugin_data[fn] = res or {}

        if plugin_data:
            aggregated[name] = plugin_data

    return aggregated

def main():
    print("[DEBUG] >>> run_plugins.py started", file=sys.stderr)

    # Command-line argument parsing
    parser = argparse.ArgumentParser()
    parser.add_argument('--model', help="Path to the model file")
    parser.add_argument('--dataset', help="Path to the dataset file")
    parser.add_argument('--use-dummy', action='store_true')
    parser.add_argument('--label-column')
    parser.add_argument('--protected-column')
    args = parser.parse_args()

    # Prepare the input_data for all plugins
    if args.model:
        input_data = {
            "file_path": args.model,
            "file_type": "model",
            "dataset_path": None if args.use_dummy else args.dataset,
            "label_column": args.label_column,
            "protected_column": args.protected_column
        }
        if not args.use_dummy and not args.dataset:
            print("Error: --use-dummy or --dataset is required if --model is provided", file=sys.stderr)
            sys.exit(1)
    else:
        print("Error: Invalid arguments", file=sys.stderr)
        sys.exit(1)

    # Load the configuration YAML file
    cfg_path = os.path.join(base_dir, "plugin_config.yaml")
    cfg      = load_config(cfg_path).get("plugins", [])

    # Discover and filter plugins based on the configuration
    mods = discover_plugins(plugins_dir)
    mods = filter_plugins_by_config(mods, cfg)

    # Evaluate the plugins with the input data
    results = evaluate_plugins(mods, input_data, cfg)

    # Output the results as JSON
    print(json.dumps(results))

if __name__ == "__main__":
    main()
