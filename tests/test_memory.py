import unittest
import json
import csv
import tempfile
from pathlib import Path

from src.db.backend.errors import TableValueError
from src.db.backend.memory import StudentDBJSON, StudentDBCSV, StudentDB


class TestStudentDB(unittest.TestCase):

    def setUp(self):
        self.db = StudentDB()
        self.assertIsInstance(self.db, StudentDB)

    def test_add(self):
        cases = [
            (1, "John", "Doe", 20, "M"),
            (2, "Jane", "Smith", 22, "F"),
            (3, "Alice", "Johnson", 19, "F"),
            (4, "Bob", "Brown", 21, "M"),
            (5, "Charlie", "Davis", 18, "M"),
            (6, "Eve", "Miller", 23, "F"),
            (7, "Frank", "Wilson", 20, "M"),
            (8, "Grace", "Moore", 22, "F"),
            (9, "Hank", "Taylor", 19, "M"),
            (10, "Ivy", "Anderson", 21, "F"),
            (11, "Jack", "Thomas", 18, "M"),
            (12, "Kathy", "Jackson", 23, "F"),
        ]

        for test_data in cases:
            with self.subTest(test_data=test_data):
                record = self.db.add(*test_data)
                self.assertEqual(record, test_data)

    def test_add_negative_age(self):
        cases = [
            (1, "John", "Doe", -1, "M"),
            (2, "Jane", "Smith", -5, "F"),
            (3, "Alice", "Johnson", -10, "F"),
        ]
        error_message = "Поле age не может быть отрицательным."

        for test_data in cases:
            with self.subTest(test_data=test_data):
                with self.assertRaises(TableValueError) as context:
                    self.db.add(*test_data)
                self.assertEqual(str(context.exception), error_message)

    def test_add_duplicate_id(self):
        test_data_1 = (1, "John", "Doe", 20, "M")
        test_data_2 = (1, "Jane", "Smith", 22, "F")
        error_message = "Запись с id=1 уже существует."

        self.db.add(*test_data_1)

        with self.assertRaises(TableValueError) as context:
            self.db.add(*test_data_2)
        self.assertEqual(str(context.exception), error_message)

    def test_select(self):
        test_datas = [
            (1, "John", "Doe", 20, "M"),
            (2, "Jane", "Smith", 22, "F"),
            (3, "Alice", "Johnson", 19, "F"),
            (4, "Bob", "Brown", 21, "M"),
            (5, "Charlie", "Davis", 18, "M"),
            (6, "Eve", "Miller", 23, "F"),
            (7, "Frank", "Wilson", 20, "M"),
            (8, "Grace", "Moore", 22, "F"),
            (9, "Hank", "Taylor", 19, "M"),
            (10, "Ivy", "Anderson", 21, "F"),
        ]

        for test_data in test_datas:
            self.db.add(*test_data)

        cases = [
            {
                "name": "Выбор без фильтров",
                "filters": {},
                "expected": test_datas,
            },
            {
                "name": "Фильтр по ID",
                "filters": {"student_id": 1},
                "expected": [test_datas[0]],
            },
            {
                "name": "Фильтр по имени",
                "filters": {"first_name": "Jane"},
                "expected": [test_datas[1]],
            },
            {
                "name": "Фильтр по фамилии",
                "filters": {"second_name": "Johnson"},
                "expected": [test_datas[2]],
            },
            {
                "name": "Фильтр по возрасту",
                "filters": {"age": 20},
                "expected": [test_datas[0], test_datas[6]],
            },
            {
                "name": "Фильтр по полу",
                "filters": {"sex": "F"},
                "expected": [
                    test_datas[1],
                    test_datas[2],
                    test_datas[5],
                    test_datas[7],
                    test_datas[9],
                ],
            },
        ]

        for case in cases:
            with self.subTest(
                case=case["name"], filters=case["filters"], expected=case["expected"]
            ):
                records = self.db.select(**case["filters"])
                self.assertEqual(records, case["expected"])

    def test_update(self):
        self.db.add(1, "John", "Doe", 20, "M")
        self.db.add(2, "Jane", "Smith", 22, "F")

        updated = self.db.update(student_id=1, new_first_name="Johnny", new_age=21)
        expected = [(1, "Johnny", "Doe", 21, "M")]
        self.assertEqual(updated, expected)

        all_records = self.db.select()
        self.assertEqual(all_records, [(1, "Johnny", "Doe", 21, "M"), (2, "Jane", "Smith", 22, "F")])

    def test_update_no_match(self):
        self.db.add(1, "John", "Doe", 20, "M")

        with self.assertRaises(TableValueError) as context:
            self.db.update(student_id=999, new_first_name="Bob")
        self.assertEqual(str(context.exception), "Нет записей, соответствующих фильтру.")

    def test_delete(self):
        self.db.add(1, "John", "Doe", 20, "M")
        self.db.add(2, "Jane", "Smith", 22, "F")
        self.db.add(3, "Bob", "Brown", 20, "M")

        deleted = self.db.delete(age=20)
        expected = [(1, "John", "Doe", 20, "M"), (3, "Bob", "Brown", 20, "M")]
        self.assertEqual(deleted, expected)

        remaining = self.db.select()
        self.assertEqual(remaining, [(2, "Jane", "Smith", 22, "F")])

    def test_delete_no_filters(self):
        self.db.add(1, "John", "Doe", 20, "M")

        result = self.db.delete()
        self.assertIsNone(result)

    def test_delete_no_match(self):
        self.db.add(1, "John", "Doe", 20, "M")

        with self.assertRaises(TableValueError) as context:
            self.db.delete(student_id=999)
        self.assertEqual(str(context.exception), "Нет записей, соответствующих фильтру.")


