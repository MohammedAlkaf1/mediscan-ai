import psycopg2

conn = psycopg2.connect(
    host='localhost',
    port=5432,
    database='medical',
    user='postgres',
    password='12345'
)
cur = conn.cursor()

# Check reports table
print("=== reports table ===")
cur.execute("SELECT column_name, data_type FROM information_schema.columns WHERE table_name = 'reports' ORDER BY ordinal_position")
for row in cur.fetchall():
    print(f"  {row[0]}: {row[1]}")

# Check extracted_text table
print("\n=== extracted_text table ===")
cur.execute("SELECT column_name, data_type FROM information_schema.columns WHERE table_name = 'extracted_text' ORDER BY ordinal_position")
for row in cur.fetchall():
    print(f"  {row[0]}: {row[1]}")

# Check lab_results table
print("\n=== lab_results table ===")
cur.execute("SELECT column_name, data_type FROM information_schema.columns WHERE table_name = 'lab_results' ORDER BY ordinal_position")
for row in cur.fetchall():
    print(f"  {row[0]}: {row[1]}")

# Check explanations table
print("\n=== explanations table ===")
cur.execute("SELECT column_name, data_type FROM information_schema.columns WHERE table_name = 'explanations' ORDER BY ordinal_position")
for row in cur.fetchall():
    print(f"  {row[0]}: {row[1]}")

cur.close()
conn.close()
