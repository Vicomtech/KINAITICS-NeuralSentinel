#!/usr/bin/env python
import os
import sys
import glob
import pandas as pd
import numpy as np
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler
import joblib
import time
import argparse

# We define the default directory for storing user behavior data (CSV files).
DEFAULT_MODEL_DIR = os.path.join(
    os.getenv('APPDATA', ''),
    'neuralsentinel-electron',
    'user_behavior'
)

class ContinuousAuthenticator:
    """
    This class implements continuous user authentication using behavioral biometrics.
    It uses an Isolation Forest model to detect anomalies in user behavior.
    """
    def __init__(self, contamination=0.01, random_state=42):
        # We initialize a StandardScaler and an IsolationForest model with the given parameters.
        self.scaler = StandardScaler()
        self.model = IsolationForest(contamination=contamination, random_state=random_state)
        self.is_trained = False

    def _load_sessions(self, data_dir):
        """
        This function loads CSV or XLS files that contain user behavior data.
        It checks the specified directory for CSV and XLS files and loads them into a pandas DataFrame.
        """
        patterns = [os.path.join(data_dir, '*.csv'), os.path.join(data_dir, '*.xls*')]
        files = []
        for pat in patterns:
            files.extend(glob.glob(pat))
        if not files:
            raise FileNotFoundError(f"No CSV/XLSX files found in {data_dir}")

        dfs = []
        for path in files:
            try:
                if path.lower().endswith(('.xls', '.xlsx')):
                    dfs.append(pd.read_excel(path))
                else:
                    dfs.append(pd.read_csv(path))
            except Exception as e:
                raise ValueError(f"Error loading file {path}: {e}")

        return pd.concat(dfs, ignore_index=True)

    def _prepare_features(self, df):
        """
        This function processes the DataFrame by selecting and preparing relevant features for model training.
        If a 'heatmap_cells' column exists, it computes a new 'heatmap_sum' column.
        """
        df = df.copy()
        if 'heatmap_cells' in df.columns:
            df['heatmap_sum'] = df['heatmap_cells'].apply(
                lambda s: sum(int(x) for x in str(s).split(','))
            )

        cols = [
            'cursor_speed','left_clicks','right_clicks',
            'left_double_clicks','right_double_clicks',
            'movement_to_click_time','avg_key_interval','avg_key_duration',
            'backspace','enter','shift','ctrl','alt',
            'caps_lock','tab','esc','space'
        ]
        if 'heatmap_sum' in df.columns:
            cols.append('heatmap_sum')

        missing = set(cols) - set(df.columns)
        if missing:
            raise KeyError(f"Missing columns: {missing}")

        return df[cols].astype(float)

    def fit(self, data_dir, save_prefix='user_auth', model_dir=None, contamination=None):
        """
        This function trains the continuous authenticator using data from CSV or XLS files located in the specified directory.
        It saves the trained model and scaler to the specified directory.
        """
        if contamination is not None:
            self.model.set_params(contamination=contamination)

        try:
            df = self._load_sessions(data_dir)
        except FileNotFoundError as e:
            raise ValueError(f"Could not load sessions: {e}")

        if hasattr(self, 'username') and self.username:
            df = df[df['user'] == self.username]
            if df.empty:
                raise ValueError(f"No data for user {self.username}")

        X = self._prepare_features(df)
        Xs = self.scaler.fit_transform(X)

        try:
            self.model.fit(Xs)
        except Exception as e:
            raise ValueError(f"Error training model: {e}")

        self.is_trained = True

        out_dir = model_dir or DEFAULT_MODEL_DIR
        os.makedirs(out_dir, exist_ok=True)
        user_prefix = f"{self.username}_" if getattr(self, 'username', None) else ""
        joblib.dump(self.scaler, os.path.join(out_dir, f"{user_prefix}{save_prefix}_scaler.pkl"))
        joblib.dump(self.model,  os.path.join(out_dir, f"{user_prefix}{save_prefix}_model.pkl"))
        print(f"Saved scaler and model in {out_dir}")

    def load(self, load_prefix='user_auth', model_dir=None):
        """
        This function loads a pre-trained model and scaler from the specified directory.
        """
        d = model_dir or DEFAULT_MODEL_DIR
        user_prefix = f"{self.username}_" if getattr(self, 'username', None) else ""
        try:
            # ➤ now include the user prefix when loading
            self.scaler = joblib.load(os.path.join(d, f"{user_prefix}{load_prefix}_scaler.pkl"))
            self.model  = joblib.load(os.path.join(d, f"{user_prefix}{load_prefix}_model.pkl"))
        except Exception as e:
            raise ValueError(f"Error loading model or scaler: {e}")

        self.is_trained = True
        print(f"Loaded scaler and model from {d}")

    def authenticate(self, feat):
        """
        This function authenticates the user based on their behavioral features.
        It uses the trained model to detect anomalies in the behavior.
        """
        if not self.is_trained:
            raise ValueError("Model not trained.")

        data = feat.copy()
        if 'heatmap_cells' in data:
            data['heatmap_sum'] = sum(int(x) for x in data['heatmap_cells'].split(','))

        cols = [
            'cursor_speed','left_clicks','right_clicks',
            'left_double_clicks','right_double_clicks',
            'movement_to_click_time','avg_key_interval','avg_key_duration',
            'backspace','enter','shift','ctrl','alt',
            'caps_lock','tab','esc','space'
        ]
        if 'heatmap_sum' in data:
            cols.append('heatmap_sum')

        arr = np.array([data[c] for c in cols], dtype=float).reshape(1, -1)

        try:
            xs = self.scaler.transform(arr)
        except Exception as e:
            raise ValueError(f"Error during feature transformation: {e}")

        try:
            pred = self.model.predict(xs)
        except Exception as e:
            raise ValueError(f"Error during prediction: {e}")

        return pred[0] == 1

