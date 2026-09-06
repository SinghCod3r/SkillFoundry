import tomlkit
from pathlib import Path

p = Path("pyproject.toml")
doc = tomlkit.parse(p.read_text())

if "tool" in doc and "ruff" in doc["tool"]:
    if "lint" in doc["tool"]["ruff"]:
        doc["tool"]["ruff"]["lint"]["ignore"] = ["E501", "S105", "TC001", "TC002", "TC003", "B007", "F841", "RUF043"]
        
p.write_text(tomlkit.dumps(doc))
