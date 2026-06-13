type StudentRecord = tuple[int, str, str, int, str]

class StudentDB:

    def __init__(self) -> None:
        self._students: list[StudentRecord] = []

    def add(self, student_id: int, first_name: str, second_name: str,
            age: int, sex: str) -> StudentRecord:
        if age < 0:
            raise ValueError("Поле age не может быть отрицательным.")
        if any(rec[0] == student_id for rec in self._students):
            raise ValueError(f"Запись с id={student_id} уже существует.")

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
            raise ValueError("Нет записей, соответствующих фильтру.")
        return updated

    def delete(self,
               student_id: int | None = None,
               first_name: str | None = None,
               second_name: str | None = None,
               age: int | None = None,
               sex: str | None = None,
               ) -> list[StudentRecord] | None:

        if not any((student_id, first_name, second_name, age, sex)):Expand commentComment on line R97Resolved
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
            raise ValueError("Нет записей, соответствующих фильтру.")
        return deleted
