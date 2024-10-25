import os
from pathlib import Path
import shutil
import logging

logger = logging.getLogger(__name__)

def ensure_directory_exists(directory_path):
    """
    Ensure that a directory exists, creating it if necessary
    
    Args:
        directory_path: Path or string pointing to the directory
    
    Returns:
        Path object of the directory
    """
    path = Path(directory_path)
    path.mkdir(parents=True, exist_ok=True)
    return path

def safe_file_write(file_path, content, backup=True):
    """
    Safely write content to a file with backup option
    
    Args:
        file_path: Path to the file
        content: Content to write
        backup: Whether to create a backup of existing file
    """
    path = Path(file_path)
    
    # Create backup if file exists and backup is requested
    if backup and path.exists():
        backup_path = path.with_suffix(path.suffix + '.bak')
        try:
            shutil.copy2(path, backup_path)
            logger.info(f"Created backup at {backup_path}")
        except Exception as e:
            logger.error(f"Failed to create backup: {str(e)}")
    
    # Write new content
    try:
        with open(path, 'w') as f:
            f.write(content)
        logger.info(f"Successfully wrote to {path}")
    except Exception as e:
        logger.error(f"Failed to write file {path}: {str(e)}")
        raise

def safe_file_read(file_path):
    """
    Safely read content from a file
    
    Args:
        file_path: Path to the file
    
    Returns:
        Content of the file as string
    """
    try:
        with open(file_path, 'r') as f:
            return f.read()
    except Exception as e:
        logger.error(f"Failed to read file {file_path}: {str(e)}")
        raise

def create_unique_filename(base_path, prefix="", suffix=""):
    """
    Create a unique filename in the given directory
    
    Args:
        base_path: Base directory path
        prefix: Optional prefix for the filename
        suffix: Optional suffix for the filename
        
    Returns:
        Path object with unique filename
    """
    path = Path(base_path)
    filename = f"{prefix}{suffix}"
    while (path / filename).exists():
        filename = f"{prefix}{suffix}.{len(filename.split('.'))}"
    return path / filename
