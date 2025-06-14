import sqlite3
from datetime import datetime

class Database:
    def __init__(self, db_name="mycotracker.db"):
        self.db_name = db_name
        self.conn = sqlite3.connect(self.db_name)
        self.cursor = self.conn.cursor()
        self.create_tables()

    def create_tables(self):
        """Create all necessary tables if they don't exist"""
        try:
            # Agar Plates table
            self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS agar_plates (
                    plate_id TEXT PRIMARY KEY,
                    strain_name TEXT NOT NULL,
                    date_inoculated TEXT NOT NULL,
                    growth_description TEXT,
                    contamination_notes TEXT,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                )
            ''')

            # Liquid Cultures table
            self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS liquid_cultures (
                    lc_id TEXT PRIMARY KEY,
                    source_id TEXT NOT NULL,
                    strain_name TEXT NOT NULL,
                    inoculation_date TEXT NOT NULL,
                    growth_description TEXT,
                    viability TEXT NOT NULL,
                    volume_remaining REAL,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                )
            ''')

            # Grain Jars table
            self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS grain_jars (
                    jar_id TEXT PRIMARY KEY,
                    source_id TEXT NOT NULL,
                    inoculation_date TEXT NOT NULL,
                    colonization_percentage INTEGER,
                    shake_date TEXT,
                    contamination_notes TEXT,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                )
            ''')

            # Bulk Tubs table
            self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS bulk_tubs (
                    tub_id TEXT PRIMARY KEY,
                    spawn_source TEXT NOT NULL,
                    substrate_type TEXT NOT NULL,
                    date_to_bulk TEXT NOT NULL,
                    first_pins_date TEXT,
                    harvest_weight_flush1 REAL,
                    harvest_weight_flush2 REAL,
                    harvest_weight_flush3 REAL,
                    performance_notes TEXT,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                )
            ''')

            # Clone Library table
            self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS clone_library (
                    clone_id TEXT PRIMARY KEY,
                    parent_strain TEXT NOT NULL,
                    date_taken TEXT NOT NULL,
                    tissue_source TEXT NOT NULL,
                    growth_characteristics TEXT,
                    performance_notes TEXT,
                    archived INTEGER DEFAULT 0,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                )
            ''')

            self.conn.commit()
        except sqlite3.Error as e:
            print(f"Error creating tables: {e}")

    def close(self):
        """Close the database connection"""
        if self.conn:
            self.conn.close()

    def get_timestamp(self):
        """Get current timestamp in ISO format"""
        return datetime.now().isoformat()

    def import_records(self, table_name, records):
        """Import multiple records into a specified table"""
        if not records:
            return
        
        # Get column names for the specified table
        self.cursor.execute(f"PRAGMA table_info({table_name})")
        columns_info = self.cursor.fetchall()
        column_names = [col[1] for col in columns_info]

        # Exclude primary key if it's auto-incrementing, or handle it based on your schema
        # For this app, all IDs are TEXT PRIMARY KEY, so they should be provided in records

        placeholders = ', '.join(['?' for _ in column_names])
        sql = f"INSERT INTO {table_name} ({', '.join(column_names)}) VALUES ({placeholders})"
        
        try:
            self.cursor.executemany(sql, records)
            self.conn.commit()
        except sqlite3.IntegrityError as e:
            raise ValueError(f"A record with a duplicate ID was found: {e}")
        except sqlite3.Error as e:
            raise Exception(f"Database error during import: {e}")

    def __del__(self):
        self.close() 