class TestStudentDBJSON(unittest.TestCase):

    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.test_file = Path(self.temp_dir.name) / "test_students.json"
        self.db = StudentDBJSON(str(self.test_file))

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_load_from_existing_file(self):
        test_data = {
            "students": [
                [1, "John", "Doe", 20, "M"],
                [2, "Jane", "Smith", 22, "F"]
            ],
            "header" : ['student_id', 'first_name', 'second_name', 'age', 'sex']
        }
        with open(self.test_file, 'w', encoding='utf-8') as f:
            json.dump(test_data, f)

        db = StudentDBJSON(str(self.test_file))
        records = db.select()
        self.assertEqual(len(records), 2)
        self.assertEqual(records[0], (1, "John", "Doe", 20, "M"))
        self.assertEqual(records[1], (2, "Jane", "Smith", 22, "F"))

    def test_save_after_add(self):
        self.db.add(1, "John", "Doe", 20, "M")
        self.db._save_if_needed()

        with open(self.test_file, 'r', encoding='utf-8') as f:
            data = json.load(f)

        self.assertEqual(data["students"], [[1, "John", "Doe", 20, "M"]])


    def test_save_after_delete(self):
        self.db.add(1, "John", "Doe", 20, "M")
        self.db.add(2, "Jane", "Smith", 22, "F")
        self.db._save_if_needed()

        self.db.delete(student_id=1)
        self.db._save_if_needed()

        with open(self.test_file, 'r', encoding='utf-8') as f:
            data = json.load(f)

        self.assertEqual(data["students"], [[2, "Jane", "Smith", 22, "F"]])


class TestStudentDBCSV(unittest.TestCase):

    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.test_file = Path(self.temp_dir.name) / "test_students.csv"
        self.db = StudentDBCSV(str(self.test_file))

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_load_from_existing_file(self):
        with open(self.test_file, 'w', encoding='utf-8', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['student_id', 'first_name', 'second_name', 'age', 'sex'])
            writer.writerow([1, "John", "Doe", 20, "M"])
            writer.writerow([2, "Jane", "Smith", 22, "F"])

        db = StudentDBCSV(str(self.test_file))
        records = db.select()
        self.assertEqual(len(records), 2)
        self.assertEqual(records[0], (1, "John", "Doe", 20, "M"))
        self.assertEqual(records[1], (2, "Jane", "Smith", 22, "F"))

    def test_load_from_file_without_header(self):
        with open(self.test_file, 'w', encoding='utf-8', newline='') as f:
            writer = csv.writer(f)
            writer.writerow([1, "John", "Doe", 20, "M"])

        db = StudentDBCSV(str(self.test_file))
        self.assertEqual(len(db.select()), 0)  # Должен пропустить (нет заголовка)

    def test_load_from_corrupted_csv(self):
        with open(self.test_file, 'w', encoding='utf-8') as f:
            f.write("not,a,csv,file\n")

        db = StudentDBCSV(str(self.test_file))
        self.assertEqual(len(db.select()), 0)

    def test_save_after_add(self):
        self.db.add(1, "John", "Doe", 20, "M")
        self.db._save_if_needed()

        with open(self.test_file, 'r', encoding='utf-8', newline='') as f:
            reader = csv.reader(f)
            rows = list(reader)

        self.assertEqual(rows[0], ['student_id', 'first_name', 'second_name', 'age', 'sex'])
        self.assertEqual(rows[1], ['1', 'John', 'Doe', '20', 'M'])

    def test_save_after_multiple_operations(self):
        self.db.add(1, "John", "Doe", 20, "M")
        self.db.add(2, "Jane", "Smith", 22, "F")
        self.db._save_if_needed()

        self.db.update(student_id=1, new_age=21)
        self.db.delete(student_id=2)
        self.db._save_if_needed()

        with open(self.test_file, 'r', encoding='utf-8', newline='') as f:
            reader = csv.reader(f)
            rows = list(reader)

        self.assertEqual(len(rows), 2)  # Header + 1 record
        self.assertEqual(rows[1], ['1', 'John', 'Doe', '21', 'M'])

    def test_unicode_support(self):
        self.db.add(1, "Иван", "Иванов", 20, "М")
        self.db._save_if_needed()

        with open(self.test_file, 'r', encoding='utf-8', newline='') as f:
            reader = csv.reader(f)
            rows = list(reader)

        self.assertEqual(rows[1], ['1', 'Иван', 'Иванов', '20', 'М'])

        db2 = StudentDBCSV(str(self.test_file))
        records = db2.select()
        self.assertEqual(records[0][1], "Иван")
        self.assertEqual(records[0][2], "Иванов")

    def test_whitespace_trimming(self):
        """Тест: обрезка пробелов при загрузке"""
        with open(self.test_file, 'w', encoding='utf-8', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['student_id', 'first_name', 'second_name', 'age', 'sex'])
            writer.writerow(['1', '  John  ', '  Doe  ', '20', '  M  '])

        db = StudentDBCSV(str(self.test_file))
        records = db.select()
        self.assertEqual(records[0][1], "John")
        self.assertEqual(records[0][2], "Doe")
        self.assertEqual(records[0][4], "M")


