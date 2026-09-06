import json
from pathlib import Path
from click.testing import CliRunner

from skillfoundry.cli.main import cli


def test_report_success(tmp_path: Path):
    runner = CliRunner()
    input_json = tmp_path / "eval_results.json"
    output_html = tmp_path / "report.html"
    
    sample_data = {
        "skill_name": "test_skill",
        "source_path": "/path/to/skill",
        "metadata": {
            "skillfoundry_version": "0.1.0",
            "evaluation_version": "1.0",
            "model_provider": "openai",
            "model_identifier": "gpt-4o",
            "skill_hash": "abc",
            "task_set_hash": "def",
            "config_hash": "ghi",
            "timestamp": "2025-01-01T00:00:00Z"
        },
        "evaluation": {
            "skill_name": "test_skill",
            "runs": [
                {
                    "run_id": "r1",
                    "task_results": [
                        {
                            "task_id": "t1",
                            "passed": True,
                            "response": "Success",
                            "label": "observed"
                        }
                    ],
                    "score": {
                        "overall": 85.0
                    }
                }
            ],
            "aggregate_score": {
                "overall": 85.0,
                "dimensions": [
                    {"name": "accuracy", "score": 0.9, "weight": 1.0}
                ]
            }
        }
    }
    
    input_json.write_text(json.dumps(sample_data))
    
    result = runner.invoke(cli, ['report', str(input_json), '-o', str(output_html)])
    
    assert result.exit_code == 0
    assert output_html.exists()
    assert "<!DOCTYPE html>" in output_html.read_text()


def test_report_invalid_json(tmp_path: Path):
    runner = CliRunner()
    input_json = tmp_path / "eval_results.json"
    input_json.write_text("{invalid json}")
    
    result = runner.invoke(cli, ['report', str(input_json)])
    
    assert result.exit_code == 1
    assert "Failed to parse input file" in result.output


def test_report_missing_file():
    runner = CliRunner()
    result = runner.invoke(cli, ['report', 'nonexistent.json'])
    
    assert result.exit_code != 0
    assert "does not exist" in result.output
