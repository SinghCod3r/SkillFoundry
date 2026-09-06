import pytest
from pydantic import ValidationError

from skillfoundry.models.skill import SkillMetadata, normalize_skill_name


def test_valid_skill_name():
    assert normalize_skill_name('my-skill') == 'my-skill'
    assert normalize_skill_name('a') == 'a'
    assert normalize_skill_name('abc-def-123') == 'abc-def-123'

def test_invalid_skill_name():
    invalid_names = ['My-Skill', '-start', 'end-', 'has--double', 'a' * 65, 'has space', 'UPPER']
    for name in invalid_names:
        with pytest.raises(ValidationError):
            SkillMetadata(name=name, description="test")

def test_normalize_skill_name():
    assert normalize_skill_name('My Amazing Project!') == 'my-amazing-project'
    assert normalize_skill_name('hello_world') == 'hello-world'
    assert normalize_skill_name('---') == 'unnamed-skill'
    assert normalize_skill_name('') == 'unnamed-skill'

def test_skill_metadata_validation():
    valid = SkillMetadata(name="valid-skill", description="Valid description")
    assert valid.name == "valid-skill"

    with pytest.raises(ValidationError):
        SkillMetadata(description="Missing name")

    with pytest.raises(ValidationError):
        SkillMetadata(name="valid-skill", description="")

    with pytest.raises(ValidationError):
        SkillMetadata(name="a" * 65, description="Too long name")
