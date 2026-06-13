import unittest
from src.db.backend.memory import StudentDB


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
                with self.assertRaises(ValueError) as context:
                    self.db.add(*test_data)
                self.assertEqual(str(context.exception), error_message)

    def test_add_duplicate_id(self):
        test_data_1 = (1, "John", "Doe", 20, "M")
        test_data_2 = (1, "Jane", "Smith", 22, "F")
        error_message = "Запись с id=1 уже существует."

        self.db.add(*test_data_1)

        with self.assertRaises(ValueError) as context:
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

        with self.assertRaises(ValueError) as context:
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

        with self.assertRaises(ValueError) as context:
            self.db.delete(student_id=999)
        self.assertEqual(str(context.exception), "Нет записей, соответствующих фильтру.")
