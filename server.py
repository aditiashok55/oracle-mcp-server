import oracledb
from dotenv import load_dotenv
import os
from mcp.server import FastMCP
from tools.query_tool import run_sql_query
from tools.schema_tool import get_table_schema
from tools.write_tool import run_write_query

# Load environment variables
load_dotenv()

# Oracle connection
connection_string = os.getenv("ORACLE_CONNECTION_STRING")
connection = oracledb.connect(connection_string)


def main():
    server = FastMCP(name="oracle-mcp-server")

    @server.tool()
    def run_sql_query_tool(query: str) -> str:
        """
        Execute a read-only SELECT query on the Oracle database.
        Only whitelisted tables are accessible. Results are capped at MAX_QUERY_ROWS.
        """
        return run_sql_query(connection, query)

    @server.tool()
    def get_table_schema_tool(table_name: str) -> str:
        """
        Retrieve the column names and data types for a whitelisted table.
        """
        return get_table_schema(connection, table_name)

    @server.tool()
    def run_write_query_tool(query: str, confirmed: bool = False) -> str:
        """
        Execute a write query (INSERT, UPDATE, or DELETE) on the Oracle database.
        Only whitelisted tables are accessible. The query will not execute until
        confirmed=true is explicitly passed. Always call this tool once first
        without confirmation to show the user a summary before proceeding.
        """
        return run_write_query(connection, query, confirmed)

    print("Starting Oracle MCP Server...")
    server.run()


if __name__ == "__main__":
    try:
        main()
    finally:
        connection.close()