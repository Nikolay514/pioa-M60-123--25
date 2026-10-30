import pytest

from exceptions import (
    RecordNotFoundError,
    StorageError,
    ValidationError,
)
from file_database import FileDatabase

from pioa_dp.file_database import FileTable


def make_db(tmp_path):
    return FileDatabase(tmp_path / "data")


def test_persistence_between_runs(tmp_path):
    db = make_db(tmp_path)
    db.create_table("students", {"name": str, "age": int})
    db.get_table("students").insert({"name": "Аня", "age": 20})

    db2 = FileDatabase(tmp_path / "data")
    assert db2.get_table("students").select() == [
        {"id": 1, "name": "Аня", "age": 20}
    ]


def test_next_id_continues_after_load(tmp_path):
    db = make_db(tmp_path)
    db.create_table("t", {"x": int})
    db.get_table("t").insert({"x": 1})

    db2 = FileDatabase(tmp_path / "data")
    added = db2.get_table("t").insert({"x": 2})
    assert added["id"] == 2


def test_crud_and_sort_persist(tmp_path):
    db = make_db(tmp_path)
    t = db.create_table("nums", {"label": str, "value": int})
    t.insert({"label": "a", "value": 3})
    t.insert({"label": "b", "value": 1})

    db2 = FileDatabase(tmp_path / "data")
    t2 = db2.get_table("nums")

    assert [r["value"] for r in t2.select(sort_field="value")] == [1, 3]
    assert [r["value"] for r in t2.select(sort_field="value", reverse=True)] == [3, 1]

    t2.update(1, {"value": 10})
    t2.delete(2)
    with pytest.raises(RecordNotFoundError):
        t2.get(2)

    db3 = FileDatabase(tmp_path / "data")
    t3 = db3.get_table("nums")
    assert t3.get(1)["value"] == 10
    assert len(t3.select()) == 1


def test_filters_work_after_load(tmp_path):
    db = make_db(tmp_path)
    t = db.create_table("students", {"name": str, "age": int})
    t.insert({"name": "Аня", "age": 20})
    t.insert({"name": "Боря", "age": 22})

    db2 = FileDatabase(tmp_path / "data")
    result = db2.get_table("students").select({"age": 22})
    assert [r["name"] for r in result] == ["Боря"]


def test_invalid_record_not_saved(tmp_path):
    db = make_db(tmp_path)
    db.create_table("t", {"x": int})
    with pytest.raises(ValidationError):
        db.get_table("t").insert({"x": "строка вместо числа"})

    db2 = FileDatabase(tmp_path / "data")
    assert db2.get_table("t").select() == []


def test_corrupt_json_raises(tmp_path):
    make_db(tmp_path)
    (tmp_path / "data" / "bad.json").write_text("{это не json", encoding="utf-8")
    with pytest.raises(StorageError):
        FileDatabase(tmp_path / "data")


def test_wrong_schema_type_raises(tmp_path):
    make_db(tmp_path)
    (tmp_path / "data" / "t.json").write_text(
        '{"schema": {"x": "float"}, "records": []}', encoding="utf-8"
    )
    with pytest.raises(StorageError):
        FileDatabase(tmp_path / "data")


def test_schema_mismatch_raises(tmp_path):
    make_db(tmp_path)
    (tmp_path / "data" / "t.json").write_text(
        '{"schema": {"a": "str"}, "records": []}', encoding="utf-8"
    )
    with pytest.raises(StorageError):
        FileTable("t", {"b": int}, tmp_path / "data" / "t.json")


def test_duplicate_id_in_file_raises(tmp_path):
    make_db(tmp_path)
    (tmp_path / "data" / "t.json").write_text(
        '{"schema": {"x": "int"}, "records": [{"id": 1, "x": 1}, {"id": 1, "x": 2}]}',
        encoding="utf-8",
    )
    with pytest.raises(StorageError):
        FileDatabase(tmp_path / "data")


def test_tables_loaded_from_directory(tmp_path):
    db = make_db(tmp_path)
    db.create_table("one", {"a": int})
    db.create_table("two", {"b": str})

    db2 = FileDatabase(tmp_path / "data")
    assert sorted(db2.table_names()) == ["one", "two"]


def test_ui_compatible_with_file_db(tmp_path, tests=None):
    from tests.test_ui import FakeUI
    from ui import Menu

    db = make_db(tmp_path)
    db.create_table("students", {"name": str, "age": int})
    ui = FakeUI(["1", "1", "Аня", "20", "2", "", "", "", "0"])
    Menu(db, ui).run()

    assert "Запись добавлена." in ui.outputs
    reloaded = FileDatabase(tmp_path / "data").get_table("students").select()
    assert reloaded[0]["name"] == "Аня"
