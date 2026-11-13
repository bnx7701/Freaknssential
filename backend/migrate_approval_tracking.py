
import sqlite3
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATABASE_PATH = PROJECT_ROOT / "freaknssential.db"


def migrate():
    if not DATABASE_PATH.exists():
        print("ERROR: Database file not found.")
        return

    connection = sqlite3.connect(DATABASE_PATH)

    try:
        cursor = connection.cursor()

        cursor.execute("PRAGMA table_info(approvals)")
        existing_columns = {
            column[1] for column in cursor.fetchall()
        }

        new_columns = {
            "approved_by": "VARCHAR(100)",
            "rejected_by": "VARCHAR(100)",
            "processed_at": "DATETIME",
        }

        for column_name, column_type in new_columns.items():
            if column_name not in existing_columns:
                cursor.execute(
                    f"ALTER TABLE approvals ADD COLUMN "
                    f"{column_name} {column_type}"
                )
                print(f"Added column: {column_name}")
            else:
                print(f"Column already exists: {column_name}")

        connection.commit()
        print("Migration completed successfully!")

    except Exception:
        connection.rollback()
        raise

    finally:
        connection.close()


if __name__ == "__main__":
    migrate()
