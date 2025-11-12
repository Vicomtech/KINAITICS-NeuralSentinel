import os, warnings, logging
os.environ["TF_CPP_MIN_LOG_LEVEL"] = "3"
warnings.filterwarnings("ignore", category=FutureWarning)
warnings.filterwarnings("ignore", module="tensorflow")
warnings.filterwarnings("ignore", module="foolbox")
import numpy as np
import tensorflow as tf
tf.get_logger().setLevel(logging.ERROR)
logging.getLogger("tensorflow").setLevel(logging.ERROR)
from neuralstrength_lite.metrics._metrics import FGSM, PGD, BIM
from core.interfaces import BaseEvaluator

# --------------------Neuralstrength Lite Evaluator--------------------
class Evaluator(BaseEvaluator):
    """
    Evaluator to assess robustness using FGSM, PGD, and BIM.
    - Automatically normalizes tabular data (1D) to [0, 1].
    - Samples up to max_samples examples of X/Y.
    - Initializes FGSM, PGD, and BIM engines.
    - For 1D inputs, filters to keep only 'accuracy'.
    - Limits impact to input_0 to avoid large JSON.
    """
    def __init__(self, logger):
        self.logger = logger
        self.meta = {
            "name": "neuralstrength_lite_evaluator",
            "functions": {"evaluate_robustness": self.evaluate_robustness}
        }
        self.model = None
        self.engines = []
        self.bounds = (0,1)
        self.max_samples = 32

    def evaluate(self, input_data):
        """
        Wrapper for the evaluate_robustness function.
        """
        return self.evaluate_robustness(input_data)

    def build(self, model, bounds=(0,1)):
        """
        Builds and wraps the model for evaluation. Initializes attack engines (FGSM, PGD, BIM).
        """
        #self.logger(f"[DEBUG] Building model, bounds={bounds}")
        dummy = np.random.rand(1, *model.input_shape[1:]).astype(np.float32)
        _ = model(dummy)
        fm = tf.keras.Model(model.inputs[0], model(model.inputs[0]))
        if len(fm.layers) == 2 and fm.layers[1].__class__.__name__ == "Sequential":
            fm = fm.layers[1]
        self.model = fm
        self.bounds = bounds

        # Initialize attack engines (FGSM, PGD, BIM)
        self.engines = []
        vectorial = (len(self.model.input_shape[1:]) == 1)
        for Engine in (FGSM, PGD, BIM):
            try:
                eng = Engine(k=10)
                eng.build(self.model, bounds=bounds)

                # Filter only 'accuracy' in 1D input
                if vectorial:
                    names, mets = [], []
                    for n, m in zip(eng.metric_names, eng.metrics):
                        if n == "accuracy":
                            names.append(n)
                            mets.append(m)
                    eng.metric_names = names
                    eng.metrics = mets

                self.engines.append(eng)
                #self.logger(f"[DEBUG] Initialized {Engine.__name__}")
            except Exception as e:
                self.logger(f"[WARN] init {Engine.__name__} failed: {e}")

    def evaluate_robustness(self, input_data=None):
        """
        Evaluates robustness by running adversarial attacks and calculating metrics.
        """
        # 1) Determine the model path
        mpath = (
            input_data.get("modelFile")
            or input_data.get("model")
            or (input_data.get("file_path") if input_data.get("file_type") == "model" else None)
        )

        # 2) If the model is the dummy placeholder, short-circuit to empty
        if mpath and os.path.basename(mpath) == "__DUMMY__":
            return {}

        # 3) Load the model if not already loaded
        if not self.model:
            if not mpath:
                return {"error": "Missing model path"}
            #self.logger(f"[DEBUG] Loading model {mpath}")
            km = tf.keras.models.load_model(mpath)
            self.build(km, bounds=self.bounds)

        # 4) Load dataset or use dummy data
        use_dummy = input_data.get("use_dummy", False)
        dpath = (
            input_data.get("datasetFile")
            or input_data.get("dataset")
            or (
                input_data.get("dataset_path")
                or (
                    input_data.get("file_path")
                    if input_data.get("file_type") == "dataset"
                    else None
                )
            )
        )
        if not use_dummy and dpath:
            self.logger(f"[DEBUG] Loading dataset {dpath}")
            data = np.load(dpath, allow_pickle=True)

            # .npz case
            if hasattr(data, "files"):
                files = data.files
                if "x" in files and "y" in files:
                    X, Y = data["x"], data["y"]
                elif len(files) >= 2:
                    X, Y = data[files[0]], data[files[1]]
                else:
                    return {"error": f".npz needs ≥2 arrays, got {files}"}

            # .npy dict case
            elif isinstance(data, np.ndarray) and data.dtype == object:
                obj = data.item()
                if isinstance(obj, dict) and "x" in obj and "y" in obj:
                    X, Y = obj["x"], obj["y"]
                else:
                    return {"error": ".npy needs a dict with keys 'x' and 'y'"}

            # .npy array case → infer Y
            elif isinstance(data, np.ndarray):
                X = data.astype(np.float32)
                preds = self.model.predict(X)
                cls = np.argmax(preds, axis=1)
                ncls = preds.shape[1] if preds.ndim > 1 else 1
                Y = np.eye(ncls, dtype=np.float32)[cls]

            else:
                return {"error": "Unsupported numpy format"}

            X = X.astype(np.float32)
            Y = Y.astype(np.float32)

            # Normalize 1D tabular
            if len(self.model.input_shape[1:]) == 1:
                mins = X.min(axis=0, keepdims=True)
                maxs = X.max(axis=0, keepdims=True)
                denom = (maxs - mins)
                denom[denom == 0] = 1.0
                X = ((X - mins) / denom).astype(np.float32)

        else:
            self.logger("[WARN] Using dummy data")
            shape = self.model.input_shape[1:]
            X = np.random.rand(1, *shape).astype(np.float32)
            out = self.model.output_shape
            out = out[0] if isinstance(out, list) else out
            ncls = out[-1]
            Y = np.zeros((1, ncls), dtype=np.float32)
            Y[0, 0] = 1.0

        # 5) Subsample
        N = min(self.max_samples, X.shape[0])
        if X.shape[0] > 1:
            X, Y = X[:N], Y[:N]

        # 6) Run each engine
        results = {}
        for eng in self.engines:
            key = eng.__class__.__name__.lower()
            try:
                # self.logger(f"[DEBUG] Running {eng.__class__.__name__}")
                try:
                    raw = eng(X, Y)
                except TypeError:
                    raw = eng(X, Y, epsilons=None)

                # Extract metrics
                m = raw.get("metrics") if isinstance(raw, dict) and "metrics" in raw else {
                    k: v for k, v in raw.items() if k != "impact"
                }
                def clean(v):
                    if isinstance(v, np.generic): return v.item()
                    if isinstance(v, np.ndarray): return v.tolist()
                    return v
                m = {k: clean(v) for k, v in (m or {}).items()}

                # Truncate impact
                imp = raw.get("impact") or {}
                if isinstance(imp, dict):
                    keys = [k for k in imp if k.startswith("input_")]
                    imp = {keys[0]: imp[keys[0]]} if keys else {}

                results[key] = {"metrics": m, "impact": imp}
            except Exception as e:
                self.logger(f"[ERROR] {key} failed: {e}")
                results[key] = {"error": str(e)}

        return results