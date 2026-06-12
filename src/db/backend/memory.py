import csv
import json
from pathlib import Path

from src.db.backend.errors import TableValueError, TableFilterError, TableIncorrectJsonError, TableFileError, \
    TableIncorrectCSVError

type StudentRecord = tuple[int, str, str, int, str]

class StudentDB:

    def __init__(self) -> None:
        self._students: list[StudentRecord] = []

    def add(self, student_id: int, first_name: str, second_name: str,
            age: int, sex: str) -> StudentRecord:
        if age < 0:
            raise TableValueError("Поле age не может быть отрицательным.")
        if any(rec[0] == student_id for rec in self._students):
            raise TableValueError(f"Запись с id={student_id} уже существует.")
        if (first_name is None or second_name is None
                or first_name.strip() == "" or second_name.strip() == ""):
            raise TableValueError('поля не могут быть пустыми')

        new_rec: StudentRecord = (
            student_id,
            first_name.strip(),
            second_name.strip(),
            age,
            sex.strip(),
        )
        self._students.append(new_rec)
        return new_rec

    def select(self,
               student_id: int | None = None,
               first_name: str | None = None,
               second_name: str | None = None,
               age: int | None = None,
               sex: str | None = None,
               ) -> list[StudentRecord]:
        if all(p is None for p in (student_id, first_name, second_name, age, sex)):
            return self._students.copy()

        result: list[StudentRecord] = []
        for rec in self._students:
            if student_id is not None and rec[0] != student_id:
                continue
            if first_name is not None and rec[1] != first_name:
                continue
            if second_name is not None and rec[2] != second_name:
                continue
            if age is not None and rec[3] != age:
                continue
            if sex is not None and rec[4] != sex:
                continue
            result.append(rec)
        return result

    def update(self,
               student_id: int | None = None,
               first_name: str | None = None,
               second_name: str | None = None,
               age: int | None = None,
               sex: str | None = None,
               new_first_name: str | None = None,
               new_second_name: str | None = None,
               new_age: int | None = None,
               new_sex: str | None = None,
               ) -> list[StudentRecord]:
        updated = []

        for i, rec in enumerate(self._students):
            if student_id is not None and rec[0] != student_id:
                continue
            if first_name is not None and rec[1] != first_name:
                continue
            if second_name is not None and rec[2] != second_name:
                continue
            if age is not None and rec[3] != age:
                continue
            if sex is not None and rec[4] != sex:
                continue


            if new_age <= 0:
                raise TableValueError('Возраст не может быть отрицательным')
            new_rec = (
                rec[0],
                new_first_name if new_first_name is not None else rec[1],
                new_second_name if new_second_name is not None else rec[2],
                new_age if new_age is not None else rec[3],
                new_sex if new_sex is not None else rec[4],
            )
            self._students[i] = new_rec
            updated.append(new_rec)

        if not updated:
            raise TableValueError("Нет записей, соответствующих фильтру.")
        return updated

    def delete(self,
               student_id: int | None = None,
               first_name: str | None = None,
               second_name: str | None = None,
               age: int | None = None,
               sex: str | None = None,
               ) -> list[StudentRecord] | None:

        if all([col is None for col in (student_id, first_name, second_name, age, sex)]):
            return None

        deleted = []
        i = 0
        while i < len(self._students):
            rec = self._students[i]
            if student_id is not None and rec[0] != student_id:
                i += 1
                continue
            if first_name is not None and rec[1] != first_name:
                i += 1
                continue
            if second_name is not None and rec[2] != second_name:
                i += 1
                continue
            if age is not None and rec[3] != age:
                i += 1
                continue
            if sex is not None and rec[4] != sex:
                i += 1
                continue

            deleted.append(self._students.pop(i))
        if not deleted:
            raise TableValueError("Нет записей, соответствующих фильтру.")
        return deleted


class StudentDBJSON(StudentDB):
    def __init__(self, filename: str = "students.json") -> None:
        super().__init__()
        self._filepath = Path(filename)
        self._load_from_file()

    def _load_from_file(self) -> None:
        if self._filepath.exists():
            try:
                with open(self._filepath, 'r', encoding='utf-8') as f:
                    data = json.load(f)

                self._students.clear()
                if data == {}:
                    raise TableIncorrectJsonError('Файл пуст')
                if data['header'] != ['student_id', 'first_name', 'second_name', 'age', 'sex']:
                    raise TableIncorrectJsonError('Неверный заголовок таблицы')

                for record in data.get("students", []):
                    student: StudentRecord = (
                        record[0],
                        record[1],
                        record[2],
                        record[3],
                        record[4],
                    )
                    self._students.append(student)

            except (json.JSONDecodeError, FileNotFoundError) as e:
                raise TableFileError(f"Ошибка при чтении JSON файла: {e}")
            except (TypeError, ValueError, IndexError) as e:
                raise TableIncorrectJsonError(f"Ошибка при разборе данных: {e}")

    def _save_if_needed(self) -> None:
        data = {
            "students": [
                list(student) for student in self._students],
            "header" : ['student_id', 'first_name', 'second_name', 'age', 'sex']

        }

        self._filepath.parent.mkdir(parents=True, exist_ok=True)

        with open(self._filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def add(self, *args, **kwargs):
        data = super().add(*args, **kwargs)
        self._save_if_needed()
        return data

    def update(self, *args, **kwargs):
        data = super().update(*args, **kwargs)
        self._save_if_needed()
        return data

    def delete(self, *args, **kwargs):
        data = super().delete(*args, **kwargs)
        self._save_if_needed()
        return data



class StudentDBCSV(StudentDB):
    def __init__(self, filename: str = "students.csv") -> None:
        super().__init__()
        self._filepath = Path(filename)
        self._load_from_file()

    def _load_from_file(self) -> None:
        if self._filepath.exists():
            try:
                with open(self._filepath, 'r', encoding='utf-8', newline='') as f:
                    reader = csv.reader(f)

                    header = next(reader, None)
                    if header is None:
                        raise TableIncorrectCSVError("CSV файл пуст")

                    self._students.clear()

                    for row in reader:
                        if len(row) >= 5:
                            student: StudentRecord = (
                                int(row[0]),
                                row[1].strip(),
                                row[2].strip(),
                                int(row[3]),
                                row[4].strip(),
                            )
                            self._students.append(student)

            except (ValueError, csv.Error) as e:
                TableIncorrectCSVError(f"Ошибка при чтении CSV файла: {e}")

    def _save_if_needed(self) -> None:
        self._filepath.parent.mkdir(parents=True, exist_ok=True)

        with open(self._filepath, 'w', encoding='utf-8', newline='') as f:
            writer = csv.writer(f)

            writer.writerow(['student_id', 'first_name', 'second_name', 'age', 'sex'])

            for student in self._students:
                writer.writerow(student)

    def add(self, *args, **kwargs):
        data = super().add(*args, **kwargs)
        self._save_if_needed()
        return data

    def update(self, *args, **kwargs):
        data = super().update(*args, **kwargs)
        self._save_if_needed()
        return data

    def delete(self, *args, **kwargs):
        data = super().delete(*args, **kwargs)
        self._save_if_needed()
        return data