import oracledb
import json
from config.settings import TABLE_WHITE_LIST

def run_sql_query(connection: oracledb.Connection, query: str) -> str:
    """
    Execute a read-only SQL query and return results as JSON string.
    """
    try:
        # Basic validation for read-only queries
        query_upper = query.upper().strip()
        if not query_upper.startswith('SELECT'):
            return json.dumps({"error": "Only SELECT queries are allowed"})
        
        # Check if query references unauthorized tables
        # Add your table validation logic here
        
        cursor = connection.cursor()
        cursor.execute(query)
        columns = [desc[0] for desc in cursor.description]
        rows = cursor.fetchall()
        cursor.close()
        
        result = {
            "columns": columns,
            "rows": [list(row) for row in rows],
            "row_count": len(rows)
        }
        return json.dumps(result)
        
    except oracledb.Error as e:
        return json.dumps({"error": str(e)})