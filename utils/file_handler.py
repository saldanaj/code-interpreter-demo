"""
File handling utilities for managing generated files from Azure AI agents.
Handles file downloads, path management, and file type detection.
"""

import os
from pathlib import Path
from typing import List, Dict, Any, Optional


# Directory where generated files will be stored
DOWNLOADS_DIR = Path("downloads")


def ensure_downloads_directory() -> Path:
    """
    Ensure the downloads directory exists.

    Returns:
        Path: Path to the downloads directory
    """
    DOWNLOADS_DIR.mkdir(exist_ok=True)
    return DOWNLOADS_DIR


def get_file_extension(file_info: Dict[str, Any]) -> str:
    """
    Determine the file extension based on file information.

    Args:
        file_info: Dictionary containing file metadata

    Returns:
        str: File extension including the dot (e.g., '.png', '.csv')
    """
    # Check if extension is already provided
    if 'extension' in file_info:
        return file_info['extension']

    # Determine by file type
    file_type = file_info.get('type', 'file')
    if file_type == 'image':
        return '.png'
    elif file_type == 'file':
        # Could be CSV or other types
        # Check if text field gives us a clue
        text = file_info.get('text', '').lower()
        if 'csv' in text:
            return '.csv'
        elif 'json' in text:
            return '.json'
        elif 'txt' in text or 'text' in text:
            return '.txt'
        else:
            return '.csv'  # Default to CSV for data files

    return '.dat'  # Generic fallback


def generate_file_path(file_id: str, file_info: Dict[str, Any]) -> Path:
    """
    Generate a local file path for a downloaded file.

    Args:
        file_id: The file ID from Azure
        file_info: Dictionary containing file metadata

    Returns:
        Path: Full path where the file should be saved
    """
    ensure_downloads_directory()
    extension = get_file_extension(file_info)
    file_name = f"{file_id}{extension}"
    return DOWNLOADS_DIR / file_name


def download_files(agent_manager, file_list: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Download multiple files from the agent.

    Args:
        agent_manager: AzureAgentManager instance
        file_list: List of file information dictionaries

    Returns:
        List of dictionaries with file information including local paths
    """
    downloaded_files = []

    for file_info in file_list:
        file_id = file_info.get('file_id')
        if not file_id:
            continue

        try:
            # Generate local path
            local_path = generate_file_path(file_id, file_info)

            # Download the file
            success = agent_manager.download_file(file_id, str(local_path))

            if success and local_path.exists():
                downloaded_files.append({
                    **file_info,
                    'local_path': str(local_path),
                    'file_name': local_path.name,
                    'success': True
                })
            else:
                downloaded_files.append({
                    **file_info,
                    'success': False,
                    'error': 'Download failed'
                })

        except Exception as e:
            print(f"Error downloading file {file_id}: {str(e)}")
            downloaded_files.append({
                **file_info,
                'success': False,
                'error': str(e)
            })

    return downloaded_files


def get_file_display_name(file_info: Dict[str, Any]) -> str:
    """
    Get a user-friendly display name for a file.

    Args:
        file_info: Dictionary containing file metadata

    Returns:
        str: Display name for the file
    """
    file_type = file_info.get('type', 'file')

    if file_type == 'image':
        return "Generated Chart"
    elif file_type == 'file':
        # Try to extract name from annotation text
        text = file_info.get('text', '')
        if text:
            # Extract filename from text if present
            if '/' in text or '\\' in text:
                return Path(text).name
            return f"Data File ({text})"
        return "Generated File"

    return "Download File"


def cleanup_old_files(max_files: int = 50):
    """
    Clean up old files in the downloads directory to prevent unlimited growth.

    Args:
        max_files: Maximum number of files to keep
    """
    try:
        if not DOWNLOADS_DIR.exists():
            return

        # Get all files sorted by modification time
        files = sorted(DOWNLOADS_DIR.glob("*"), key=lambda x: x.stat().st_mtime)

        # Remove oldest files if we exceed max_files
        if len(files) > max_files:
            files_to_remove = files[:len(files) - max_files]
            for file_path in files_to_remove:
                try:
                    file_path.unlink()
                    print(f"Removed old file: {file_path.name}")
                except Exception as e:
                    print(f"Error removing file {file_path}: {str(e)}")

    except Exception as e:
        print(f"Error during cleanup: {str(e)}")


def read_file_bytes(file_path: str) -> Optional[bytes]:
    """
    Read file contents as bytes for download buttons.

    Args:
        file_path: Path to the file

    Returns:
        bytes: File contents or None if error
    """
    try:
        with open(file_path, 'rb') as f:
            return f.read()
    except Exception as e:
        print(f"Error reading file {file_path}: {str(e)}")
        return None


def get_mime_type(file_info: Dict[str, Any]) -> str:
    """
    Get the MIME type for a file.

    Args:
        file_info: Dictionary containing file metadata

    Returns:
        str: MIME type string
    """
    file_type = file_info.get('type', 'file')
    extension = get_file_extension(file_info)

    if file_type == 'image' or extension == '.png':
        return 'image/png'
    elif extension == '.jpg' or extension == '.jpeg':
        return 'image/jpeg'
    elif extension == '.csv':
        return 'text/csv'
    elif extension == '.json':
        return 'application/json'
    elif extension == '.txt':
        return 'text/plain'
    else:
        return 'application/octet-stream'
