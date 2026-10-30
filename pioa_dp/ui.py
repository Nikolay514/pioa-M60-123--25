from database import Database
from exceptions import DatabaseError

STUDENTS_SCHEMA = {"name": str, "group": str, "age": int}
GRADES_SCHEMA = {"student_id": int, "subject": str, "grade": int}


class ConsoleUI:
    def ask(self, prompt: str) -> str:
        return input(prompt)

    def tell(self, message: str) -> None:
        print(message)


class Command:
    title: str = ""

    def __init__(self, db: Database, ui: ConsoleUI):
        self.db = db
        self.ui = ui

    def execute(self) -> None:
        raise NotImplementedError


class ChooseTableMixin:
    def choose_table(self):
        names = self.db.table_names()
        if not names:
            self.ui.tell("Таблиц пока нет. Сначала создайте одну.")
            return None
        for i, name in enumerate(names, start=1):
            self.ui.tell(f"  {i}. {name}")
        choice = self.ui.ask("Номер таблицы: ").strip()
        try:
            return self.db.get_table(names[int(choice) - 1])
        except (ValueError, IndexError):
            self.ui.tell("Ошибка: нет такой таблицы.")
            return None

    def input_record(self, schema: dict) -> dict:
        record = {}
        for field, field_type in schema.items():
            raw = self.ui.ask(f"  {field} ({field_type.__name__}): ").strip()
            if field_type is int:
                record[field] = int(raw)
            else:
                record[field] = raw
        return record


class AddCommand(Command, ChooseTableMixin):
    title = "добавить запись"

    def execute(self) -> None:
        table = self.choose_table()
        if table:
            table.insert(self.input_record(table.schema))
            self.ui.tell("Запись добавлена.")


class SelectCommand(Command, ChooseTableMixin):
    title = "прочитать записи"

    def execute(self) -> None:
        table = self.choose_table()
        if not table:
            return

        filters = {}
        for field, field_type in table.schema.items():
            raw = self.ui.ask(f"  фильтр по {field} (Enter — пропустить): ").strip()
            if raw:
                filters[field] = int(raw) if field_type is int else raw

        sort_field = (
            self.ui.ask("  сортировать по полю (Enter — не сортировать): ").strip()
            or None
        )
        reverse = False
        if sort_field:
            answer = self.ui.ask(
                "  порядок (1 — по возрастанию, 2 — по убыванию): "
            ).strip()
            reverse = answer == "2"

        records = table.select(filters, sort_field=sort_field, reverse=reverse)
        if not records:
            self.ui.tell("  Ничего не найдено.")
        for rec in records:
            self.ui.tell("  " + " | ".join(f"{k}: {v}" for k, v in rec.items()))


class UpdateCommand(Command, ChooseTableMixin):
    title = "обновить запись"

    def execute(self) -> None:
        table = self.choose_table()
        if not table:
            return
        record_id = int(self.ui.ask("id записи: "))
        changes = self.input_record(table.schema)
        table.update(record_id, changes)
        self.ui.tell("Запись обновлена.")


class DeleteCommand(Command, ChooseTableMixin):
    title = "удалить запись"

    def execute(self) -> None:
        table = self.choose_table()
        if not table:
            return
        table.delete(int(self.ui.ask("id записи: ")))
        self.ui.tell("Запись удалена.")


class CreateTableCommand(Command):
    title = "создать таблицу"

    def execute(self) -> None:
        name = self.ui.ask("Имя новой таблицы: ").strip()
        schema = {}
        while True:
            field = self.ui.ask("Поле (Enter — закончить): ").strip()
            if not field:
                break
            ftype = self.ui.ask(f"Тип поля {field} (str/int): ").strip()
            if ftype not in ("str", "int"):
                raise ValueError("Тип может быть только str или int")
            schema[field] = str if ftype == "str" else int
        self.db.create_table(name, schema)
        self.ui.tell(f"Таблица '{name}' создана.")


class ExitCommand(Command):
    title = "выход"

    def __init__(self, db: Database, ui: ConsoleUI):
        super().__init__(db, ui)
        self.done = False

    def execute(self) -> None:
        self.ui.tell("Пока!")
        self.done = True


class Menu:
    def __init__(self, db: Database, ui: ConsoleUI):
        self.ui = ui
        self.commands = [
            AddCommand(db, ui),
            SelectCommand(db, ui),
            UpdateCommand(db, ui),
            DeleteCommand(db, ui),
            CreateTableCommand(db, ui),
            ExitCommand(db, ui),
        ]

    def run(self) -> None:
        while True:
            self.ui.tell("\nМеню:")
            for i, command in enumerate(self.commands, start=1):
                self.ui.tell(f"  {i} — {command.title}")

            try:
                raw = self.ui.ask("> ").strip()
                if not raw:
                    continue
                command = self.commands[int(raw) - 1]
            except (ValueError, IndexError):
                self.ui.tell("Неизвестная команда, попробуйте снова.")
                continue

            try:
                command.execute()
            except DatabaseError as err:
                self.ui.tell(f"Ошибка: {err}")
            except ValueError:
                self.ui.tell("Ошибка: ожидалось целое число.")
            except EOFError:
                self.ui.tell("Прервано.")
                break

            if isinstance(command, ExitCommand) and command.done:
                break
