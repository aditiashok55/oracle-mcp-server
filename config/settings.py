# Tables that are accessible via the MCP server.
# Any table not listed here will be rejected by both the query and schema tools.
TABLE_WHITE_LIST = [
    "CUSTOMERS",
    "ORDERS",
    "PRODUCTS"
]

# Maximum number of rows returned by run_sql_query.
# Prevents large unintended result sets on production databases.
MAX_QUERY_ROWS = 500