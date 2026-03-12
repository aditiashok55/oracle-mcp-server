import oracledb
from dotenv import load_dotenv
import os

load_dotenv()

connection_string = os.getenv("ORACLE_CONNECTION_STRING")
instant_client_path = os.getenv("ORACLE_INSTANT_CLIENT_PATH")

if not connection_string:
    print("Error: ORACLE_CONNECTION_STRING is not set in .env")
    exit(1)

if instant_client_path:
    try:
        oracledb.init_oracle_client(lib_dir=instant_client_path)
        print("Oracle Instant Client initialised.")
    except oracledb.Error as e:
        print(f"Instant Client initialisation error: {e}")
        exit(1)

try:
    connection = oracledb.connect(connection_string)
    print("Connected to Oracle database successfully!")
    connection.close()
except oracledb.Error as e:
    print(f"Connection error: {e}")