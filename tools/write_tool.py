import re
import oracledb
import json
from config.settings import TABLE_WHITE_LIST

# Operations the write tool is permitted to execute
ALLOWED_WRITE_OPERATIONS = {"INSERT", "UPDATE", "DELETE"}


def extract_table_name_from_write(query: str) -> str | None:
    """
    Extract the target table name from an INSERT, UPDATE, or DELETE statement.
    Returns the uppercase table name or None if it cannot be determined.
    """
    cleaned = re.sub(r"'[^']*'", "", query)

    patterns = [
        r'\bINSERT\s+INTO\s+([a-zA-Z_][a-zA-Z0-9_$#]*)',   # INSERT INTO <table>
        r'\bUPDATE\s+([a-zA-Z_][a-zA-Z0-9_$#]*)',           # UPDATE <table>
        r'\bDELETE\s+FROM\s+([a-zA-Z_][a-zA-Z0-9_$#]*)',    # DELETE FROM <table>
    ]

    for pattern in patterns:
        match = re.search(pattern, cleaned, flags=re.IGNORECASE)
        if match:
            return match.group(1).upper()

    return None


def run_write_query(connection: oracledb.Connection, query: str, confirmed: bool) -> str:
    """
    Execute a write query (INSERT, UPDATE, DELETE) against the Oracle database.

    Parameters:
        connection  -- active oracledb connection
        query       -- the SQL statement to execute
        confirmed   -- must be True for the query to execute; if False, returns
                       a dry-run summary for the user to review before confirming

    Enforces:
        - INSERT, UPDATE, DELETE only (no DDL)
        - Table whitelist validation
        - Explicit confirmation gate before any data is modified
    """
    try:
        query_stripped = query.strip()
        operation = query_stripped.split()[0].upper()

        # Reject anything outside the allowed write operations
        if operation not in ALLOWED_WRITE_OPERATIONS:
            return json.dumps({
                "error": f"Operation '{operation}' is not permitted. "
                         f"Allowed write operations are: {', '.join(ALLOWED_WRITE_OPERATIONS)}."
            })

        # Validate the target table against the whitelist
        table_name = extract_table_name_from_write(query_stripped)
        if not table_name:
            return json.dumps({"error": "Could not identify the target table in the query."})

        if table_name not in TABLE_WHITE_LIST:
            return json.dumps({
                "error": f"Table '{table_name}' is not permitted. "
                         f"Allowed tables are: {', '.join(TABLE_WHITE_LIST)}."
            })

        # Confirmation gate — return a dry-run summary if not yet confirmed
        if not confirmed:
            return json.dumps({
                "status": "awaiting_confirmation",
                "message": (
                    f"You are about to execute the following {operation} on '{table_name}':\n\n"
                    f"{query_stripped}\n\n"
                    f"Please confirm by calling this tool again with confirmed=true."
                )
            })

        # Execute the write query
        cursor = connection.cursor()
        cursor.execute(query_stripped)
        rows_affected = cursor.rowcount
        connection.commit()
        cursor.close()

        return json.dumps({
            "status": "success",
            "operation": operation,
            "table": table_name,
            "rows_affected": rows_affected
        })

    except oracledb.Error as e:
        # Roll back on any database error to leave the DB in a clean state
        connection.rollback()
        return json.dumps({"error": str(e)})