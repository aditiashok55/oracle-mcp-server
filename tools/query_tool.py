import re
import oracledb
import json
from config.settings import TABLE_WHITE_LIST, MAX_QUERY_ROWS


def extract_table_names(query: str) -> list[str]:
    """
    Extract table names from a SQL SELECT query.
    Handles FROM and JOIN clauses. Returns a list of uppercase table names.
    """
    # Remove string literals to avoid false matches inside quoted values
    cleaned = re.sub(r"'[^']*'", "", query, flags=re.IGNORECASE)

    # Match tables after FROM and all JOIN types
    pattern = r'\b(?:FROM|JOIN)\s+([a-zA-Z_][a-zA-Z0-9_$#]*)'
    matches = re.findall(pattern, cleaned, flags=re.IGNORECASE)

    return [match.upper() for match in matches]


def run_sql_query(connection: oracledb.Connection, query: str) -> str:
    """
    Execute a read-only SQL query and return results as a JSON string.

    Enforces:
    - SELECT-only queries
    - Table whitelist validation
    - Row limit (configured via MAX_QUERY_ROWS in settings.py)
    """
    try:
        query_upper = query.upper().strip()

        # Reject anything that isn't a SELECT statement
        if not query_upper.startswith('SELECT'):
            return json.dumps({"error": "Only SELECT queries are allowed."})

        # Validate all referenced tables against the whitelist
        referenced_tables = extract_table_names(query)
        if not referenced_tables:
            return json.dumps({"error": "Could not identify any table references in the query."})

        unauthorised = [t for t in referenced_tables if t not in TABLE_WHITE_LIST]
        if unauthorised:
            return json.dumps({
                "error": f"Query references tables that are not permitted: {', '.join(unauthorised)}. "
                         f"Allowed tables are: {', '.join(TABLE_WHITE_LIST)}."
            })

        cursor = connection.cursor()
        cursor.execute(query)

        columns = [desc[0] for desc in cursor.description]
        rows = cursor.fetchmany(MAX_QUERY_ROWS)
        cursor.close()

        result = {
            "columns": columns,
            "rows": [list(row) for row in rows],
            "row_count": len(rows),
            "row_limit": MAX_QUERY_ROWS,
            "limit_reached": len(rows) == MAX_QUERY_ROWS
        }
        return json.dumps(result)

    except oracledb.Error as e:
        return json.dumps({"error": str(e)})