from db import get_connection

conn = get_connection()

if conn:
    print("DB connection test successful")
    conn.close()