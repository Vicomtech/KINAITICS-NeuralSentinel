import os
import numpy as np
import pandas as pd
import tensorflow as tf
from core.interfaces import BaseEvaluator
from art.attacks.evasion import FastGradientMethod, ProjectedGradientDescent
from art.estimators.classification import TensorFlowV2Classifier

# --------------------ART Robustness Evaluator--------------------
class Evaluator(BaseEvaluator):
    """
    Evaluator for ART Robustness using FGSM and PGD attacks,
    including perturbation norms (L0, L2, L∞), cross-entropy loss,
    and margin (true vs runner-up).
    """

    def __init__(self, logger):
        self.logger     = logger
        self.meta       = {
            "name": "art_robustness_evaluator",
            "functions": {"evaluate_robustness": self.evaluate_robustness}
        }
        self.classifier = None

    def evaluate(self, input_data):
        """
        Wrapper for evaluate_robustness function.
        """
        return self.evaluate_robustness(input_data)

    def evaluate_robustness(self, input_data=None):
        """
        Evaluate robustness using ART attacks (FGSM and PGD).
        Args:
            input_data (dict): Contains the model path, dataset path, and other necessary parameters.
        Returns:
            dict: Evaluation results with robustness metrics for clean and adversarial examples.
        """
        try:
            # 1) Load the model and wrap it for ART compatibility
            model_path   = input_data.get("file_path")
            dataset_path = input_data.get("dataset_path")
            if not model_path:
                return {"error": "Missing model file_path"}
            if not dataset_path:
                return {"error": "Missing dataset_path"}

            if self.classifier is None:
                self.logger(f"Loading model from {model_path}")
                model = tf.keras.models.load_model(model_path)
                # If model output is not binary, modify it for binary output
                if model.output_shape[-1] < 2:
                    inp = model.input
                    pr  = tf.keras.activations.sigmoid(model(inp))
                    inv = 1.0 - pr
                    out2= tf.keras.layers.Concatenate(axis=-1)([pr, inv])
                    model = tf.keras.Model(inputs=inp, outputs=out2)
                loss = tf.keras.losses.CategoricalCrossentropy()
                self.classifier = TensorFlowV2Classifier(
                    model=model,
                    nb_classes=model.output_shape[-1],
                    input_shape=model.input_shape[1:],
                    loss_object=loss,
                    clip_values=(0.0, 1.0)
                )

            if dataset_path.lower().endswith(".npz"):
                arr = np.load(dataset_path, allow_pickle=True)
                if hasattr(arr, "files"):
                    X = arr.get("x", arr.get("X"))
                    if X is None:
                        return {"error": "NPZ must contain an 'x' or 'X' array"}
                else:
                    return {"error": f"Unsupported NPZ structure: {list(arr.files)}"}
                X = X.astype(np.float32)

            elif dataset_path.lower().endswith(".npy"):
                arr = np.load(dataset_path, allow_pickle=True)
                # handle pickled dict case
                if isinstance(arr, np.ndarray) and arr.dtype == object:
                    obj = arr.item()
                    if isinstance(obj, dict) and "x" in obj:
                        X = obj["x"].astype(np.float32)
                    else:
                        return {"error": "NPY must be a dict with key 'x'"}
                else:
                    # raw numeric array
                    X = arr.astype(np.float32)

            elif dataset_path.lower().endswith(".csv"):
                df = pd.read_csv(dataset_path)
                if 'label' in df.columns:
                    df = df.drop(columns=['label'])
                X = df.select_dtypes(include=[np.number]).to_numpy().astype(np.float32)
                if X.size == 0:
                    return {"error": "No numeric columns in CSV"}

            else:
                return {"error": f"Unsupported dataset extension: {os.path.basename(dataset_path)}"}

            # 3) Validate input shape compatibility
            expected = self.classifier.input_shape
            if len(expected) != len(X.shape[1:]) or tuple(X.shape[1:]) != tuple(expected):
                return {"error":
                    f"Model expects input shape {expected}, data has {X.shape[1:]}"}

            # 4) Normalize the data
            mins, maxs = X.min(axis=0), X.max(axis=0)
            X = (X - mins) / (maxs - mins + 1e-8)
            X = X.reshape((-1,) + tuple(expected))[:20]

            # 5) Dummy one-hot labels (class 0)
            nb = self.classifier.nb_classes
            Y  = np.zeros((len(X), nb), dtype=np.float32)
            Y[:,0] = 1.0

            # 6) Compute clean metrics (accuracy, cross-entropy, margin)
            preds = self.classifier.predict(X)
            clean_acc = float((preds.argmax(axis=1)==0).mean())
            eps = 1e-12
            ce_clean = -np.log(preds[:,0] + eps)
            ce_clean_mean = float(ce_clean.mean())
            sorted_probs = np.sort(preds, axis=1)
            runner_up    = sorted_probs[:,-2]
            margin_clean = preds[:,0] - runner_up
            margin_clean_mean = float(margin_clean.mean())

            results = {}
            # 7) Run adversarial attacks (FGSM and PGD)
            for Attack, key in ((FastGradientMethod, "fgsm"),
                                (ProjectedGradientDescent, "pgd")):
                params = {"estimator": self.classifier, "eps": 0.1}
                if key=="pgd": params["max_iter"] = 5
                attack = Attack(**params)
                X_adv  = attack.generate(X)
                adv_preds = self.classifier.predict(X_adv)
                adv_acc   = float((adv_preds.argmax(axis=1)==0).mean())
                # Adversarial CE & margin
                ce_adv = -np.log(adv_preds[:,0] + eps)
                ce_adv_mean = float(ce_adv.mean())
                sorted_adv  = np.sort(adv_preds, axis=1)
                runner_adv  = sorted_adv[:,-2]
                margin_adv  = adv_preds[:,0] - runner_adv
                margin_adv_mean = float(margin_adv.mean())
                # Compute perturbation norms
                delta = (X_adv - X).reshape((len(X), -1))
                l2   = np.linalg.norm(delta, axis=1)
                linf = np.max(np.abs(delta), axis=1)
                l0   = np.count_nonzero(delta, axis=1)
                metrics = {
                    "clean_accuracy":     clean_acc,
                    "adv_accuracy":       adv_acc,
                    "accuracy_drop":      abs(clean_acc-adv_acc),
                    "l2_dist_mean":       float(l2.mean()),
                    "l2_dist_max":        float(l2.max()),
                    "linf_dist_mean":     float(linf.mean()),
                    "linf_dist_max":      float(linf.max()),
                    "l0_dist_mean":       float(l0.mean()),
                    "l0_dist_max":        float(l0.max()),
                    "crossentropy_clean": ce_clean_mean,
                    "crossentropy_adv":   ce_adv_mean,
                    "margin_clean":       margin_clean_mean,
                    "margin_adv":         margin_adv_mean
                }
                results[key] = {"metrics": metrics}

            return results

        except Exception as e:
            return {"error": str(e)}
