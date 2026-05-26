import psycopg2

try:
    conn = psycopg2.connect(
        host="localhost",
        port=5432,
        database="medical",
        user="postgres",
        password="12345"
    )
    
    cur = conn.cursor()
    
    # Get all tables
    cur.execute("""
        SELECT table_name 
        FROM information_schema.tables 
        WHERE table_schema = 'public' 
        ORDER BY table_name;
    """)
    
    tables = cur.fetchall()
    
    print("=" * 50)
    print("TABLES IN 'medical' DATABASE:")
    print("=" * 50)
    
    for table in tables:
        print(f"  ✓ {table[0]}")
    
    # Check specifically for users table
    print("\n" + "=" * 50)
    cur.execute("""
        SELECT EXISTS (
            SELECT FROM information_schema.tables 
            WHERE table_schema = 'public' 
            AND table_name = 'users'
        );
    """)
    
    users_exists = cur.fetchone()[0]
    
    if users_exists:
        print("✅ USERS TABLE: EXISTS")
        
        # Get column info
        cur.execute("""
            SELECT column_name, data_type 
            FROM information_schema.columns 
            WHERE table_name = 'users' 
            ORDER BY ordinal_position;
        """)
        columns = cur.fetchall()
        print("\nColumns in users table:")
        for col in columns:
            print(f"  - {col[0]} ({col[1]})")
    else:
        print("❌ USERS TABLE: DOES NOT EXIST")
    
    print("=" * 50)
    
    cur.close()
    conn.close()
    
except Exception as e:
    print(f"ERROR: {e}")
