from database import Database
from file_database import FileDatabase
from ui import GRADES_SCHEMA, STUDENTS_SCHEMA, ConsoleUI, Menu

DEFAULT_TABLES = {"students": STUDENTS_SCHEMA, "grades": GRADES_SCHEMA}


def build_database() -> Database:
    print("Режим хранения: 1 — в памяти (данные теряются при выходе), "
          "2 — файл (каталог data)")
    choice = input("> ").strip()
    if choice == "2":
        return FileDatabase("data")
    return Database()


def main() -> None:
    db = build_database()
    for name, schema in DEFAULT_TABLES.items():
        if name not in db.table_names():
            db.create_table(name, schema)

    try:
        Menu(db, ConsoleUI()).run()
    except KeyboardInterrupt:
        print("\nПрервано.")


if __name__ == "__main__":
    main()
