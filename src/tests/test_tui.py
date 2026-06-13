import unittest
from unittest.mock import patch
from io import StringIO
from src.db.tui import Tui


class TestTUI(unittest.TestCase):

    def setUp(self):
        self.app = Tui()

    def _run_with_input(self, method, inputs):
        with patch('builtins.input', side_effect=inputs):
            with patch('sys.stdout', new_callable=StringIO) as out:
                method()
                return out.getvalue()

    def test_add_success(self):
        output = self._run_with_input(self.app._add, ["1", "John", "Doe", "20", "M"])
        self.assertIn("Запись добавлена", output)
        self.assertEqual(len(self.app.db.select()), 1)

    def test_add_negative_age(self):
        output = self._run_with_input(self.app._add, ["1", "John", "Doe", "-5", "M"])
        self.assertIn("Ошибка", output)
        self.assertEqual(len(self.app.db.select()), 0)

    def test_add_duplicate_id(self):
        self.app.db.add(1, "John", "Doe", 20, "M")
        output = self._run_with_input(self.app._add, ["1", "Jane", "Smith", "22", "F"])
        self.assertIn("Ошибка", output)
        self.assertEqual(len(self.app.db.select()), 1)

    def test_show_all_empty(self):
        output = self._run_with_input(self.app._show_all, [])
        self.assertIn("Записи не найдены", output)

    def test_show_all_with_records(self):
        self.app.db.add(1, "John", "Doe", 20, "M")
        output = self._run_with_input(self.app._show_all, [])
        self.assertIn("John", output)

    def test_find_found(self):
        self.app.db.add(1, "John", "Doe", 20, "M")
        output = self._run_with_input(self.app._find, ["1", "", "", "", ""])
        self.assertIn("John", output)

    def test_find_not_found(self):
        output = self._run_with_input(self.app._find, ["999", "", "", "", ""])
        self.assertIn("Записи не найдены", output)

    def test_update_success(self):
        self.app.db.add(1, "John", "Doe", 20, "M")
        output = self._run_with_input(self.app._update,
            ["1", "", "", "", "", "Johnny", "", "", ""])
        self.assertIn("Обновлённые записи", output)
        self.assertEqual(self.app.db.select()[0][1], "Johnny")

    def test_update_error(self):
        output = self._run_with_input(self.app._update,
            ["999", "", "", "", "", "Johnny", "", "", ""])
        self.assertIn("Ошибка", output)

    def test_delete_success(self):
        self.app.db.add(1, "John", "Doe", 20, "M")
        output = self._run_with_input(self.app._delete, ["1", "", "", "", ""])
        self.assertIn("Удалённые записи", output)
        self.assertEqual(len(self.app.db.select()), 0)

    def test_delete_error(self):
        output = self._run_with_input(self.app._delete, ["999", "", "", "", ""])
        self.assertIn("Ошибка", output)

    def test_run_exit(self):
        output = self._run_with_input(self.app.run, ["0"])
        self.assertIn("Выход из программы", output)

    def test_run_unknown_command(self):
        output = self._run_with_input(self.app.run, ["9", "0"])
        self.assertIn("Неизвестная команда", output)

    def test_run_full_flow(self):
        inputs = [
            "1", "1", "John", "Doe", "20", "M",
            "2",
            "3", "1", "", "", "", "",
            "4", "1", "", "", "", "", "Johnny", "", "21", "",
            "5", "1", "", "", "", "",
            "0",
        ]
        output = self._run_with_input(self.app.run, inputs)
        self.assertIn("Выход из программы", output)


if __name__ == '__main__':
    unittest.main()
