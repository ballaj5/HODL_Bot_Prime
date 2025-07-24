# src/utils/model.py
import os
import logging
import pickle
import pandas as pd
import xgboost as xgb
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score

# --- Configuration ---
MODEL_DIR = "/workspace/models_data"
os.makedirs(MODEL_DIR, exist_ok=True)
logging.basicConfig(level=logging.INFO)

def _get_model_path(symbol: str, timeframe: str) -> str:
    """Generates a standardized path for a model file."""
    return os.path.join(MODEL_DIR, f"{symbol}USDT_{timeframe}_model.pkl")

def train_model(symbol: str, timeframe: str, df: pd.DataFrame):
    """Trains an XGBoost classifier and saves it to a file."""
    try:
        # --- Feature Engineering ---
        df['target'] = (df['close'].shift(-1) > df['close']).astype(int)
        df.dropna(inplace=True)

        # --- CORRECTED FEATURE SELECTION ---
        # Dynamically use all columns as features except for 'timestamp' and the 'target'
        features = [col for col in df.columns if col not in ['timestamp', 'target']]
        X = df[features]
        y = df['target']

        if len(X) < 20:
            logging.warning(f"Not enough data for {symbol}-{timeframe} after processing.")
            return

        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42, shuffle=False
        )

        # --- Model Training ---
        model = xgb.XGBClassifier(
            objective='binary:logistic',
            eval_metric='logloss',
            use_label_encoder=False,
            n_estimators=100
        )
        model.fit(X_train, y_train)

        # --- Evaluation & Save ---
        accuracy = accuracy_score(y_test, model.predict(X_test))
        logging.info(f"Model for {symbol}-{timeframe} trained with accuracy: {accuracy:.2f}")
        
        with open(_get_model_path(symbol, timeframe), 'wb') as f:
            pickle.dump(model, f)
        logging.info(f"Model saved to {_get_model_path(symbol, timeframe)}")

    except Exception as e:
        logging.error(f"Error training model for {symbol}-{timeframe}: {e}", exc_info=True)

def load_model(symbol: str, timeframe: str):
    """Loads a trained model from a file."""
    model_path = _get_model_path(symbol, timeframe)
    if not os.path.exists(model_path):
        logging.warning(f"Model file not found: {model_path}")
        return None
    try:
        with open(model_path, 'rb') as f:
            return pickle.load(f)
    except Exception as e:
        logging.error(f"Error loading model from {model_path}: {e}")
        return None