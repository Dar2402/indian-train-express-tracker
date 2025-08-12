from sqlalchemy import (
    create_engine, MetaData, Table, Column, Integer, String, DateTime, Float,
    ForeignKey, Index
)
from sqlalchemy.exc import SQLAlchemyError

def create_table_dynamic(db_url: str, table_name: str, columns: list, indexes: list = None):
    """
    Dynamically creates a table with optional indexes and foreign keys.

    Args:
        db_url (str): Database connection string.
        table_name (str): Name of the table to create.
        columns (list): List of dicts with column metadata.
                        Supported keys: name, type, length, primary_key, nullable,
                                        autoincrement, unique, default, foreign_key.
        indexes (list): List of dicts for indexes.
                        Example:
                        [
                            {"name": "idx_train_number", "columns": ["train_number"]},
                            {"name": "idx_status_station", "columns": ["status", "current_station"]}
                        ]
    """
    engine = create_engine(db_url)
    metadata = MetaData()

    type_map = {
        "integer": Integer,
        "string": lambda length: String(length),
        "datetime": DateTime,
        "float": Float
    }

    column_objs = []
    for col in columns:
        col_type_key = col["type"].lower()
        if col_type_key not in type_map:
            raise ValueError(f"Unsupported column type: {col['type']}")

        col_type = type_map[col_type_key](col.get("length", 255)) if col_type_key == "string" else type_map[col_type_key]

        fk = ForeignKey(col["foreign_key"]) if "foreign_key" in col else None

        column_objs.append(
            Column(
                col["name"],
                col_type,
                primary_key=col.get("primary_key", False),
                nullable=col.get("nullable", True),
                autoincrement=col.get("autoincrement", False),
                unique=col.get("unique", False),
                default=col.get("default", None),
                foreign_key=fk
            )
        )

    table = Table(table_name, metadata, *column_objs)

    if indexes:
        for idx in indexes:
            Index(idx["name"], *[table.c[col] for col in idx["columns"]])

    try:
        metadata.create_all(engine)
        print(f"✅ Table '{table_name}' created successfully.")
    except SQLAlchemyError as e:
        print(f"❌ Error creating table: {e}")

# Example usage
if __name__ == "__main__":
    DB_URL = "postgresql://postgres:iaCkmHPhuyhFLEBDGdwxQGGqlHvdgWJA@yamanote.proxy.rlwy.net:29855/railway"

    columns_metadata = [
        {"name": "id", "type": "Integer", "primary_key": True, "nullable": False, "autoincrement": True},
        {"name": "station_code", "type": "String", "length": 10, "nullable": False},
        # {"name": "status", "type": "String", "length": 255, "nullable": False},
        {"name": "station_name", "type": "String", "length": 50, "nullable": True},
        {"name": "created_at", "type": "DateTime", "nullable": True},
        {"name": "updated_at", "type": "DateTime", "nullable": True},
    ]

    indexes_metadata = [
        {"name": "idx_station_code", "columns": ["station_code"]},
        {"name": "idx_station_name", "columns": ["station_name"]}
    ]

    create_table_dynamic(DB_URL, "stations", columns_metadata, indexes_metadata)
