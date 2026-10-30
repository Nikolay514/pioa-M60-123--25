import pytest

from database import Database, Table
from exceptions import (
    RecordNotFoundError,
    TableNotFoundError,
    ValidationError,
)


@pytest.fixture
def table():
    t = Table("students", {"name": str, "age": int})
    t.insert({"name": "Аня", "age": 20})
    t.insert({"name": "Боря", "age": 22})
    t.insert({"name": "Вера", "age": 21})
    return t


def test_insert_assigns_sequential_ids(table):
    assert table._records[1]["name"] == "Аня"
    assert table._records[3]["name"] == "Вера" and table._records[3]["age"] == 21


def test_insert_validates_types(table):
    with pytest.raises(ValidationError):
        table.insert({"name": 123, "age": 20})


def test_get_existing_record(table):
    assert table.get(2)["name"] == "Боря"


def test_get_missing_record_raises(table):
    with pytest.raises(RecordNotFoundError):
        table.get(999)


def test_select_without_filters_returns_all(table):
    assert len(table.select()) == 3


def test_select_with_single_filter(table):
    result = table.select({"age": 21})
    assert [rec["name"] for rec in result] == ["Вера"]


def test_select_with_multiple_filters(table):
    result = table.select({"age": 22, "name": "Боря"})
    assert len(result) == 1


def test_select_nothing_matches(table):
    assert table.select({"name": "Гоша"}) == []


def test_select_unknown_field_raises(table):
    with pytest.raises(ValidationError):
        table.select({"height": 180})


def test_select_sort_ascending(table):
    result = table.select(sort_field="age")
    assert [rec["age"] for rec in result] == [20, 21, 22]


def test_select_sort_descending(table):
    result = table.select(sort_field="age", reverse=True)
    assert [rec["age"] for rec in result] == [22, 21, 20]


def test_select_sort_by_unknown_field_raises(table):
    with pytest.raises(ValidationError):
        table.select(sort_field="height")


def test_select_sort_by_id(table):
    result = table.select(sort_field="id", reverse=True)
    assert [rec["id"] for rec in result] == [3, 2, 1]


def test_update_changes_fields(table):
    updated = table.update(1, {"age": 25})
    assert updated["age"] == 25 and updated["name"] == "Аня"


def test_update_missing_record_raises(table):
    with pytest.raises(RecordNotFoundError):
        table.update(999, {"age": 1})


def test_update_unknown_field_raises(table):
    with pytest.raises(ValidationError):
        table.update(1, {"height": 180})


def test_update_empty_changes_raises(table):
    with pytest.raises(ValidationError):
        table.update(1, {})


def test_delete_removes_record(table):
    table.delete(2)
    assert len(table.select()) == 2
    with pytest.raises(RecordNotFoundError):
        table.get(2)


def test_delete_missing_record_raises(table):
    with pytest.raises(RecordNotFoundError):
        table.delete(999)


def test_create_table():
    db = Database()
    db.create_table("students", {"name": str})
    assert db.table_names() == ["students"]


def test_create_duplicate_table_raises():
    db = Database()
    db.create_table("t1", {"a": int})
    with pytest.raises(ValidationError):
        db.create_table("t1", {"b": int})


def test_create_table_with_empty_schema_raises():
    with pytest.raises(ValidationError):
        Database().create_table("t1", {})


def test_get_missing_table_raises():
    with pytest.raises(TableNotFoundError):
        Database().get_table("nope")


def test_multiple_tables_are_independent():
    db = Database()
    students = db.create_table("students", {"name": str})
    grades = db.create_table("grades", {"student_id": int, "grade": int})
    students.insert({"name": "Аня"})
    grades.insert({"student_id": 1, "grade": 5})

    assert len(students.select()) == 1
    assert len(grades.select()) == 1
