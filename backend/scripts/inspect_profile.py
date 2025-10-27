# scripts/inspect_profile.py
import sqlite3
import os

p = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'instance', 'database.db'))
print('DB path:', p)
conn = sqlite3.connect(p)
cur = conn.cursor()
try:
    cur.execute("PRAGMA table_info('profile')")
    rows = cur.fetchall()
    if not rows:
        print("profile table does not exist or has no columns.")
    else:
        print("profile table columns (cid, name, type, notnull, dflt_value, pk):")
        for r in rows:
            print(r)
except Exception as e:
    print('Error reading PRAGMA table_info:', type(e).__name__, e)
finally:
    conn.close()
