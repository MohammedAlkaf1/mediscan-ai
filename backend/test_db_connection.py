import psycopg2

try:
    conn = psycopg2.connect(
        host="127.0.0.1",
        port=5432,
        database="medical",
        user="postgres",
        password="12345"
    )
    print("SUCCESS: Connected to PostgreSQL!")
    print("Database: medical")
    
    # Test query
    cur = conn.cursor()
    cur.execute("SELECT version();")
    version = cur.fetchone()
    print(f"PostgreSQL Version: {version[0]}")
    
    # Check if tables exist
    print("\nChecking tables:")
    tables = ['reports', 'report_files', 'extracted_text', 'lab_results', 'explanations']
    for table in tables:
        cur.execute(f"SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = '{table}');")
        exists = cur.fetchone()[0]
        status = "✓" if exists else "✗"
        print(f"  {status} Table '{table}' {'exists' if exists else 'does not exist'}")
    
    cur.close()
    conn.close()
except Exception as e:
    print(f"ERROR: {e}")
