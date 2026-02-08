import mysql.connector

# Connect to database
conn = mysql.connector.connect(
    host="localhost",
    user="root",
    password="Elan@2004",
    database="cricbuzz_livestats",
    auth_plugin="mysql_native_password"
)

cursor = conn.cursor()

# Show all tables
print("=== TABLES IN DATABASE ===")
cursor.execute("SHOW TABLES")
tables = cursor.fetchall()
for table in tables:
    print(f"Table: {table[0]}")

print("\n=== PLAYERS TABLE STRUCTURE ===")
cursor.execute("DESCRIBE players")
columns = cursor.fetchall()
for col in columns:
    print(f"Column: {col[0]}, Type: {col[1]}, Null: {col[2]}, Key: {col[3]}")

print("\n=== SAMPLE DATA ===")
cursor.execute("SELECT * FROM players LIMIT 1")
sample = cursor.fetchone()
if sample:
    cursor.execute("SELECT * FROM players LIMIT 1")
    cursor.fetchone()
    print("Column names:")
    for desc in cursor.description:
        print(f"  - {desc[0]}")
else:
    print("No data in table")

cursor.close()
conn.close()