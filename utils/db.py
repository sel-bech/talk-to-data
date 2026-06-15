import sqlalchemy
from sqlalchemy import create_engine, inspect, text
import pandas as pd

def get_engine(db_path: str):
    """
    Creates a connection to the database.
    
    'engine' = the object that handles talking to the database.
    Think of it as opening a phone line to the database.
    """
    engine = create_engine(f"sqlite:///{db_path}")
    return engine


def get_schema(engine) -> str:
    """
    Reads the database structure and returns it as a string
    we can paste directly into a Gemini prompt.
    
    'inspect' = SQLAlchemy's tool for peeking at the database structure
    without reading any actual data.
    """
    inspector = inspect(engine)
    
    schema_parts = []
    
    # Loop through every table in the database
    for table_name in inspector.get_table_names():
        columns = inspector.get_columns(table_name)
        
        # Build a description of this table
        col_descriptions = []
        for col in columns:
            col_name = col["name"]
            col_type = str(col["type"])  # e.g. INTEGER, VARCHAR, REAL
            col_descriptions.append(f"  {col_name} ({col_type})")
        
        table_description = f"Table: {table_name}\n" + "\n".join(col_descriptions)
        schema_parts.append(table_description)
    
    # Join all tables into one big string
    full_schema = "\n\n".join(schema_parts)
    return full_schema


def run_query(engine, sql: str) -> pd.DataFrame:
    """
    Executes (runs) a SQL query and returns the results
    as a pandas DataFrame (a table in Python memory).
    
    'DataFrame' = pandas' word for a table. Rows and columns,
    just like a spreadsheet, but in Python.
    """
    with engine.connect() as connection:
        result = pd.read_sql_query(text(sql), connection)
    return result