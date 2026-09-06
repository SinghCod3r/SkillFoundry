import pytest

from skillfoundry.security.sandbox import run_sandboxed, validate_command


@pytest.mark.security
def test_blocked_commands():
    with pytest.raises(ValueError):
        validate_command(["rm", "-rf", "/"])

    with pytest.raises(ValueError):
        validate_command(["sudo", "ls"])

@pytest.mark.security
def test_shell_string_rejected():
    with pytest.raises(TypeError):
        # We only accept list[str] to prevent shell injection via shell=True
        run_sandboxed("echo hello; rm -rf /")
