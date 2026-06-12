from src.db.backend.memory import StudentDB

db = StudentDB()

def _print_menu() -> None:
    print("\n=== База студентов ===")
    print("1. Добавить запись")
    print("2. Показать все записи")
    print("3. Найти записи")
    print("4. Обновить записи")
    print("5. Удалить записи")
    print("0. Выход")

def _read_int(prompt: str) -> int:
    while True:
        raw = input(prompt).strip()
        try:
            return int(raw)
        except ValueError:
            print("Ошибка: введите целое число.")

def _read_optional_int(prompt: str) -> int | None:
    while True:
        raw = input(prompt).strip()
        if raw == "":
            return None
        try:
            return int(raw)
        except ValueError:
            print("Ошибка: введите целое число или оставьте поле пустым.")

def _print_records(records: list[tuple[int, str, str, int, str]]) -> None:
    if not records:
        print("Записи не найдены.")
        return
    for r in records:
        print(r)

def _add() -> None:
    print("\nДобавление записи")
    sid = _read_int("id: ")
    fname = input("first_name: ").strip()
    sname = input("second_name: ").strip()
    age = _read_int("age: ")
    sex = input("sex: ").strip()
    try:
        rec = db.add(sid, fname, sname, age, sex)
        print(f"Запись добавлена: {rec}")
    except ValueError as e:
        print(f"Ошибка: {e}")

def _show_all() -> None:
    print("\nСписок записей")
    _print_records(db.select())

def _find() -> None:
    print("\nПоиск (Enter – пропустить поле)")
    sid = _read_optional_int("id: ")
    fname = input("first_name: ").strip() or None
    sname = input("second_name: ").strip() or None
    age = _read_optional_int("age: ")
    sex = input("sex: ").strip() or None
    records = db.select(student_id=sid, first_name=fname,
                        second_name=sname, age=age, sex=sex)
    _print_records(records)

# --- обновление по фильтру ---
def _update() -> None:
    print("\nОбновление по фильтру")
    print("Введите условия поиска (Enter – пропустить):")
    sid = _read_optional_int("id: ")
    fname = input("first_name: ").strip() or None
    sname = input("second_name: ").strip() or None
    age = _read_optional_int("age: ")
    sex = input("sex: ").strip() or None

    print("Новые значения (Enter – не менять):")
    new_fname = input("first_name: ").strip() or None
    new_sname = input("second_name: ").strip() or None
    new_age = _read_optional_int("age: ")
    new_sex = input("sex: ").strip() or None

    try:
        updated = db.update(
            student_id=sid, first_name=fname, second_name=sname,
            age=age, sex=sex,
            new_first_name=new_fname, new_second_name=new_sname,
            new_age=new_age, new_sex=new_sex,
        )
        print("Обновлённые записи:")
        _print_records(updated)
    except ValueError as e:
        print(f"Ошибка: {e}")

def _delete() -> None:
    print("\nУдаление по фильтру")
    print("Введите условия поиска (Enter – пропустить):")
    sid = _read_optional_int("id: ")
    fname = input("first_name: ").strip() or None
    sname = input("second_name: ").strip() or None
    age = _read_optional_int("age: ")
    sex = input("sex: ").strip() or None

    try:
        deleted = db.delete(
            student_id=sid, first_name=fname, second_name=sname,
            age=age, sex=sex,
        )
        print("Удалённые записи:")
        _print_records(deleted)
    except ValueError as e:
        print(f"Ошибка: {e}")

def run() -> None:
    while True:
        _print_menu()
        action = input("Выберите действие: ").strip()
        if action == "1":
            _add()
        elif action == "2":
            _show_all()
        elif action == "3":
            _find()
        elif action == "4":
            _update()
        elif action == "5":
            _delete()
        elif action == "0":
            print("Выход из программы.")
            break
        else:
            print("Неизвестная команда. Повторите ввод.")