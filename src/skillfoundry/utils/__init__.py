from __future__ import annotations

import hashlib
import time
from pathlib import Path


def hash_file(path: Path) -> str:
    """Return SHA256 hash of file contents."""
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            h.update(chunk)
    return h.hexdigest()

def hash_string(s: str) -> str:
    """Return SHA256 hash of string."""
    return hashlib.sha256(s.encode('utf-8')).hexdigest()

def hash_directory(path: Path) -> str:
    """Return hash of all file hashes in directory (sorted)."""
    if not path.is_dir():
        raise ValueError(f"{path} is not a directory")

    hashes = []
    for file_path in sorted(path.rglob("*")):
        if file_path.is_file():
            hashes.append(hash_file(file_path))

    h = hashlib.sha256()
    for file_hash in hashes:
        h.update(file_hash.encode('utf-8'))

    return h.hexdigest()

def format_size(bytes_size: int) -> str:
    """Return human-readable file size (e.g., 1.2 KB, 3.4 MB)."""
    if bytes_size < 1024:
        return f"{bytes_size} B"
    elif bytes_size < 1024 * 1024:
        return f"{bytes_size / 1024:.1f} KB"
    elif bytes_size < 1024 * 1024 * 1024:
        return f"{bytes_size / (1024 * 1024):.1f} MB"
    else:
        return f"{bytes_size / (1024 * 1024 * 1024):.1f} GB"

def truncate(text: str, max_length: int, suffix: str = '...') -> str:
    """Truncate text to max_length, appending suffix if truncated."""
    if len(text) <= max_length:
        return text
    return text[:max_length - len(suffix)] + suffix

def elapsed_ms(start_time: float) -> float:
    """Return milliseconds since start_time (time.perf_counter based)."""
    return (time.perf_counter() - start_time) * 1000.0

__all__ = [
    "elapsed_ms",
    "format_size",
    "hash_directory",
    "hash_file",
    "hash_string",
    "truncate"
]
