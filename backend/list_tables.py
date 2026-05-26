import psycopg2

conn = psycopg2.connect(
    host='localhost',
    port=5432,
    database='medical',
    user='postgres',
    password='12345'
)
cur = conn.cursor()

cur.execute("SELECT tablename FROM pg_tables WHERE schemaname = 'public' ORDER BY tablename")
tables = [row[0] for row in cur.fetchall()]

print('\n📋 Tables in database:')
for t in tables:
    print(f'  ✓ {t}')

print(f'\nTotal: {len(tables)} tables')

cur.close()
conn.close()
