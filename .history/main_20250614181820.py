import tkinter as tk
from tkinter import ttk
import sqlite3
from agar_plates_tab import AgarPlatesTab
from liquid_culture_tab import LiquidCultureTab
from grain_jars_tab import GrainJarsTab
from bulk_tubs_tab import BulkTubsTab
from clone_library_tab import CloneLibraryTab
from dashboard_tab import DashboardTab
import os

class MycoTrackerApp:
    def __init__(self, root):
        self.root = root
        
        # Set theme and styles
        self.style = ttk.Style()
        self.style.theme_use('clam')
        
        # Configure custom styles
        self.style.configure('Card.TFrame', background='#ffffff', relief='solid', borderwidth=1)
        self.style.configure('CardTitle.TLabel', font=('Helvetica', 12, 'bold'), background='#ffffff')
        self.style.configure('CardValue.TLabel', font=('Helvetica', 24), background='#ffffff')
        
        # Create database if it doesn't exist
        self.db_path = "mycotracker.db"
        self.create_database()
        
        # Create main container
        self.main_container = ttk.Frame(self.root, padding="10")
        self.main_container.pack(fill=tk.BOTH, expand=True)
        
        # Create notebook (tabbed interface)
        self.notebook = ttk.Notebook(self.main_container)
        self.notebook.pack(fill=tk.BOTH, expand=True)
        
        # Create tabs
        self.dashboard_tab = DashboardTab(self.notebook, self.db_path)
        self.agar_plates_tab = AgarPlatesTab(self.notebook, self.db_path)
        self.liquid_culture_tab = LiquidCultureTab(self.notebook, self.db_path)
        self.grain_jars_tab = GrainJarsTab(self.notebook, self.db_path)
        self.bulk_tubs_tab = BulkTubsTab(self.notebook, self.db_path)
        self.clone_library_tab = CloneLibraryTab(self.notebook, self.db_path)
        
        # Add tabs to notebook
        self.notebook.add(self.dashboard_tab, text="Dashboard")
        self.notebook.add(self.agar_plates_tab, text="Agar Plates")
        self.notebook.add(self.liquid_culture_tab, text="Liquid Culture")
        self.notebook.add(self.grain_jars_tab, text="Grain Jars")
        self.notebook.add(self.bulk_tubs_tab, text="Bulk Tubs")
        self.notebook.add(self.clone_library_tab, text="Clone Library")
        
        # Set up refresh mechanism
        self.setup_refresh()
        
    def create_database(self):
        # Delete existing database if it exists
        if os.path.exists(self.db_path):
            os.remove(self.db_path)
            
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Create agar_plates table
        cursor.execute('''
            CREATE TABLE agar_plates (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                strain_name TEXT NOT NULL,
                date_created TEXT NOT NULL,
                media_type TEXT NOT NULL,
                notes TEXT,
                contamination INTEGER DEFAULT 0,
                date_contaminated TEXT,
                transfer_count INTEGER DEFAULT 0,
                last_transfer_date TEXT,
                storage_location TEXT,
                status TEXT DEFAULT 'Active'
            )
        ''')
        
        # Create liquid_cultures table
        cursor.execute('''
            CREATE TABLE liquid_cultures (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                lc_id TEXT UNIQUE NOT NULL,
                source_id TEXT NOT NULL,
                strain_name TEXT NOT NULL,
                date_created TEXT NOT NULL,
                growth_description TEXT,
                viability TEXT NOT NULL,
                volume_remaining REAL,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
        ''')
        
        # Create grain_jars table
        cursor.execute('''
            CREATE TABLE grain_jars (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                jar_id TEXT UNIQUE NOT NULL,
                source_id TEXT NOT NULL,
                inoculation_date TEXT NOT NULL,
                colonization_percentage INTEGER,
                shake_date TEXT,
                contamination_notes TEXT,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
        ''')
        
        # Create bulk_tubs table
        cursor.execute('''
            CREATE TABLE bulk_tubs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                tub_id TEXT UNIQUE NOT NULL,
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
        
        # Create clone_library table
        cursor.execute('''
            CREATE TABLE clone_library (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                clone_id TEXT UNIQUE NOT NULL,
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
        
        conn.commit()
        conn.close()
        
    def setup_refresh(self):
        def refresh_all():
            # Refresh all tabs
            self.dashboard_tab.load_data()
            self.agar_plates_tab.load_data()
            self.liquid_culture_tab.load_data()
            self.grain_jars_tab.load_data()
            self.bulk_tubs_tab.load_data()
            self.clone_library_tab.load_data()
            
            # Schedule next refresh
            self.root.after(300000, refresh_all)  # Refresh every 5 minutes
            
        # Start refresh cycle
        refresh_all()

if __name__ == "__main__":
    try:
        root = tk.Tk()
        root.title("MycoTracker - Psilocybe Cubensis Cultivation Tracker")
        root.geometry("1200x800")
        app = MycoTrackerApp(root)
        root.mainloop()
    except Exception as e:
        print(f"Error: {str(e)}")
        input("Press Enter to exit...") 