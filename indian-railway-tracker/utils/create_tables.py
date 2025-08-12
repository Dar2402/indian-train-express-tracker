from sqlalchemy import (
    create_engine, MetaData, Table, Column, Integer, String, DateTime, Float,
    ForeignKey, Index
)
from sqlalchemy.dialects.postgresql import ARRAY, JSONB
from sqlalchemy.exc import SQLAlchemyError


def create_table_dynamic(db_url: str, table_name: str, columns: list, indexes: list = None):
    """
    Dynamically creates a table with optional indexes and foreign keys.
    Reflects existing tables from DB first, so foreign keys can reference them.

    Args:
        db_url (str): Database connection string.
        table_name (str): Name of the table to create.
        columns (list): List of dicts with column metadata.
                        Supported keys: name, type, length, primary_key, nullable,
                                        autoincrement, unique, default, foreign_key.
        indexes (list): List of dicts for indexes.
    """
    engine = create_engine(db_url)
    metadata = MetaData()

    # Reflect all existing tables from DB into metadata
    metadata.reflect(bind=engine)
    # Now metadata.tables contains all existing tables known to DB

    type_map = {
        "integer": Integer,
        "string": lambda length=255: String(length),
        "datetime": DateTime,
        "float": Float,
        "array": lambda: ARRAY(Integer)  # Only integer arrays supported here
    }

    column_objs = []
    for col in columns:
        col_type_key = col["type"].lower()
        if col_type_key not in type_map:
            raise ValueError(f"Unsupported column type: {col['type']}")

        if col_type_key == "string":
            col_type = type_map[col_type_key](col.get("length", 255))
        elif col_type_key == "array":
            col_type = type_map[col_type_key]()  # no length param for ARRAY
        else:
            col_type = type_map[col_type_key]

        fk = ForeignKey(col["foreign_key"]) if "foreign_key" in col else None

        args = [col["name"], col_type]
        if fk:
            args.append(fk)

        column_objs.append(
            Column(
                *args,
                primary_key=col.get("primary_key", False),
                nullable=col.get("nullable", True),
                autoincrement=col.get("autoincrement", False),
                unique=col.get("unique", False),
                default=col.get("default", None),
            )
        )

    # Create new table in the same metadata (which has all reflected tables)
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
        {"name": "train_no", "type": "String", "length": 20, "nullable": True,  "primary_key": True, "nullable": False},
        {"name": "arrival_time", "type": "String", "length": 100, "nullable": True},
        {"name": "delay", "type": "Integer", "nullable": True},
        #  "foreign_key": "stations.station_code"},
        # {"name": "dstn_stn_code", "type": "String", "length": 10, "nullable": True,
        #  "foreign_key": "stations.station_code"},
        {"name": "departure_time", "type": "String", "length": 10, "nullable": True},
        {"name": "station_code", "type": "String", "length": 10, "nullable": True},
        # {"name": "travel_time", "type": "String", "length": 20, "nullable": True},
        # {"name": "running_days", "type": "array", "nullable": True},
        # {"name": "distance", "type": "String", "length": 20, "nullable": True},
        # {"name": "halts", "type": "Integer", "nullable": True},
        # {"name": "live_status", "type": "String", "length": 20, "nullable": True}
    ]

    indexes_metadata = [
        {"name": "idx_train_no", "columns": ["train_no"]},
        {"name": "idx_source_stn_code", "columns": ["source_stn_code"]},
        {"name": "idx_dstn_stn_code", "columns": ["dstn_stn_code"]},
    ]

    create_table_dynamic(DB_URL, "trains", columns_metadata, indexes_metadata)
