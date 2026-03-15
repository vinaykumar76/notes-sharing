import pymysql
from setup_db import MYSQL_ROOT_PASSWORD

print("Connecting to database to clear dummy data...")
try:
    connection = pymysql.connect(
        host='localhost',
        user='root',
        password='admin123',
        database='p2p_notes'
    )
    cursor = connection.cursor()
    
    # Disable foreign key checks temporarily to clear tables
    cursor.execute("SET FOREIGN_KEY_CHECKS = 0;")
    
    # Clear all data leaving the structure intact
    cursor.execute("TRUNCATE TABLE downloads;")
    cursor.execute("TRUNCATE TABLE notes;")
    cursor.execute("TRUNCATE TABLE users;")
    
    cursor.execute("SET FOREIGN_KEY_CHECKS = 1;")
    
    connection.commit()
    print("------------------------------------------")
    print("✅ SUCCESS! All dummy data has been removed. The database is now completely empty.")
    print("------------------------------------------")
except Exception as e:
    print(f"Error: {e}")
finally:
    if 'connection' in locals() and connection.open:
        connection.close()
