import json
from pathlib import Path
from src.db.backend.errors import TableIncorrectJsonError, TableFileError

class JSONBackend:
    def __init__(self, filepath: str):
        self.filepath = Path(filepath)

    def load(self):
        if not self.filepath.exists():
            # Возвращаем пустую структуру
            return {"header": ['student_id', 'first_name', 'second_name', 'age', 'sex'], "students": []}
        try:
            with open(self.filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
            self._validate(data)
            return data
        except (json.JSONDecodeError, FileNotFoundError) as e:
            raise TableFileError(f"Ошибка при чтении JSON файла: {e}")

    def save(self, students: list):
        data = {
            "header": ['student_id', 'first_name', 'second_name', 'age', 'sex'],
            "students": [list(student) for student in students]
        }
        self.filepath.parent.mkdir(parents=True, exist_ok=True)
        with open(self.filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def _validate(self, data):
        if not data:
            raise TableIncorrectJsonError('Файл пуст')
        if 'header' not in data:
            raise TableIncorrectJsonError('Отсутствует ключ "header"')
        if data['header'] != ['student_id', 'first_name', 'second_name', 'age', 'sex']:
            raise TableIncorrectJsonError('Неверный заголовок таблицы')
