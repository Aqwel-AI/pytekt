#!/usr/bin/env python3
"""
PyTekt - File Management
=============================

File and directory utilities: create, read, write, append, delete, rename, copy;
file metadata; list files by pattern; create directories; organize by type;
batch rename; swap two paths. All functions return bool or optional value and
print errors on failure.
"""

# Import the os module for operating system interface functions
import os

# Import the shutil module for high-level file operations
import shutil

# Import the pathlib module for object-oriented filesystem paths
from pathlib import Path

# Import typing modules for type hints and annotations
from typing import List, Dict, Optional, Any, Union


PathLike = Union[str, os.PathLike]

# Import datetime module for date and time operations
from datetime import datetime

def create_empty_file(filepath: str) -> bool:
    """
    Create an empty file at the specified path.
    
    Args:
        filepath (str): The path where the file should be created
        
    Returns:
        bool: True if file was created successfully, False otherwise
    """
    try:
        # Create the file by opening it in write mode and immediately closing it
        with open(filepath, 'w') as f:
            # File is created empty
            pass
        
        # Return True to indicate successful creation
        return True
    except Exception as e:
        # Print error message if file creation fails
        print(f"Error creating file {filepath}: {e}")
        
        # Return False to indicate failure
        return False

def file_exists(filepath: str) -> bool:
    """
    Check if a file exists at the specified path.
    
    Args:
        filepath (str): The path to check for file existence
        
    Returns:
        bool: True if file exists, False otherwise
    """
    # Use os.path.exists to check if the file exists
    return os.path.exists(filepath)

def write_file(filepath: str, content: str) -> bool:
    """
    Write content to a file at the specified path.
    
    Args:
        filepath (str): The path where the file should be written
        content (str): The content to write to the file
        
    Returns:
        bool: True if file was written successfully, False otherwise
    """
    try:
        # Open the file in write mode and write the content
        with open(filepath, 'w', encoding='utf-8') as f:
            # Write the content to the file
            f.write(content)
        
        # Return True to indicate successful write
        return True
    except Exception as e:
        # Print error message if file write fails
        print(f"Error writing to file {filepath}: {e}")
        
        # Return False to indicate failure
        return False

def read_file(filepath: str) -> Optional[str]:
    """
    Read content from a file at the specified path.
    
    Args:
        filepath (str): The path of the file to read
        
    Returns:
        Optional[str]: The file content if successful, None otherwise
    """
    try:
        # Open the file in read mode and read the content
        with open(filepath, 'r', encoding='utf-8') as f:
            # Read the entire file content
            content = f.read()
        
        # Return the file content
        return content
    except Exception as e:
        # Print error message if file read fails
        print(f"Error reading file {filepath}: {e}")
        
        # Return None to indicate failure
        return None

def append_to_file(filepath: str, content: str) -> bool:
    """
    Append content to an existing file at the specified path.
    
    Args:
        filepath (str): The path of the file to append to
        content (str): The content to append to the file
        
    Returns:
        bool: True if content was appended successfully, False otherwise
    """
    try:
        # Open the file in append mode and write the content
        with open(filepath, 'a', encoding='utf-8') as f:
            # Write the content to the end of the file
            f.write(content)
        
        # Return True to indicate successful append
        return True
    except Exception as e:
        # Print error message if file append fails
        print(f"Error appending to file {filepath}: {e}")
        
        # Return False to indicate failure
        return False

def delete_file(filepath: str) -> bool:
    """
    Delete a file at the specified path.
    
    Args:
        filepath (str): The path of the file to delete
        
    Returns:
        bool: True if file was deleted successfully, False otherwise
    """
    try:
        # Remove the file using os.remove
        os.remove(filepath)
        
        # Return True to indicate successful deletion
        return True
    except Exception as e:
        # Print error message if file deletion fails
        print(f"Error deleting file {filepath}: {e}")
        
        # Return False to indicate failure
        return False

def rename_file(old_path: str, new_path: str) -> bool:
    """
    Rename a file from old_path to new_path.
    
    Args:
        old_path (str): The current path of the file
        new_path (str): The new path for the file
        
    Returns:
        bool: True if file was renamed successfully, False otherwise
    """
    try:
        # Rename the file using os.rename
        os.rename(old_path, new_path)
        
        # Return True to indicate successful rename
        return True
    except Exception as e:
        # Print error message if file rename fails
        print(f"Error renaming file from {old_path} to {new_path}: {e}")
        
        # Return False to indicate failure
        return False

