import oracledb
from dotenv import load_dotenv
import os

try:
    # Initialize Oracle Instant Client
    oracledb.init_oracle_client(lib_dir=r"C:\\Users\\JAS260\\Downloads\\instantclient-basic-windows.x64-23.8.0.25.04\\instantclient_23_8")
    print("Client version:", oracledb.clientversion())
except oracledb.Error as e:
    print("Client version error:", str(e))
    exit(1)

load_dotenv()
connection_string = os.getenv("ORACLE_CONNECTION_STRING")
print("Connection string:", connection_string)

if not connection_string:
    print("Error: ORACLE_CONNECTION_STRING is not set in .env")
    exit(1)

try:
    connection = oracledb.connect(connection_string)
    print("Connected to Oracle database successfully!")
    connection.close()
except oracledb.Error as e:
    print("Connection error:", str(e))