class TestExportFunctionality(unittest.TestCase):

    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.db = StudentDBJSON(str(Path(self.temp_dir.name) / "source.json"))

        self.db.add(1, "John", "Doe", 20, "M")
        self.db.add(2, "Jane", "Smith", 22, "F")
        self.db.add(3, "Bob", "Brown", 21, "M")

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_export_to_json_from_memory(self):
        export_file = Path(self.temp_dir.name) / "export.json"

        temp_db = StudentDBJSON(str(export_file))
        temp_db._students = self.db._students.copy()
        temp_db._save_if_needed()

        self.assertTrue(export_file.exists())
        with open(export_file, 'r', encoding='utf-8') as f:
            data = json.load(f)

        self.assertEqual(len(data["students"]), 3)

    def test_export_to_csv_from_memory(self):
        export_file = Path(self.temp_dir.name) / "export.csv"

        temp_db = StudentDBCSV(str(export_file))
        temp_db._students = self.db._students.copy()
        temp_db._save_if_needed()

        self.assertTrue(export_file.exists())
        with open(export_file, 'r', encoding='utf-8', newline='') as f:
            reader = csv.reader(f)
            rows = list(reader)

        self.assertEqual(len(rows), 4)  # Header + 3 records
        self.assertEqual(rows[1][0], '1')
        self.assertEqual(rows[2][0], '2')
        self.assertEqual(rows[3][0], '3')

    def test_export_empty_database(self):
        empty_db = StudentDBJSON(str(Path(self.temp_dir.name) / "empty.json"))
        export_file = Path(self.temp_dir.name) / "empty_export.csv"

        temp_db = StudentDBCSV(str(export_file))
        temp_db._students = empty_db._students.copy()
        temp_db._save_if_needed()

        with open(export_file, 'r', encoding='utf-8', newline='') as f:
            reader = csv.reader(f)
            rows = list(reader)

        self.assertEqual(len(rows), 1)  # Only header
        self.assertEqual(rows[0][0], 'student_id')

    def test_export_preserves_data_integrity(self):
        """Тест: экспорт сохраняет целостность данных"""
        json_export = Path(self.temp_dir.name) / "export.json"
        csv_export = Path(self.temp_dir.name) / "export.csv"

        # Экспорт в JSON
        temp_json = StudentDBJSON(str(json_export))
        temp_json._students = self.db._students.copy()
        temp_json._save_if_needed()

        # Экспорт в CSV
        temp_csv = StudentDBCSV(str(csv_export))
        temp_csv._students = self.db._students.copy()
        temp_csv._save_if_needed()

        with open(json_export, 'r', encoding='utf-8') as f:
            json_data = json.load(f)

        with open(csv_export, 'r', encoding='utf-8', newline='') as f:
            reader = csv.reader(f)
            next(reader)
            csv_data = list(reader)

        self.assertEqual(len(json_data["students"]), 3)
        self.assertEqual(len(csv_data), 3)

        for i, record in enumerate(json_data["students"]):
            self.assertEqual(str(record[0]), csv_data[i][0])
            self.assertEqual(record[1], csv_data[i][1])
            self.assertEqual(record[2], csv_data[i][2])
            self.assertEqual(str(record[3]), csv_data[i][3])
            self.assertEqual(record[4], csv_data[i][4])


if __name__ == '__main__':
    unittest.main()