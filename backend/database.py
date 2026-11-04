import sqlite3
import os

# ⚠️ Change this to point to your actual database file path
DB_PATH = "rss_database.db" 

def view_database():
    if not os.path.exists(DB_PATH):
        print(f"Andmebaasifaili ei leitud: {os.path.abspath(DB_PATH)}")
        print("Palun uuenda 'DB_PATH' muutujat selliselt, et see viitab tegelikule andmebaasifailile.")
        return

    conn = sqlite3.connect(DB_PATH) # ühendame andmebaasiga
    cursor = conn.cursor() # loome cursori

    # 1. Get all table names from the database
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()

    if not tables:
        print(f"⚠️ Connected to {DB_PATH}, but no tables were found.")
        conn.close()
        return

    print(f"📂 Connected to database: {DB_PATH}\n")

    for table_row in tables:
        table_name = table_row[0]
        print("=" * 60)
        print(f"📋 TABLE: {table_name}")
        print("=" * 60)

        # 2. Get column information (Schema)
        cursor.execute(f"PRAGMA table_info('{table_name}');")
        columns = cursor.fetchall()
        col_names = [col[1] for col in columns]
        
        print("\n[ Columns ]")
        for col in columns:
            # col[1] = column name, col[2] = data type, col[5] = primary key flag
            pk_marker = " 🔑 (Primary Key)" if col[5] else ""
            print(f"  • {col[1]}  ({col[2]}){pk_marker}")

        # 3. Get all rows of data
        cursor.execute(f"SELECT * FROM '{table_name}';")
        rows = cursor.fetchall()

        print(f"\n[ Data Records ({len(rows)} total) ]")
        if not rows:
            print("  (This table is currently empty)")
        else:
            # Print column headers neatly
            header_str = " | ".join(f"{name:<15}" for name in col_names)
            print(header_str)
            print("-" * len(header_str))
            
            # Print each row of data
            for row in rows:
                row_str = " | ".join(f"{str(val):<15}" for val in row)
                print(row_str)
                
        print("\n" + "=" * 60 + "\n")

    conn.close()

if __name__ == "__main__":
    view_database()