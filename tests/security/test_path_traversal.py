import pytest

from skillfoundry.security.paths import safe_join, validate_path


@pytest.mark.security
def test_traversal_in_generated_path(tmp_path):
    with pytest.raises(ValueError):
        validate_path("../../../etc/passwd", str(tmp_path))

@pytest.mark.security
def test_traversal_in_skill_output(tmp_path):
    with pytest.raises(ValueError):
        safe_join(str(tmp_path), "../../../etc/passwd")
