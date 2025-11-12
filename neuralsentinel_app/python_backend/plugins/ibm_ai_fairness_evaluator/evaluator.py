import os
import pandas as pd
from aif360.datasets import BinaryLabelDataset
from aif360.metrics import BinaryLabelDatasetMetric
from python_backend.core.interfaces import BaseEvaluator

# --------------------Evaluator for fairness metrics--------------------
class Evaluator(BaseEvaluator):
    """
    Plugin to evaluate fairness using IBM AIF360,
    automatically binarizing any column and keeping only
    label and protected columns for AIF360.
    """
    
    def __init__(self, logger):
        # Initialize the evaluator and set the metadata
        super().__init__(logger)
        self.meta = {
            "name": "ibm_ai_fairness_evaluator",
            "description": "Evaluates fairness using IBM AIF360",
            "functions": {
                "compute_fairness": self.compute_fairness
            }
        }

    def _binarize(self, series: pd.Series) -> pd.Series:
        """
        Convert a column into binary values (0 or 1).
        Numeric columns are binarized by the median.
        Categorical columns are binarized based on the mode (most frequent value).
        """
        if pd.api.types.is_numeric_dtype(series) and series.nunique() > 2:
            return (series >= series.median()).astype(int)
        if series.dtype == object and series.nunique() > 2:
            top = series.mode().iloc[0]
            return (series == top).astype(int)
        return pd.Categorical(series).codes

    def compute_fairness(self, input_data):
        """
        Compute the fairness metrics for the provided dataset.
        Args:
            input_data (dict): Contains the dataset path, label column, and protected column.
        Returns:
            dict: Contains fairness metrics (disparate impact, statistical parity difference, mean difference).
        """
        ds_path = input_data.get("dataset_path")
        lbl     = input_data.get("label_column")
        prot    = input_data.get("protected_column")

        # Check for missing parameters
        if not ds_path or not lbl or not prot:
            return {"error": "Missing parameters (dataset_path, label_column, protected_column)"}
        
        # Verify if dataset exists
        if not os.path.exists(ds_path):
            return {"error": f"Dataset not found: {ds_path}"}

        # Read dataset (supports CSV or Excel formats)
        ext = ds_path.lower().split('.')[-1]
        try:
            df = pd.read_csv(ds_path) if ext == "csv" else pd.read_excel(ds_path)
        except Exception as e:
            return {"error": f"Unable to read the dataset: {e}"}

        # Ensure the label and protected columns are present in the dataset
        for col in (lbl, prot):
            if col not in df.columns:
                return {"error": f"Column not found: {col}"}

        # Binarize the label and protected columns
        df[lbl]  = self._binarize(df[lbl])
        df[prot] = self._binarize(df[prot])

        # Keep only the label and protected columns
        df2 = df[[lbl, prot]].copy()

        # Create a BinaryLabelDataset for fairness evaluation
        try:
            bd = BinaryLabelDataset(
                df=df2,
                label_names=[lbl],
                protected_attribute_names=[prot]
            )
        except Exception as e:
            return {"error": f"Error creating BinaryLabelDataset: {e}"}

        # Compute fairness metrics
        try:
            m = BinaryLabelDatasetMetric(
                bd,
                privileged_groups=[{prot: 1}],
                unprivileged_groups=[{prot: 0}]
            )
            di  = m.disparate_impact()  # Disparate impact
            spd = m.statistical_parity_difference()  # Statistical parity difference
            md  = m.mean_difference()  # Mean difference
        except Exception as e:
            return {"error": f"Error calculating metrics: {e}"}

        # Return the fairness metrics
        return {
            "label_column": lbl,
            "protected_column": prot,
            "num_instances": int(bd.features.shape[0]),
            "disparate_impact": float(di),
            "statistical_parity_difference": float(spd),
            "mean_difference": float(md)
        }

    def evaluate(self, input_data):
        """
        Run the fairness evaluation and return the result.
        """
        return self.compute_fairness(input_data)
