import unittest
from unittest.mock import patch, MagicMock
from io import StringIO

from src.db.backend.memory import StudentDB, StudentDBJSON, StudentDBCSV
from src.db.tui import Tui


class TestTUI(unittest.TestCase):

    def setUp(self):
        with patch('builtins.input', side_effect=['1']):
            self.app = Tui()

    def _run_with_input(self, method, inputs):
        with patch('builtins.input', side_effect=inputs):
            with patch('sys.stdout', new_callable=StringIO) as out:
                method()
                return out.getvalue()

    def test_add_success(self):
        output = self._run_with_input(
            self.app._add,
            ["1", "John", "Doe", "20", "M"]
        )
        self.assertIn("Запись добавлена", output)
        self.assertEqual(len(self.app.db.select()), 1)


    def test_show_all_with_records(self):
        self.app.db.add(1, "John", "Doe", 20, "M")
        output = self._run_with_input(self.app._show_all, [])
        self.assertIn("John", output)

    def test_find_found(self):
        self.app.db.add(1, "John", "Doe", 20, "M")
        output = self._run_with_input(
            self.app._find,
            ["1", "", "", "", ""]
        )
        self.assertIn("John", output)

    def test_find_not_found(self):
        output = self._run_with_input(
            self.app._find,
            ["999", "", "", "", ""]
        )
        self.assertIn("Записи не найдены", output)

    def test_update_error(self):
        output = self._run_with_input(
            self.app._update,
            ["999", "", "", "", "", "Johnny", "", "", ""]
        )
        self.assertIn("Записи по заданному фильтру не найдены", output)

    def test_update_cancel(self):
        self.app.db.add(1, "John", "Doe", 20, "M")
        output = self._run_with_input(
            self.app._update,
            ["1", "", "", "", "", "Johnny", "", "", "", "n"]
        )
        self.assertIn("Обновление отменено", output)
        self.assertEqual(self.app.db.select()[0][1], "John")

    def test_delete_success(self):
        self.app.db.add(1, "John", "Doe", 20, "M")
        output = self._run_with_input(
            self.app._delete,
            ["1", "", "", "", "", "y"]
        )
        self.assertIn("Удалённые записи", output)
        self.assertEqual(len(self.app.db.select()), 0)

    def test_delete_error(self):
        output = self._run_with_input(
            self.app._delete,
            ["999", "", "", "", ""]
        )
        self.assertIn("Записи по заданному фильтру не найдены", output)

    def test_delete_cancel(self):
        self.app.db.add(1, "John", "Doe", 20, "M")
        output = self._run_with_input(
            self.app._delete,
            ["1", "", "", "", "", "n"]
        )
        self.assertIn("Удаление отменено", output)
        self.assertEqual(len(self.app.db.select()), 1)

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
            "4", "1", "", "", "", "",
            "y",
            "Johnny", "", "21", "",
            "n",
            "5", "1", "", "", "", "",
            "y",

            "0",
        ]
        output = self._run_with_input(self.app.run, inputs)
        self.assertIn("Выход из программы", output)



    def test_export_empty_database(self):
        output = self._run_with_input(
            self.app._export_data,
            ["1", "export.json"]
        )
        self.assertIn("База данных пуста", output)

    def test_export_cancel(self):
        self.app.db.add(1, "John", "Doe", 20, "M")
        output = self._run_with_input(
            self.app._export_data,
            ["0"]
        )
        self.assertIn("Экспорт отменён", output)

    def test_export_empty_filename(self):
        """Тест экспорта с пустым именем файла"""
        self.app.db.add(1, "John", "Doe", 20, "M")
        output = self._run_with_input(
            self.app._export_data,
            ["1", ""]
        )
        self.assertIn("Имя файла не может быть пустым", output)

    def test_init_database_memory(self):
        with patch('builtins.input', side_effect=['1']):
            with patch('sys.stdout', new_callable=StringIO) as out:
                app = Tui()
                output = out.getvalue()
                self.assertIn("База данных создана в памяти", output)
                self.assertIsInstance(app.db, StudentDB)

    def test_init_database_csv(self):
        with patch('builtins.input', side_effect=['3', 'test.csv']):
            with patch('sys.stdout', new_callable=StringIO) as out:
                with patch('pathlib.Path.absolute', return_value='/abs/path/test.csv'):
                    app = Tui()
                    output = out.getvalue()
                    self.assertIn("База данных подключена к файлу", output)
                    self.assertIsInstance(app.db, StudentDBCSV)

    def test_init_database_invalid_choice(self):
        with patch('builtins.input', side_effect=['4', '1']):
            with patch('sys.stdout', new_callable=StringIO) as out:
                app = Tui()
                output = out.getvalue()
                self.assertIn("Ошибка: выберите 1, 2 или 3", output)



if __name__ == '__main__':
    unittest.main()