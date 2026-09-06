"""Inventory discovery must never traverse generated directories."""

from pathlib import Path

from skillfoundry.analysis.inventory import discover_files
from skillfoundry.config.settings import AnalysisSettings


def test_discovery_skips_generated_directories(tmp_path: Path):
    settings = AnalysisSettings()
    (tmp_path / "src").mkdir()
    (tmp_path / "src" / "main.py").write_text("print('x')\n")
    (tmp_path / "README.md").write_text("readme\n")

    for generated in (".git", "node_modules", ".venv", "__pycache__", "dist", "build"):
        d = tmp_path / generated
        d.mkdir()
        (d / "junk.js").write_text("generated\n")

    found = discover_files(tmp_path, settings)
    paths = [f.path for f in found]

    assert (tmp_path / "src" / "main.py") in [tmp_path / p for p in paths]
    assert (tmp_path / "README.md") in [tmp_path / p for p in paths]
    assert all("node_modules" not in str(p) for p in paths)
    assert all(".git" not in str(p) for p in paths)
    assert all(".venv" not in str(p) for p in paths)
    assert all("__pycache__" not in str(p) for p in paths)
    assert all("dist" not in str(p) for p in paths)
    assert all("build" not in str(p) for p in paths)


def test_discovery_still_finds_normal_sources(tmp_path: Path):
    settings = AnalysisSettings()
    (tmp_path / "lib").mkdir()
    (tmp_path / "lib" / "core.py").write_text("x = 1\n")
    found = discover_files(tmp_path, settings)
    assert any("lib/core.py" in str(f.path) for f in found)
