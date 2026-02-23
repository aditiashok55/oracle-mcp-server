import oracledb
from dotenv import load_dotenv
import os
import json
from config.settings import TABLE_WHITE_LIST

# Load environment variables
load_dotenv()
connection_string = os.getenv("ORACLE_CONNECTION_STRING")
connection = oracledb.connect(connection_string)

def get_table_schema(connection: oracledb.Connection, table_name: str) -> str:
    """
    Retrieve the schema for a specified table.
    Returns column names and data types as a JSON string.
    """
    try:
        # Validate table name
        if table_name.upper() not in TABLE_WHITE_LIST:
            return json.dumps({"error": f"Table {table_name} is not in the whitelist"})

        cursor = connection.cursor()
        cursor.execute(
            "SELECT column_name, data_type FROM user_tab_columns WHERE table_name = :1",
            [table_name.upper()]
        )
        schema = [dict(zip(["column_name", "data_type"], row)) for row in cursor.fetchall()]
        cursor.close()
        return json.dumps({"schema": schema})
    except oracledb.Error as e:
        return json.dumps({"error": str(e)})