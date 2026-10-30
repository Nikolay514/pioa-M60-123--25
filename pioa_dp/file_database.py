import json
from pathlib import Path

from database import Database, Table
from exceptions import StorageError
from validators import validate_record

_TYPE_TO_NAME = {str: "str", int: "int"}
_NAME_TO_TYPE = {name: ftype for ftype, name in _TYPE_TO_NAME.items()}


class FileTable(Table):
    def __init__(self, name: str, schema: dict, path):
        self._path = Path(path)
        super().__init__(name, schema)
        self._load()

    def _load(self) -> None:
        if not self._path.exists():
            self._save()

            return

        data = self._read_json()
        try:
            stored_schema = {
                field: _NAME_TO_TYPE[type_name]
                for field, type_name in data["schema"].items()
            }


            records = data["records"]
        except (KeyError, TypeError, AttributeError) as err:
            raise StorageError(
                f"Файл '{self._path.name}' поврежден или имеет неверный формат"
            ) from err

        if stored_schema != self.schema:
            raise StorageError(
                f"Схема в файле '{self._path.name}' не совпадает с заданной"
            )

        for raw in records:
            if not isinstance(raw, dict) or "id" not in raw:
                raise StorageError(
                    f"Поврежденная запись в файле '{self._path.name}'"
                )
            record_id = raw["id"]
            if not isinstance(record_id, int) or record_id in self._records:
                raise StorageError(
                    f"Некорректный id записи в файле '{self._path.name}'"
                )
            try:
                clean = validate_record(
                    self.schema, {f: raw.get(f) for f in self.schema}
                )
            except Exception as err:
                raise StorageError(
                    f"Некорректные данные в файле '{self._path.name}': {err}"
                ) from err
            self._records[record_id] = {"id": record_id, **clean}
            self._next_id = max(self._next_id, record_id + 1)

    def _read_json(self) -> dict:
        try:
            text = self._path.read_text(encoding="utf-8")
            return json.loads(text)
        except OSError as err:
            raise StorageError(f"Не удалось прочитать файл: {err}") from err
        except json.JSONDecodeError as err:
            raise StorageError(
                f"Файл '{self._path.name}' поврежден (некорректный JSON)"
            ) from err

    def _save(self) -> None:
        data = {
            "schema": {
                field: _TYPE_TO_NAME[ftype] for field, ftype in self.schema.items()
            },
            "records": list(self._records.values()),
        }
        try:
            self._path.write_text(
                json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8"
            )
        except OSError as err:
            raise StorageError(f"Не удалось сохранить таблицу: {err}") from err

    def insert(self, record: dict) -> dict:
        result = super().insert(record)
        self._save()
        return result

    def update(self, record_id: int, changes: dict) -> dict:
        result = super().update(record_id, changes)
        self._save()
        return result

    def delete(self, record_id: int) -> None:
        super().delete(record_id)
        self._save()


class FileDatabase(Database):
    def __init__(self, directory):
        self._dir = Path(directory)
        try:
            self._dir.mkdir(parents=True, exist_ok=True)
        except OSError as err:
            raise StorageError(f"Не удалось создать каталог данных: {err}") from err

        super().__init__()
        for file in sorted(self._dir.glob("*.json")):
            schema = self._read_schema(file)
            self._tables[file.stem] = FileTable(file.stem, schema, file)

    def _read_schema(self, file: Path) -> dict:
        try:
            text = file.read_text(encoding="utf-8")
            data = json.loads(text)
            return {
                field: _NAME_TO_TYPE[type_name]
                for field, type_name in data["schema"].items()
            }
        except OSError as err:
            raise StorageError(f"Не удалось прочитать файл: {err}") from err
        except (json.JSONDecodeError, KeyError, TypeError, AttributeError) as err:
            raise StorageError(
                f"Файл '{file.name}' поврежден или имеет неверный формат"
            ) from err

    def _make_table(self, name: str, schema: dict) -> Table:
        return FileTable(name, schema, self._dir / f"{name}.json")
