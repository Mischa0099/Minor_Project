import os
import sqlite3
import sys
import stat

p = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'instance', 'database.db'))
print('CWD:', os.getcwd())
print('DB path:', p)
print('exists:', os.path.exists(p))
print('isfile:', os.path.isfile(p))
try:
    st = os.stat(p)
    print('mode:', oct(st.st_mode), 'size:', st.st_size)
except Exception as e:
    print('stat-error:', repr(e))

# Try opening the DB
try:
    conn = sqlite3.connect(p)
    cur = conn.cursor()
    cur.execute("SELECT name FROM sqlite_master WHERE type='table' LIMIT 1;")
    print('first-table:', cur.fetchone())
    conn.close()
except Exception as e:
    print('open-error:', type(e).__name__, str(e))
    sys.exit(1)

print('DB check completed successfully')
