import os, pyodbc
dsn = os.environ['ANALYTICS_DB_DSN']
c = pyodbc.connect(dsn, timeout=15)
cur = c.cursor()
cur.execute("SELECT TABLE_SCHEMA, TABLE_NAME FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_NAME LIKE '%STRANS%' OR TABLE_NAME LIKE '%SKU%' OR TABLE_NAME LIKE '%TRANSHDR%' ORDER BY TABLE_NAME")
for r in cur.fetchall():
    print(r)
c.close()
