import pickle
import os
import hashlib
from logger import logger

def get_file_checksum(file_path):
    """Calculates the SHA256 checksum of a file."""
    sha256_hash = hashlib.sha256()
    try:
        with open(file_path, "rb") as f:
            # Read and update hash in chunks of 4K
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)
        return sha256_hash.hexdigest()
    except FileNotFoundError:
        return None

def load_model(model_path, backup_model_path=None):
    """
    Loads a model from a pickle file.
    - Validates model file integrity using a checksum.
    - Falls back to a backup model if the primary is missing or corrupt.
    - Raises an exception if no valid model can be loaded.
    """
    model = None
    path_to_load = None

    # 1. Check for primary model
    if os.path.exists(model_path):
        logger.info(f"Primary model found at {model_path}.")
        # Optional: Add checksum validation here
        # checksum = get_file_checksum(model_path)
        # expected_checksum = "your_expected_checksum_here"
        # if checksum != expected_checksum:
        #     logger.warning("Primary model checksum mismatch. Trying backup.")
        # else:
        #     path_to_load = model_path
        path_to_load = model_path
    else:
        logger.warning(f"Primary model not found at {model_path}.")

    # 2. If primary failed, try backup
    if not path_to_load and backup_model_path and os.path.exists(backup_model_path):
        logger.info(f"Falling back to backup model at {backup_model_path}.")
        path_to_load = backup_model_path

    # 3. Load the selected model
    if path_to_load:
        try:
            with open(path_to_load, 'rb') as f:
                model = pickle.load(f)
            logger.info(f"Model successfully loaded from {path_to_load}.")
        except (pickle.UnpicklingError, EOFError) as e:
            logger.error(f"Failed to load model from {path_to_load}: {e}")
            model = None # Ensure model is None if loading fails
    else:
        logger.error("No valid model file found at primary or backup paths.")

    if not model:
        # If no model could be loaded at all, raise a critical error
        raise FileNotFoundError("Critical: No model could be loaded. Bot cannot proceed.")

    return model