def main():
    """
    The main function handles command-line arguments and executes continuous authentication.
    """
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest='cmd', required=True)

    p_train = sub.add_parser('train')
    p_train.add_argument('--user', default=None, help="Filter training data by this username")
    p_train.add_argument('--data_dir',    required=True)
    p_train.add_argument('--save_prefix', default='user_auth')
    p_train.add_argument('--model_dir',   default=None)
    p_train.add_argument('--contamination', type=float, default=None)

    p_run = sub.add_parser('run')
    p_run.add_argument('--user', default=None, help="Which user's model to load/authenticate")
    p_run.add_argument('--load_prefix', default='user_auth')
    p_run.add_argument('--model_dir',   default=None)
    p_run.add_argument('--interval',    type=float, default=5.0)

    args = parser.parse_args()
    auth = ContinuousAuthenticator()
    auth.username = getattr(args, 'user', None)

    if args.cmd == 'train':
        try:
            auth.fit(args.data_dir, args.save_prefix, args.model_dir, args.contamination)
        except ValueError as e:
            print(f"ERROR during training: {e}", file=sys.stderr)
        return

    try:
        auth.username = args.user
        auth.load(args.load_prefix, args.model_dir)
        print("Starting continuous authentication… Ctrl+C to exit.")
        # Después:
        csv_dir = os.path.join(args.model_dir or DEFAULT_MODEL_DIR, auth.username)


        try:
            while True:
                try:
                    files = glob.glob(os.path.join(csv_dir, 'mouse_keyboard_stats_*.csv'))
                    if not files:
                        raise FileNotFoundError(f"No CSV files in {csv_dir}")
                    latest = max(files, key=os.path.getmtime)
                    df = pd.read_csv(latest)
                    row = df.iloc[-1].to_dict()
                    feat = {
                        'cursor_speed':         row['cursor_speed'],
                        'left_clicks':          row['left_clicks'],
                        'right_clicks':         row['right_clicks'],
                        'left_double_clicks':   row['left_double_clicks'],
                        'right_double_clicks':  row['right_double_clicks'],
                        'movement_to_click_time': row['movement_to_click_time'],
                        'avg_key_interval':     row['avg_key_interval'],
                        'avg_key_duration':     row['avg_key_duration'],
                        'backspace':            row['backspace'],
                        'enter':                row['enter'],
                        'shift':                row['shift'],
                        'ctrl':                 row['ctrl'],
                        'alt':                  row['alt'],
                        'caps_lock':            row['caps_lock'],
                        'tab':                  row['tab'],
                        'esc':                  row['esc'],
                        'space':                row['space'],
                        'heatmap_cells':        row['heatmap_cells']
                    }
                    normal = auth.authenticate(feat)
                    if not normal:
                        print("ANOMALY_DETECTED", flush=True)
                except Exception as e:
                    print(f"ERROR: {e}", file=sys.stderr, flush=True)
                time.sleep(args.interval)
        except KeyboardInterrupt:
            print("Stopped.")
    except ValueError as e:
        print(f"ERROR loading model: {e}", file=sys.stderr)

if __name__ == '__main__':
    main()