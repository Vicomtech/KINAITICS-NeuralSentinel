import os
import sys
import json
import traceback
import h5py

# Suppress TensorFlow logging and optimizations
os.environ["TF_CPP_MIN_LOG_LEVEL"] = "3"  # Suppress TensorFlow warnings
os.environ["TF_ENABLE_ONEDNN_OPTS"] = "0"  # Disable optimizations for oneDNN

# Try to import TensorFlow and Keras
try:
    import tensorflow as tf
    from tensorflow import keras
except ImportError:
    tf = None
    keras = None

# Try to import the 'tabulate' library for table formatting (optional)
try:
    from tabulate import tabulate
except ImportError:
    tabulate = None

def make_json_serializable(obj):
    """
    Recursively converts bytes to strings and other non-JSON types into JSON-compatible types.
    This function ensures that objects like NumPy arrays and byte data can be serialized into JSON.
    """
    if isinstance(obj, bytes):
        try:
            return obj.decode('utf-8')  # Decode bytes to UTF-8 string
        except Exception:
            return str(obj)  # If decoding fails, return the string representation of the object
    elif isinstance(obj, dict):
        return {make_json_serializable(k): make_json_serializable(v) for k, v in obj.items()}
    elif isinstance(obj, (list, tuple)):
        return [make_json_serializable(item) for item in obj]
    else:
        return obj  # Return the object as is if it is already JSON serializable

def explore_h5(h5obj, current_path="/"):
    """
    Recursively explores an HDF5 object (file or group) and returns a dictionary representing its structure,
    attributes, and children. It can explore datasets and groups in an HDF5 file.
    """
    info = {
        "path": current_path,
        "type": "group",
        "attrs": {},  # Store attributes of the object
        "children": {}  # Store children datasets or groups
    }
    # Process attributes of the current object
    for attr_name in h5obj.attrs:
        attr_value = h5obj.attrs[attr_name]
        if hasattr(attr_value, "tolist"):  # If the attribute is a NumPy array, convert it to list
            attr_value = attr_value.tolist()
        info["attrs"][make_json_serializable(attr_name)] = make_json_serializable(attr_value)
    
    # If the object is a group, iterate through its keys (datasets or subgroups)
    if isinstance(h5obj, h5py.Group):
        for key in h5obj.keys():
            item = h5obj[key]
            if isinstance(item, h5py.Dataset):
                # Handle datasets and capture their attributes
                ds_attrs = {}
                for a in item.attrs:
                    val = item.attrs[a]
                    if hasattr(val, "tolist"):
                        val = val.tolist()
                    ds_attrs[make_json_serializable(a)] = make_json_serializable(val)
                info["children"][make_json_serializable(key)] = {
                    "type": "dataset",
                    "shape": item.shape,
                    "dtype": make_json_serializable(repr(item.dtype)),
                    "attrs": ds_attrs,
                    "path": current_path + key
                }
            elif isinstance(item, h5py.Group):
                # Recursively explore subgroups
                info["children"][make_json_serializable(key)] = explore_h5(item, current_path + key + "/")
    return info

def flatten_structure(structure):
    """
    Recursively traverses the HDF5 structure and collects rows for each dataset with columns: 
    Path, Type, Shape, Dtype, Attributes.
    If a dataset has no attributes, a dash ("–") is used.
    Returns a list of rows that represent datasets in the HDF5 structure.
    """
    rows = []
    def _traverse(node):
        if node.get("type") == "dataset":
            # Collect attributes and create a row for the dataset
            attrs_keys = ", ".join(node.get("attrs", {}).keys())
            if not attrs_keys:
                attrs_keys = "–"  # If no attributes, use a dash
            row = [
                node.get("path", ""),
                node.get("type", ""),
                str(node.get("shape", "")),
                node.get("dtype", ""),
                attrs_keys
            ]
            rows.append(row)
        for child in node.get("children", {}).values():
            _traverse(child)
    _traverse(structure)
    return rows

def filter_empty_columns(headers, rows):
    """
    Checks each column to see if all rows are empty or a dash ("–").
    Filters out columns that contain only empty values or dashes across all rows.
    Returns the filtered headers and rows.
    """
    keep_cols = []
    for i in range(len(headers)):
        if any(row[i].strip() not in ("", "–") for row in rows):  # Keep column if it has non-empty values
            keep_cols.append(i)
    filtered_headers = [headers[i] for i in keep_cols]
    filtered_rows = [[row[i] for i in keep_cols] for row in rows]
    return filtered_headers, filtered_rows

def table_to_string(rows):
    """
    Converts a list of rows into a formatted table string.
    Uses the 'tabulate' library for better formatting if available.
    Otherwise, falls back to a simple text format.
    Also removes columns that are empty for all rows.
    """
    headers = ["Path", "Type", "Shape", "Dtype", "Attributes"]
    filtered_headers, filtered_rows = filter_empty_columns(headers, rows)
    if tabulate:
        # Use tabulate for better formatting
        return tabulate(filtered_rows, headers=filtered_headers, tablefmt="grid")
    else:
        # Fallback to simple text format
        header_line = " | ".join(filtered_headers)
        separator = "-" * len(header_line)
        lines = [header_line, separator]
        for row in filtered_rows:
            lines.append(" | ".join(row))
        return "\n".join(lines)

def try_keras_summary(model_path):
    """
    Attempts to load a Keras model from the given path and return its summary as text.
    Returns (summary, None) if successful or (None, error_message) on failure.
    """
    if not keras:
        return None, "TensorFlow not available."
    try:
        model = keras.models.load_model(model_path, compile=False)
        from io import StringIO
        buffer = StringIO()
        model.summary(print_fn=lambda x: buffer.write(x + "\n"))
        return buffer.getvalue(), None
    except Exception as e:
        return None, str(e)

def try_h5_inspect(model_path):
    """
    Uses h5py to inspect the HDF5 file structure and returns a representation of it.
    Returns (structure, None) if successful or (None, error_message) on failure.
    """
    try:
        with h5py.File(model_path, 'r') as f:
            structure = explore_h5(f, "/")
        return structure, None
    except Exception as e:
        return None, str(e)

def main():
    """
    The main function that processes the model file and attempts to generate a summary or structure.
    It tries to get the Keras summary first, then falls back to inspecting the HDF5 structure.
    """
    if len(sys.argv) < 2:
        print(json.dumps({"error": "No model path provided"}))
        sys.exit(1)

    file_path = sys.argv[1]
    if not os.path.exists(file_path):
        print(json.dumps({"error": f"File not found: {file_path}"}))
        sys.exit(1)

    # First, attempt to get the summary using Keras
    summary, keras_err = try_keras_summary(file_path)
    if summary is not None:
        output = {"summary": summary}
        # Always output valid JSON
        print(json.dumps(output, indent=2))
        sys.exit(0)

    # If Keras summary fails, use HDF5 inspection
    structure, h5_err = try_h5_inspect(file_path)
    if structure is not None:
        rows = flatten_structure(structure)
        table_str = table_to_string(rows)
        # Output valid JSON with the formatted table as a string
        output = {"summary": table_str}
        print(json.dumps(output, indent=2))
        sys.exit(0)

    # If both methods fail, output a combined error as JSON
    combined_error = f"Keras load failed: {keras_err}\nH5 inspection failed: {h5_err}"
    print(json.dumps({"error": combined_error}))
    sys.exit(1)

if __name__ == "__main__":
    main()