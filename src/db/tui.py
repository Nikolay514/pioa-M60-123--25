from src.db.backend.memory import StudentDB, StudentDBJSON, StudentDBCSV
from pathlib import Path


class Tui:
    def __init__(self):
        self.db = None
        self._init_database()

    def _init_database(self) -> None:
        print("\n=== Инициализация базы данных ===")
        print("Выберите формат хранения:")
        print("1. В памяти (без сохранения)")
        print("2. JSON файл")
        print("3. CSV файл")

        while True:
            choice = input().strip()
            if choice == "1":
                self.db = StudentDB()
                print("База данных создана в памяти.")
                break
            elif choice == "2":
                filename = input("Имя JSON файла (Enter для 'students.json'): ").strip()
                filename = filename if filename else "students.json"
                self.db = StudentDBJSON(filename)
                print(f"База данных подключена к файлу: {filename}")
                break
            elif choice == "3":
                filename = input("Имя CSV файла (Enter для 'students.csv'): ").strip()
                filename = filename if filename else "students.csv"
                self.db = StudentDBCSV(filename)
                print(f"База данных подключена к файлу: {filename}")
                break
            else:
                print("Ошибка: выберите 1, 2 или 3.")

    def _print_menu(self) -> None:
        print("\n=== База студентов ===")
        if isinstance(self.db, (StudentDBJSON, StudentDBCSV)):
            print(f"Файл: {self.db._filepath.name}")
        print("1. Добавить запись")
        print("2. Показать все записи")
        print("3. Найти записи")
        print("4. Обновить записи")
        print("5. Удалить записи")
        print("6. Экспорт в другой формат")
        print("0. Выход")

    def _read_int(self, prompt: str) -> int:
        while True:
            raw = input(prompt).strip()
            try:
                return int(raw)
            except ValueError:
                print("Ошибка: введите целое число.")

    def _read_optional_int(self, prompt: str) -> int | None:
        while True:
            raw = input(prompt).strip()
            if raw == "":
                return None
            try:
                return int(raw)
            except ValueError:
                print("Ошибка: введите целое число или оставьте поле пустым.")

    def _print_records(self, records: list[tuple[int, str, str, int, str]]) -> None:
        if not records:
            print("Записи не найдены.")
            return

        print("\n" + "=" * 80)
        print(f"{'ID':<6} {'Имя':<20} {'Фамилия':<20} {'Возраст':<10} {'Пол':<10}")
        print("-" * 80)
        for r in records:
            print(f"{r[0]:<6} {r[1]:<20} {r[2]:<20} {r[3]:<10} {r[4]:<10}")
        print(f"Всего записей: {len(records)}")

    def _save_to_file(self) -> None:
        if isinstance(self.db, (StudentDBJSON, StudentDBCSV)):
            try:
                self.db._save_if_needed()
                print(f"Данные успешно сохранены в файл: {self.db._filepath.name}")
            except Exception as e:
                print(f"Ошибка при сохранении: {e}")
        else:
            print("Функция сохранения доступна только для JSON/CSV форматов.")
            print("Экспортируйте данные в файл через опцию '7. Экспорт в другой формат'")

    def _export_data(self) -> None:
        if not self.db.select():
            print("База данных пуста. Нечего экспортировать.")
            return

        print("\nЭкспорт данных:")
        print("1. Экспорт в JSON")
        print("2. Экспорт в CSV")
        print("0. Отмена")

        choice = input("Выберите формат: ").strip()

        if choice not in ["1", "2"]:
            print("Экспорт отменён.")
            return

        filename = input("Введите имя файла для экспорта: ").strip()
        if not filename:
            print("Имя файла не может быть пустым.")
            return

        try:
            if choice == "1":
                temp_db = StudentDBJSON(filename)
            else:
                temp_db = StudentDBCSV(filename)

            for row in self.db.select():
                temp_db.add(*row)

            filepath = Path(filename).absolute()
            print(f"Данные успешно экспортированы в файл: {filepath}")
        except Exception as e:
            print(f"Ошибка при экспорте: {e}")

    def _add(self) -> None:
        print("\nДобавление записи")
        sid = self._read_int("id: ")
        fname = input("first_name: ").strip()
        sname = input("second_name: ").strip()
        age = self._read_int("age: ")
        sex = input("sex: ").strip()

        try:
            rec = self.db.add(sid, fname, sname, age, sex)
            print(f"Запись добавлена: {rec}")

            if isinstance(self.db, (StudentDBJSON, StudentDBCSV)):
                save = input("Сохранить изменения в файл? (y/n): ").strip().lower()
                if save == 'y':
                    self._save_to_file()
        except ValueError as e:
            print(f"Ошибка: {e}")

    def _show_all(self) -> None:
        print("\nСписок записей")
        records = self.db.select()
        if records:
            records_sorted = sorted(records, key=lambda x: x[0])
            self._print_records(records_sorted)
        else:
            print("База данных пуста.")

    def _find(self) -> None:
        print("\nПоиск (Enter – пропустить поле)")
        sid = self._read_optional_int("id: ")
        fname = input("first_name: ").strip() or None
        sname = input("second_name: ").strip() or None
        age = self._read_optional_int("age: ")
        sex = input("sex: ").strip() or None

        records = self.db.select(
            student_id=sid,
            first_name=fname,
            second_name=sname,
            age=age,
            sex=sex
        )
        self._print_records(records)

    def _update(self) -> None:
        print("\nОбновление по фильтру")
        print("Введите условия поиска (Enter – пропустить):")
        sid = self._read_optional_int("id: ")
        fname = input("first_name: ").strip() or None
        sname = input("second_name: ").strip() or None
        age = self._read_optional_int("age: ")
        sex = input("sex: ").strip() or None

        found = self.db.select(
            student_id=sid,
            first_name=fname,
            second_name=sname,
            age=age,
            sex=sex
        )

        if not found:
            print("Записи по заданному фильтру не найдены.")
            return

        print(f"\nНайдено записей для обновления: {len(found)}")
        self._print_records(found)

        confirm = input("\nПродолжить обновление? (y/n): ").strip().lower()
        if confirm != 'y':
            print("Обновление отменено.")
            return

        print("\nНовые значения (Enter – не менять):")
        new_fname = input("first_name: ").strip() or None
        new_sname = input("second_name: ").strip() or None
        new_age = self._read_optional_int("age: ")
        new_sex = input("sex: ").strip() or None

        try:
            updated = self.db.update(
                student_id=sid,
                first_name=fname,
                second_name=sname,
                age=age,
                sex=sex,
                new_first_name=new_fname,
                new_second_name=new_sname,
                new_age=new_age,
                new_sex=new_sex,
            )
            print(f"\nОбновлено записей: {len(updated)}")
            print("Обновлённые записи:")
            self._print_records(updated)

            if isinstance(self.db, (StudentDBJSON, StudentDBCSV)):
                save = input("\nСохранить изменения в файл? (y/n): ").strip().lower()
                if save == 'y':
                    self._save_to_file()
        except ValueError as e:
            print(f"Ошибка: {e}")

    def _delete(self) -> None:
        print("\nУдаление по фильтру")
        print("Введите условия поиска (Enter – пропустить):")
        sid = self._read_optional_int("id: ")
        fname = input("first_name: ").strip() or None
        sname = input("second_name: ").strip() or None
        age = self._read_optional_int("age: ")
        sex = input("sex: ").strip() or None

        found = self.db.select(
            student_id=sid,
            first_name=fname,
            second_name=sname,
            age=age,
            sex=sex
        )

        if not found:
            print("Записи по заданному фильтру не найдены.")
            return

        print(f"\nНайдено записей для удаления: {len(found)}")
        self._print_records(found)

        confirm = input("\nПодтвердите удаление (y/n): ").strip().lower()
        if confirm != 'y':
            print("Удаление отменено.")
            return

        try:
            deleted = self.db.delete(
                student_id=sid,
                first_name=fname,
                second_name=sname,
                age=age,
                sex=sex,
            )
            if deleted:
                print(f"\nУдалено записей: {len(deleted)}")
                print("Удалённые записи:")
                self._print_records(deleted)

                if isinstance(self.db, (StudentDBJSON, StudentDBCSV)):
                    save = input("\nСохранить изменения в файл? (y/n): ").strip().lower()
                    if save == 'y':
                        self._save_to_file()
        except ValueError as e:
            print(f"Ошибка: {e}")

    def run(self) -> None:
        print("=== Система управления базой данных студентов ===")

        while True:
            self._print_menu()
            action = input("\nВыберите действие: ").strip()

            if action == "1":
                self._add()
            elif action == "2":
                self._show_all()
            elif action == "3":
                self._find()
            elif action == "4":
                self._update()
            elif action == "5":
                self._delete()
            elif action == "6":
                self._export_data()
            elif action == "0":
                print("Выход из программы.")
                break
            else:
                print("Неизвестная команда. Повторите ввод.")


if __name__ == "__main__":
    app = Tui()
    app.run()