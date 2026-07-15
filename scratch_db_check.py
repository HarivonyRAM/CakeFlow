import sys
import os

# Add project root to sys.path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

from app.db.init_db import initialize_database
from app.db.connection import get_connection

# Re-run initialization to insert SuperAdmin
initialize_database()

# Verify SuperAdmin exists
conn = get_connection()
cursor = conn.cursor()
cursor.execute("SELECT id, username, nom, prenom, role FROM users;")
users = cursor.fetchall()
print("\n=== Users in database ===")
for u in users:
    print(dict(u))
conn.close()
