import csv
import json
from pathlib import Path
from src.db.backends.backend_json import JSONBackend
from src.db.backends.backend_csv import CSVBackend
from src.db.backend.errors import TableValueError, TableIncorrectJsonError, TableFileError, \
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

    def _matches_filters(self, rec: StudentRecord, student_id=None, first_name=None, second_name=None, age=None, sex=None) -> bool:
    if student_id is not None and rec[0] != student_id:
        return False
    if first_name is not None and rec[1] != first_name:
        return False
    if second_name is not None and rec[2] != second_name:
        return False
    if age is not None and rec[3] != age:
        return False
    if sex is not None and rec[4] != sex:
        return False
    return True


    def select(self, student_id=None, first_name=None, second_name=None, age=None, sex=None) -> list[StudentRecord]:
    if all(p is None for p in (student_id, first_name, second_name, age, sex)):
        return self._students.copy()

    result: list[StudentRecord] = []
    for rec in self._students:
        if self._matches_filters(rec, student_id, first_name, second_name, age, sex):
            result.append(rec)
    return result
  

    def update(self, student_id=None, first_name=None, second_name=None, age=None, sex=None,
           new_first_name=None, new_second_name=None, new_age=None, new_sex=None) -> list[StudentRecord]:
    updated = []

    for i, rec in enumerate(self._students):
        if not self._matches_filters(rec, student_id, first_name, second_name, age, sex):
            continue

        if new_age is not None and new_age < 0:
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

    def delete(self, student_id=None, first_name=None, second_name=None, age=None, sex=None) -> list[StudentRecord]:
    if all(p is None for p in (student_id, first_name, second_name, age, sex)):
        return None

    deleted = []
    i = 0
    while i < len(self._students):
        rec = self._students[i]
        if self._matches_filters(rec, student_id, first_name, second_name, age, sex):
            deleted.append(self._students.pop(i))
        else:
            i += 1

    if not deleted:
        raise TableValueError("Нет записей, соответствующих фильтру.")
    return deleted



class StudentDBJSON(StudentDB):
    def __init__(self, filename: str = "students.json") -> None:
        super().__init__()
        self._backend = JSONBackend(filename)
        self._load_from_file()

    def _load_from_file(self):
        data = self._backend.load()
        self._students.clear()
        for record in data.get("students", []):
            student: StudentRecord = (
                record[0],
                record[1],
                record[2],
                record[3],
                record[4],
            )
            self._students.append(student)

    def _save_if_needed(self):
        self._backend.save(self._students)

class StudentDBCSV(StudentDB):
    def __init__(self, filename: str = "students.csv") -> None:
        super().__init__()
        self._backend = CSVBackend(filename)
        self._load_from_file()

    def _load_from_file(self):
        self._students.clear()
        students = self._backend.load()
        self._students.extend(students)

    def _save_if_needed(self):
        self._backend.save(self._students)



