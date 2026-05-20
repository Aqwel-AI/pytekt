"""Filesystem tools for Aion Vibe Coding."""

import os
from typing import Dict, Any

def write_file(path: str, content: str) -> str:
    """
    Create or overwrite a file with the given content.
    
    Parameters
    ----------
    path : str
        The path to the file (relative to current directory).
    content : str
        The content to write to the file.
    """
    try:
        os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)
        return f"Successfully wrote to {path}"
    except Exception as e:
        return f"Error writing to {path}: {e}"

def read_file(path: str) -> str:
    """
    Read the contents of a file.
    
    Parameters
    ----------
    path : str
        The path to the file.
    """
    try:
        if not os.path.exists(path):
            return f"Error: File {path} does not exist."
        with open(path, "r", encoding="utf-8") as f:
            return f.read()
    except Exception as e:
        return f"Error reading {path}: {e}"

def list_files(path: str = ".") -> str:
    """
    List files in a directory.
    
    Parameters
    ----------
    path : str
        The directory path (default is current directory).
    """
    try:
        files = os.listdir(path)
        return "\n".join(files) if files else "Directory is empty."
    except Exception as e:
        return f"Error listing {path}: {e}"
