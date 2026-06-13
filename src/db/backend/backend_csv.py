import csv
from pathlib import Path
from src.db.backend.errors import TableIncorrectCSVError

class CSVBackend:
    def __init__(self, filepath: str):
        self.filepath = Path(filepath)

    def load(self):
        if not self.filepath.exists():
            # Возвращаем пустой список
            return []
        students = []
        try:
            with open(self.filepath, 'r', encoding='utf-8', newline='') as f:
                reader = csv.reader(f)
                header = next(reader, None)
                if header is None:
                    raise TableIncorrectCSVError("CSV файл пуст")
                for row in reader:
                    if len(row) >= 5:
                        student = (
                            int(row[0]),
                            row[1].strip(),
                            row[2].strip(),
                            int(row[3]),
                            row[4].strip(),
                        )
                        students.append(student)
        except (ValueError, csv.Error) as e:
            raise TableIncorrectCSVError(f"Ошибка при чтении CSV файла: {e}")
        return students

    def save(self, students: list):
        self.filepath.parent.mkdir(parents=True, exist_ok=True)
        with open(self.filepath, 'w', encoding='utf-8', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['student_id', 'first_name', 'second_name', 'age', 'sex'])
            for student in students:
                writer.writerow(student)
