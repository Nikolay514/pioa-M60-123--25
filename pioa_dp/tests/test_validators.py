import pytest

from exceptions import ValidationError
from validators import validate_record


SCHEMA = {"name": str, "age": int}


def test_valid_record_passes():
    assert validate_record(SCHEMA, {"name": "Аня", "age": 20}) == {"name": "Аня", "age": 20}


def test_record_not_dict_raises():
    with pytest.raises(ValidationError):
        validate_record(SCHEMA, ["Аня", 20])


def test_missing_field_raises():
    with pytest.raises(ValidationError):
        validate_record(SCHEMA, {"name": "Аня"})


def test_wrong_type_raises():
    with pytest.raises(ValidationError):
        validate_record(SCHEMA, {"name": "Аня", "age": "20"})


def test_extra_fields_are_ignored():
    result = validate_record(SCHEMA, {"name": "Аня", "age": 20, "height": 180})
    assert "height" not in result