def copy_file(source_path: str, destination_path: str) -> bool:
    """
    Copy a file from source_path to destination_path.
    
    Args:
        source_path (str): The path of the source file
        destination_path (str): The path where the file should be copied
        
    Returns:
        bool: True if file was copied successfully, False otherwise
    """
    try:
        # Copy the file using shutil.copy2 (preserves metadata)
        shutil.copy2(source_path, destination_path)
        
        # Return True to indicate successful copy
        return True
    except Exception as e:
        # Print error message if file copy fails
        print(f"Error copying file from {source_path} to {destination_path}: {e}")
        
        # Return False to indicate failure
        return False

def get_file_info(filepath: str) -> Optional[Dict[str, Any]]:
    """
    Get detailed information about a file.
    
    Args:
        filepath (str): The path of the file to get information about
        
    Returns:
        Optional[Dict[str, Any]]: File information dictionary or None if error
    """
    try:
        # Get file statistics using os.stat
        stat_info = os.stat(filepath)
        
        # Create a dictionary with file information
        file_info = {
            'path': filepath,  # File path
            'size': stat_info.st_size,  # File size in bytes
            'created': datetime.fromtimestamp(stat_info.st_ctime),  # Creation time
            'modified': datetime.fromtimestamp(stat_info.st_mtime),  # Last modified time
            'accessed': datetime.fromtimestamp(stat_info.st_atime),  # Last accessed time
            'is_file': os.path.isfile(filepath),  # Whether it's a file
            'is_directory': os.path.isdir(filepath),  # Whether it's a directory
            'exists': True  # File exists flag
        }
        
        # Return the file information dictionary
        return file_info
    except Exception as e:
        # Print error message if getting file info fails
        print(f"Error getting file info for {filepath}: {e}")
        
        # Return None to indicate failure
        return None

def list_files(directory: str, pattern: str = "*") -> List[str]:
    """
    List all files in a directory matching the specified pattern.
    
    Args:
        directory (str): The directory to list files from
        pattern (str): The file pattern to match (default: "*" for all files)
        
    Returns:
        List[str]: List of file paths matching the pattern
    """
    try:
        # Create a Path object for the directory
        dir_path = Path(directory)
        
        # Use glob to find files matching the pattern
        files = list(dir_path.glob(pattern))
        
        # Convert Path objects to strings and return
        return [str(f) for f in files if f.is_file()]
    except Exception as e:
        # Print error message if listing files fails
        print(f"Error listing files in {directory}: {e}")
        
        # Return empty list to indicate failure
        return []

def create_directory(directory_path: str) -> bool:
    """
    Create a directory at the specified path.
    
    Args:
        directory_path (str): The path where the directory should be created
        
    Returns:
        bool: True if directory was created successfully, False otherwise
    """
    try:
        # Create the directory using os.makedirs (creates parent directories if needed)\
        os.makedirs(directory_path, exist_ok=True)
        
        # Return True to indicate successful creation
        return True
    except Exception as e:
        # Print error message if directory creation fails
        print(f"Error creating directory {directory_path}: {e}")
        
        # Return False to indicate failure
        return False

def organize_files(source_dir: str, target_dir: str, file_types: Dict[str, List[str]]) -> bool:
    """
    Organize files by moving them to appropriate directories based on file types.
    
    Args:
        source_dir (str): The source directory containing files to organize
        target_dir (str): The target directory where organized files will be placed
        file_types (Dict[str, List[str]]): Dictionary mapping category names to file extensions
        
    Returns:
        bool: True if organization was successful, False otherwise
    """
    try:
        # Create the target directory if it doesn't exist
        create_directory(target_dir)
        
        # Get all files in the source directory
        files = list_files(source_dir)
        
        # Process each file
        for file_path in files:
            # Get the file extension
            file_ext = Path(file_path).suffix.lower()
            
            # Find the appropriate category for this file type
            category = None
            for cat, extensions in file_types.items():
                # Check if the file extension matches any in this category
                if file_ext in extensions:
                    category = cat
                    break
            
            # If category found, move the file
            if category:
                # Create category directory
                category_dir = os.path.join(target_dir, category)
                create_directory(category_dir)
                
                # Move the file to the category directory
                filename = os.path.basename(file_path)
                new_path = os.path.join(category_dir, filename)
                rename_file(file_path, new_path)
        
        # Return True to indicate successful organization
        return True
    except Exception as e:
        # Print error message if file organization fails
        print(f"Error organizing files: {e}")
        
        # Return False to indicate failure
        return False

