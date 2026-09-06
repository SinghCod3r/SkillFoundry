import pytest
import os
from pathlib import Path
from skillfoundry.security.paths import validate_path, safe_join

def test_valid_path(tmp_path):
    workspace = tmp_path
    valid_file = workspace / "test.txt"
    valid_file.touch()
    assert validate_path(valid_file, workspace) == valid_file

def test_traversal_blocked(tmp_path):
    workspace = tmp_path
    with pytest.raises(ValueError, match="[tT]raversal"):
        validate_path("../../etc/passwd", str(workspace))

def test_absolute_escape_blocked(tmp_path):
    workspace = tmp_path
    with pytest.raises(ValueError, match="outside"):
        validate_path("/etc/passwd", str(workspace))

def test_safe_join():
    base = "/base/path"
    assert safe_join(base, "sub", "file.txt") == Path("/base/path/sub/file.txt")

def test_safe_join_traversal():
    base = "/base/path"
    with pytest.raises(ValueError, match="[tT]raversal"):
        safe_join(base, "../etc/passwd")
