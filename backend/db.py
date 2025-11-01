# # backend/db.py
# from flask_sqlalchemy import SQLAlchemy

# # SQLite / SQLAlchemy only
# db = SQLAlchemy()


# def ensure_conversations_schema(app):
#     """Ensure Conversation table and ChatHistory.conversation_id exist (SQLite-safe).

#     - Creates `conversation` table if missing
#     - Adds `conversation_id` column to `chat_history` if missing
#     """
#     try:
#         engine = db.get_engine(app)
#     except Exception:
#         engine = db.engine

#     conn = engine.connect()
#     try:
#         # Create conversation table if not exists
#         conn.execute(
#             """
#             CREATE TABLE IF NOT EXISTS conversation (
#                 id INTEGER PRIMARY KEY AUTOINCREMENT,
#                 user_id INTEGER NOT NULL,
#                 title VARCHAR(200) NOT NULL DEFAULT 'New chat',
#                 created_at DATETIME,
#                 updated_at DATETIME
#             )
#             """
#         )

#         # Ensure chat_history has conversation_id
#         res = conn.execute("PRAGMA table_info('chat_history')")
#         cols = [row[1] for row in res.fetchall()]
#         if 'conversation_id' not in cols:
#             print("Adding missing column 'chat_history.conversation_id' to SQLite database...")
#             conn.execute("ALTER TABLE chat_history ADD COLUMN conversation_id INTEGER")
#             print("Added column 'conversation_id' to chat_history table")
#     except Exception as e:
#         print('ensure_conversations_schema: failed to inspect/alter tables:', e)
#     finally:
#         try:
#             conn.close()
#         except Exception:
#             pass

# def ensure_profile_response_style(app):
# 	"""Ensure custom columns exist on the `profile` table for SQLite DBs.

# 	This is a lightweight, safe migration helper: it inspects PRAGMA table_info('profile')
# 	and adds the columns with a default value if they are missing.
# 	"""
# 	try:
# 		engine = db.get_engine(app)
# 	except Exception:
# 		# Fallback for older Flask-SQLAlchemy versions
# 		engine = db.engine

# 	conn = engine.connect()
# 	try:
# 		res = conn.execute("PRAGMA table_info('profile')")
# 		cols = [row[1] for row in res.fetchall()]
        
#         # List of columns to check and add if missing (column_name, type_with_default)
# 		COLUMNS_TO_ADD = [
# 			('response_style', 'VARCHAR(20) DEFAULT "concise"'),
# 			('family_medication_history', 'TEXT'),
# 			('previous_medication_history', 'TEXT')
# 		]

# 		for column_name, column_type in COLUMNS_TO_ADD:
# 			if column_name not in cols:
# 				# ALTER TABLE ADD COLUMN is supported by SQLite
# 				print(f"Adding missing column 'profile.{column_name}' to SQLite database...")
# 				conn.execute(f"ALTER TABLE profile ADD COLUMN {column_name} {column_type}")
# 				print(f"Added column '{column_name}' to profile table")

# 	except Exception as e:
# 		print('ensure_profile_response_style: failed to inspect/alter table:', e)
# 	finally:
# 		try:
# 			conn.close()
# 		except Exception:
# 			pass
# backend/db.py
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import text

# SQLite / SQLAlchemy only
db = SQLAlchemy()


def ensure_conversations_schema(app):
    """Ensure Conversation table and ChatHistory.conversation_id exist (SQLite-safe).

    - Creates `conversation` table if missing
    - Adds `conversation_id` column to `chat_history` if missing
    """
    try:
        engine = db.get_engine(app)
    except Exception:
        engine = db.engine

    conn = engine.connect()
    try:
        # Create conversation table if not exists
        conn.execute(
            text(
            """
            CREATE TABLE IF NOT EXISTS conversation (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                title VARCHAR(200) NOT NULL DEFAULT 'New chat',
                created_at DATETIME,
                updated_at DATETIME
            )
            """
            )
        )

        # Ensure chat_history has conversation_id
        res = conn.execute(text("PRAGMA table_info('chat_history')"))
        cols = [row[1] for row in res.fetchall()]
        if 'conversation_id' not in cols:
            print("Adding missing column 'chat_history.conversation_id' to SQLite database...")
            # Use raw connection object to execute ALTER TABLE
            conn.execute(text("ALTER TABLE chat_history ADD COLUMN conversation_id INTEGER"))
            print("Added column 'conversation_id' to chat_history table")
        
        conn.commit() # Commit changes to chat_history table

    except Exception as e:
        print('ensure_conversations_schema: failed to inspect/alter tables:', e)
        conn.rollback() # Rollback if error occurred
    finally:
        try:
            conn.close()
        except Exception:
            pass

def ensure_profile_response_style(app):
	"""Ensure custom columns exist on the `profile` table for SQLite DBs.

	This is a lightweight, safe migration helper: it inspects PRAGMA table_info('profile')
	and adds the columns with a default value if they are missing.
	"""
	try:
		engine = db.get_engine(app)
	except Exception:
		# Fallback for older Flask-SQLAlchemy versions
		engine = db.engine

	conn = engine.connect()
	try:
		res = conn.execute(text("PRAGMA table_info('profile')"))
		cols = [row[1] for row in res.fetchall()]
        
        # List of columns to check and add if missing (column_name, type_with_default)
		COLUMNS_TO_ADD = [
			('response_style', 'VARCHAR(20) DEFAULT "concise"'),
			('family_medication_history', 'TEXT'),
			('previous_medication_history', 'TEXT'),
			('weight', 'REAL')
		]

		migrated = False
		for column_name, column_type in COLUMNS_TO_ADD:
			if column_name not in cols:
				# ALTER TABLE ADD COLUMN is supported by SQLite
				print(f"MIGRATION: Adding missing column 'profile.{column_name}' to SQLite database...")
				# Use text() function for raw SQL execution
				conn.execute(text(f"ALTER TABLE profile ADD COLUMN {column_name} {column_type}"))
				print(f"MIGRATION: Added column '{column_name}' successfully.")
				migrated = True
			# else: print(f"Column '{column_name}' already exists.")

		if migrated:
			conn.commit()
			print("MIGRATION: Profile schema update committed.")
		
	except Exception as e:
		print(f'FATAL MIGRATION ERROR in ensure_profile_response_style: {e}')
		conn.rollback()
	finally:
		try:
			conn.close()
		except Exception:
			pass
