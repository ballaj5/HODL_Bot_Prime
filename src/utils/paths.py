# utils/paths.py
import os

def get_path(filename: str) -> str:
    """
    Returns the full path to a file inside the data directory.
    Creates the directory if it does not exist.
    """
    base = os.getenv("DATA_DIR", "data")
    os.makedirs(base, exist_ok=True)
    return os.path.join(base, filename)
