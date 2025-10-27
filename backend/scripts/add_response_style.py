# scripts/add_response_style.py
import sqlite3
import os

p = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'instance', 'database.db'))
print('DB path:', p)
conn = sqlite3.connect(p)
cur = conn.cursor()
try:
    cur.execute("PRAGMA table_info('profile')")
    cols = [r[1] for r in cur.fetchall()]
    print('Existing profile columns:', cols)
    if 'response_style' not in cols:
        try:
            cur.execute("ALTER TABLE profile ADD COLUMN response_style VARCHAR(20) DEFAULT 'concise'")
            print("ALTER TABLE executed: response_style added")
        except Exception as e:
            print('ALTER TABLE failed:', type(e).__name__, e)
    else:
        print('response_style column already present')
    try:
        cur.execute("UPDATE profile SET response_style='concise' WHERE response_style IS NULL OR response_style=''")
        conn.commit()
        print('Backfilled response_style values')
    except Exception as e:
        print('Backfill failed:', type(e).__name__, e)
except Exception as e:
    print('Failed to inspect/add column:', type(e).__name__, e)
finally:
    conn.close()
