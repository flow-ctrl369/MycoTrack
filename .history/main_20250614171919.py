import tkinter as tk
from tkinter import ttk
from ttkthemes import ThemedTk
from database import Database
from agar_plates_tab import AgarPlatesTab
from liquid_culture_tab import LiquidCultureTab

class MycoTrackerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("MycoTracker - Psilocybe Cubensis Cultivation Tracker")
        self.root.geometry("1200x800")
        
        # Initialize database
        self.db = Database()
        
        # Create main container
        self.main_container = ttk.Frame(self.root)
        self.main_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Create notebook (tabbed interface)
        self.notebook = ttk.Notebook(self.main_container)
        self.notebook.pack(fill=tk.BOTH, expand=True)
        
        # Create tabs
        self.tabs = {
            "Agar Plates": AgarPlatesTab(self.notebook, self.db),
            "Liquid Culture": LiquidCultureTab(self.notebook, self.db),
            "Grain Jars": self.create_grain_jars_tab(),
            "Bulk Tubs": self.create_bulk_tubs_tab(),
            "Clone Library": self.create_clone_library_tab()
        }
        
        # Add tabs to notebook
        for tab_name, tab_frame in self.tabs.items():
            self.notebook.add(tab_frame, text=tab_name)

    def create_grain_jars_tab(self):
        """Create the Grain Jars tab"""
        frame = ttk.Frame(self.notebook)
        # TODO: Implement grain jars tab content
        return frame

    def create_bulk_tubs_tab(self):
        """Create the Bulk Tubs tab"""
        frame = ttk.Frame(self.notebook)
        # TODO: Implement bulk tubs tab content
        return frame

    def create_clone_library_tab(self):
        """Create the Clone Library tab"""
        frame = ttk.Frame(self.notebook)
        # TODO: Implement clone library tab content
        return frame

def main():
    root = ThemedTk(theme="arc")  # Using a clean, modern theme
    app = MycoTrackerApp(root)
    root.mainloop()

if __name__ == "__main__":
    main() 