def batch_rename_files(directory: str, prefix: str = "", suffix: str = "", 
                      start_number: int = 1) -> bool:
    """
    Rename all files in a directory with a consistent naming pattern.
    
    Args:
        directory (str): The directory containing files to rename
        prefix (str): Prefix to add to all filenames
        suffix (str): Suffix to add to all filenames
        start_number (int): Starting number for sequential naming
        
    Returns:
        bool: True if batch rename was successful, False otherwise
    """
    try:
        # Get all files in the directory
        files = list_files(directory)
        
        # Sort files to ensure consistent ordering
        files.sort()
        
        # Rename each file with the new pattern
        for i, file_path in enumerate(files):
            # Get the file extension
            file_ext = Path(file_path).suffix
            
            # Create new filename with prefix, number, and suffix
            new_filename = f"{prefix}{start_number + i:03d}{suffix}{file_ext}"
            
            # Create new file path
            new_path = os.path.join(directory, new_filename)
            
            # Rename the file
            rename_file(file_path, new_path)
        
        # Return True to indicate successful batch rename
        return True
    except Exception as e:
        # Print error message if batch rename fails
        print(f"Error batch renaming files: {e}")
        
        # Return False to indicate failure
        return False



def change_name(from_one: PathLike, from_two: PathLike) -> bool:
    """
    Swap two paths (files or directories) safely.

    Example:
        change_name("one.txt", "two.txt")  # one.txt ↔ two.txt

    Rules:
    - Both paths must exist
    - Both must be the same type (file↔file or dir↔dir)
    - Uses a temporary name to avoid collisions
    """
    a = Path(from_one)
    b = Path(from_two)

    try:
        if a.resolve() == b.resolve():
            return True  # nothing to do

        if not a.exists() or not b.exists():
            raise FileNotFoundError(f"Both paths must exist. Got: {a} (exists={a.exists()}), {b} (exists={b.exists()})")

        if a.is_file() != b.is_file() or a.is_dir() != b.is_dir():
            raise IsADirectoryError("Cannot swap a file with a directory.")

        # Temp path in the same directory as 'a' (same filesystem -> atomic rename)
        temp = a.with_name(f".__pytekt_swap__{a.name}__{os.getpid()}__")

        # Ensure temp doesn't exist (very unlikely, but safe)
        while temp.exists():
            temp = a.with_name(f"{temp.name}_x")

        a.rename(temp)  # a -> temp
        b.rename(a)     # b -> a
        temp.rename(b)  # temp -> b

        return True

    except Exception as e:
        print(f"Error swapping names: {e}")
        return False
    
    

import hashlib

