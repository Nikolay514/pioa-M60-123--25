import pytest

from database import Database
from ui import Menu, ConsoleUI


class FakeUI(ConsoleUI):
    def __init__(self, answers: list[str]):
        self.answers = answers
        self.outputs = []

    def ask(self, prompt: str) -> str:
        return self.answers.pop(0) if self.answers else ""

    def tell(self, message: str) -> None:
        self.outputs.append(message)


@pytest.fixture
def db():
    db = Database()
    db.create_table("students", {"name": str, "age": int})
    return db


def test_add_and_select(db):
    ui = FakeUI(["1", "1", "Аня", "20", "2", "1", "", "", "", "0"])
    Menu(db, ui).run()
    assert "Запись добавлена." in ui.outputs
    assert any("Аня" in line for line in ui.outputs)


def test_select_with_filter(db):
    db.get_table("students").insert({"name": "Аня", "age": 20})
    db.get_table("students").insert({"name": "Боря", "age": 22})
    ui = FakeUI(["2", "1", "", "22", "", "", "0"])
    Menu(db, ui).run()
    shown = [line for line in ui.outputs if "Боря" in line]
    not_shown = [line for line in ui.outputs if "Аня" in line]
    assert shown and not not_shown


def test_select_sorted(db):
    t = db.get_table("students")
    t.insert({"name": "Боря", "age": 22})
    t.insert({"name": "Аня", "age": 20})
    ui = FakeUI(["2", "1", "", "", "age", "2", "0"])
    Menu(db, ui).run()
    ages = [line.split("age: ")[1] for line in ui.outputs if "age: " in line]
    assert ages == ["22", "20"]


def test_update(db):
    db.get_table("students").insert({"name": "Аня", "age": 20})
    ui = FakeUI(["3", "1", "1", "Аня", "25", "0"])
    Menu(db, ui).run()
    assert "Запись обновлена." in ui.outputs
    assert db.get_table("students").get(1)["age"] == 25


def test_delete(db):
    db.get_table("students").insert({"name": "Аня", "age": 20})
    ui = FakeUI(["4", "1", "1", "0"])
    Menu(db, ui).run()
    assert "Запись удалена." in ui.outputs
    assert db.get_table("students").select() == []


def test_create_table(db):
    ui = FakeUI(["5", "teachers", "name", "str", "", "0"])
    Menu(db, ui).run()
    assert "teachers" in db.table_names()


def test_delete_missing_record_shows_error(db):
    ui = FakeUI(["4", "1", "999", "0"])
    Menu(db, ui).run()
    assert any("не найдена" in line for line in ui.outputs)


def test_unknown_command(db):
    ui = FakeUI(["42", "0"])
    Menu(db, ui).run()
    assert any("Неизвестная команда" in line for line in ui.outputs)


def test_exit_command_stops_loop(db):
    ui = FakeUI(["6", "0"])
    Menu(db, ui).run()
