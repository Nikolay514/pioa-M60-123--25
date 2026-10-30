from exceptions import (
    RecordNotFoundError,
    TableNotFoundError,
    ValidationError,
)
from validators import validate_record


class Table:
    def __init__(self, name: str, schema: dict):
        self.name = name
        self.schema = dict(schema)
        self._records: dict[int, dict] = {}
        self._next_id = 1

    def insert(self, record: dict) -> dict:
        clean = validate_record(self.schema, record)
        record_id = self._next_id
        self._next_id += 1
        self._records[record_id] = {"id": record_id, **clean}
        return self._records[record_id]

    def get(self, record_id: int) -> dict:
        if record_id not in self._records:
            raise RecordNotFoundError(
                f"Запись с id={record_id} не найдена в таблице '{self.name}'"
            )
        return self._records[record_id]

    def select(
        self,
        filters: dict | None = None,
        sort_field: str | None = None,
        reverse: bool = False,
    ) -> list[dict]:
        if not filters:
            result = list(self._records.values())
        else:
            unknown = set(filters) - set(self.schema)
            if unknown:
                raise ValidationError(
                    f"Неизвестные поля для фильтрации: {', '.join(unknown)}"
                )
            result = [
                rec for rec in self._records.values()
                if all(rec.get(f) == v for f, v in filters.items())
            ]

        if sort_field is not None:
            if sort_field not in self.schema and sort_field != "id":
                raise ValidationError(
                    f"Поле '{sort_field}' не существует, сортировать не по чему"
                )
            result.sort(key=lambda rec: rec[sort_field], reverse=reverse)

        return result

    def update(self, record_id: int, changes: dict) -> dict:
        if record_id not in self._records:
            raise RecordNotFoundError(
                f"Запись с id={record_id} не найдена в таблице '{self.name}'"
            )
        if not changes:
            raise ValidationError("Пустой набор изменений")

        unknown = set(changes) - set(self.schema)
        if unknown:
            raise ValidationError(f"Неизвестные поля: {', '.join(unknown)}")

        record = self._records[record_id]
        merged = {f: record[f] for f in self.schema}
        merged.update(changes)
        clean = validate_record(self.schema, merged)

        self._records[record_id] = {"id": record_id, **clean}
        return self._records[record_id]

    def delete(self, record_id: int) -> None:
        if record_id not in self._records:
            raise RecordNotFoundError(
                f"Запись с id={record_id} не найдена в таблице '{self.name}'"
            )
        del self._records[record_id]


class Database:
    def __init__(self):
        self._tables: dict[str, Table] = {}

    def _make_table(self, name: str, schema: dict) -> Table:
        return Table(name, schema)

    def create_table(self, name: str, schema: dict) -> Table:
        if name in self._tables:
            raise ValidationError(f"Таблица '{name}' уже существует")
        if not schema:
            raise ValidationError("Схема таблицы не может быть пустой")
        table = self._make_table(name, schema)
        self._tables[name] = table
        return table

    def get_table(self, name: str) -> Table:
        if name not in self._tables:
            raise TableNotFoundError(f"Таблица '{name}' не существует")
        return self._tables[name]

    def table_names(self) -> list[str]:
        return list(self._tables)
