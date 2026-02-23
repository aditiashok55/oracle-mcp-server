import oracledb
from dotenv import load_dotenv
import os
from mcp.server import FastMCP
from tools.query_tool import run_sql_query
from tools.schema_tool import get_table_schema
from config.settings import TABLE_WHITE_LIST

# Load environment variables
load_dotenv()

# Oracle connection
connection_string = os.getenv("ORACLE_CONNECTION_STRING")
connection = oracledb.connect(connection_string)

def main():
    # Initialize MCP server
    server = FastMCP(name="oracle-mcp-server")
    
    # Register query tool using decorator
    @server.tool()
    def run_sql_query_tool(query: str) -> str:
        """Execute a read-only SQL query on the Oracle database"""
        return run_sql_query(connection, query)
    
    # Register schema tool using decorator
    @server.tool()
    def get_table_schema_tool(table_name: str) -> str:
        """Retrieve schema for a specified table"""
        return get_table_schema(connection, table_name)

    # Start the server
    print("Starting Oracle MCP Server...")
    server.run()

if __name__ == "__main__":
    try:
        main()
    finally:
        connection.close()