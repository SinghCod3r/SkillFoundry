from pathlib import Path

from skillfoundry.skills.validator import SkillValidator


def test_valid_skill():
    validator = SkillValidator()
    result = validator.validate(Path("tests/fixtures/valid-skill"))
    assert result.valid
    assert not result.errors

def test_invalid_name():
    validator = SkillValidator()
    result = validator.validate(Path("tests/fixtures/invalid-skill"))
    assert not result.valid
    assert any("name" in err.lower() for err in result.errors)

def test_missing_skill_md(tmp_path):
    validator = SkillValidator()
    result = validator.validate(Path(tmp_path))
    assert not result.valid
    assert any("skill.md" in err.lower() for err in result.errors)

def test_frontmatter_parsing():
    validator = SkillValidator()
    result = validator.validate(Path("tests/fixtures/malformed-project"))
    assert not result.valid
    assert any("yaml" in err.lower() or "parse" in err.lower() or "name" in err.lower() or "description" in err.lower() for err in result.errors)
