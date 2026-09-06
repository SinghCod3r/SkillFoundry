import pytest

from skillfoundry.security.process_runner import run_process, ProcessConfig, validate_command


@pytest.mark.security
def test_blocked_commands():
    with pytest.raises(ValueError):
        validate_command(["rm", "-rf", "/"])

    with pytest.raises(ValueError):
        validate_command(["sudo", "ls"])

@pytest.mark.security
def test_shell_string_rejected(tmp_path):
    with pytest.raises(TypeError):
        # We only accept list[str] to prevent shell injection via shell=True
        run_process("echo hello; rm -rf /", ProcessConfig(workspace=str(tmp_path)))