def file_hash(file_name: str, hash_algo="sha256") -> str:
    try:
        hash_func = getattr(hashlib, hash_algo)()
    except AttributeError:
        raise ValueError(f"Hash algorithm '{hash_algo}' is not supported.")

    try:
        with open(file_name, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_func.update(chunk)
    except FileNotFoundError:
        raise FileNotFoundError(f"The file '{file_name}' does not exist.")

    return hash_func.hexdigest()



    
    
    
    
def read_lines(filepath: str) -> Optional[List[str]]:
    """
    Read a file and return its contents as a list of lines.

    Args:
        filepath (str): The path of the file to read

    Returns:
        Optional[List[str]]: List of lines if successful, None otherwise
    """
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            return f.readlines()
    except Exception as e:
        print(f"Error reading lines from {filepath}: {e}")
        return None


def write_lines(filepath: str, lines: List[str]) -> bool:
    """
    Write a list of lines to a file at the specified path.

    Args:
        filepath (str): The path where the file should be written
        lines (List[str]): Lines to write to the file

    Returns:
        bool: True if file was written successfully, False otherwise
    """
    try:
        with open(filepath, "w", encoding="utf-8") as f:
            f.writelines(lines)
        return True
    except Exception as e:
        print(f"Error writing lines to file {filepath}: {e}")
        return False


def safe_delete(filepath: str, trash_dir: Optional[str] = None) -> bool:
    """
    Move a file to a trash directory instead of deleting it.

    Args:
        filepath (str): File to move to trash
        trash_dir (str, optional): Destination trash directory. If not
            provided, a ".trash" directory is created next to the file.

    Returns:
        bool: True if file was moved successfully, False otherwise
    """
    try:
        src = Path(filepath)
        if not src.exists():
            print(f"File does not exist: {filepath}")
            return False

        trash_path = Path(trash_dir) if trash_dir else src.parent / ".trash"
        create_directory(str(trash_path))

        dest = trash_path / src.name
        if dest.exists():
            timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
            dest = trash_path / f"{src.stem}_{timestamp}{src.suffix}"

        shutil.move(str(src), str(dest))
        return True
    except Exception as e:
        print(f"Error moving file to trash {filepath}: {e}")
        return False


def ensure_directory(path: str) -> bool:
    """
    Ensure the parent directory for a path exists.

    Args:
        path (str): File or directory path

    Returns:
        bool: True if directory exists or was created, False otherwise
    """
    try:
        parent = Path(path).parent
        if parent and not parent.exists():
            os.makedirs(parent, exist_ok=True)
        return True
    except Exception as e:
        print(f"Error ensuring directory for {path}: {e}")
        return False


def copy_directory(source_dir: str, destination_dir: str) -> bool:
    """
    Copy a directory recursively.

    Args:
        source_dir (str): Source directory path
        destination_dir (str): Destination directory path

    Returns:
        bool: True if directory was copied successfully, False otherwise
    """
    try:
        shutil.copytree(source_dir, destination_dir, dirs_exist_ok=True)
        return True
    except Exception as e:
        print(f"Error copying directory {source_dir} to {destination_dir}: {e}")
        return False


def list_directories(directory: str) -> List[str]:
    """
    List subdirectories in a directory.

    Args:
        directory (str): Directory to list

    Returns:
        List[str]: List of directory paths
    """
    try:
        dir_path = Path(directory)
        return [str(p) for p in dir_path.iterdir() if p.is_dir()]
    except Exception as e:
        print(f"Error listing directories in {directory}: {e}")
        return []


def search_files(directory: str, pattern: str, recursive: bool = True) -> List[str]:
    """
    Search for files matching a pattern.

    Args:
        directory (str): Directory to search
        pattern (str): Glob pattern to match
        recursive (bool): Search recursively if True

    Returns:
        List[str]: List of matching file paths
    """
    try:
        dir_path = Path(directory)
        if recursive:
            matches = dir_path.rglob(pattern)
        else:
            matches = dir_path.glob(pattern)
        return [str(p) for p in matches if p.is_file()]
    except Exception as e:
        print(f"Error searching files in {directory}: {e}")
        return []


def file_size_human(filepath: str) -> Optional[str]:
    """
    Get a human-readable file size.

    Args:
        filepath (str): File path

    Returns:
        Optional[str]: Human-readable size string or None if error
    """
    try:
        size = os.path.getsize(filepath)
        units = ["B", "KB", "MB", "GB", "TB"]
        for unit in units:
            if size < 1024 or unit == units[-1]:
                return f"{size:.2f} {unit}"
            size /= 1024
    except Exception as e:
        print(f"Error getting size for {filepath}: {e}")
        return None


def get_directory_size(directory: str) -> Optional[int]:
    """
    Get total size of all files in a directory.

    Args:
        directory (str): Directory path

    Returns:
        Optional[int]: Total size in bytes or None if error
    """
    try:
        total = 0
        for root, _, files in os.walk(directory):
            for name in files:
                total += os.path.getsize(os.path.join(root, name))
        return total
    except Exception as e:
        print(f"Error getting directory size for {directory}: {e}")
        return None


def compare_files(file_a: str, file_b: str, hash_algo: str = "sha256") -> bool:
    """
    Compare two files by hash.

    Args:
        file_a (str): First file path
        file_b (str): Second file path
        hash_algo (str): Hash algorithm

    Returns:
        bool: True if files match, False otherwise
    """
    try:
        return file_hash(file_a, hash_algo) == file_hash(file_b, hash_algo)
    except Exception as e:
        print(f"Error comparing files {file_a} and {file_b}: {e}")
        return False


def backup_file(filepath: str, suffix: str = ".bak") -> Optional[str]:
    """
    Create a backup copy of a file.

    Args:
        filepath (str): File to back up
        suffix (str): Backup suffix

    Returns:
        Optional[str]: Backup file path or None if error
    """
    try:
        src = Path(filepath)
        if not src.exists():
            raise FileNotFoundError(f"File does not exist: {filepath}")

        backup_path = src.with_name(f"{src.name}{suffix}")
        if backup_path.exists():
            timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
            backup_path = src.with_name(f"{src.name}{suffix}.{timestamp}")

        shutil.copy2(str(src), str(backup_path))
        return str(backup_path)
    except Exception as e:
        print(f"Error backing up file {filepath}: {e}")
        return None


def touch_file(filepath: str) -> bool:
    """
    Update file modification time or create the file if missing.

    Args:
        filepath (str): File path

    Returns:
        bool: True if successful, False otherwise
    """
    try:
        ensure_directory(filepath)
        Path(filepath).touch()
        return True
    except Exception as e:
        print(f"Error touching file {filepath}: {e}")
        return False