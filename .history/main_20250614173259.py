import tkinter as tk
from tkinter import ttk
from ttkthemes import ThemedTk
from database import Database
from agar_plates_tab import AgarPlatesTab
from liquid_culture_tab import LiquidCultureTab
from grain_jars_tab import GrainJarsTab
from bulk_tubs_tab import BulkTubsTab
from clone_library_tab import CloneLibraryTab
from theme_manager import ThemeManager

class MycoTrackerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("MycoTracker - Psilocybe Cubensis Cultivation Tracker")
        self.root.geometry("1200x800")
        
        # Initialize database
        self.db = Database()
        
        # Initialize theme manager
        self.theme_manager = ThemeManager(self.root)
        
        # Create main container
        self.main_container = ttk.Frame(self.root)
        self.main_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Create header frame for theme toggle
        self.header_frame = ttk.Frame(self.main_container)
        self.header_frame.pack(fill=tk.X, pady=(0, 5))
        
        # Add theme toggle button
        self.theme_button = ttk.Button(
            self.header_frame,
            text="🌙 Dark Mode",
            command=self.toggle_theme
        )
        self.theme_button.pack(side=tk.RIGHT)
        
        # Create notebook (tabbed interface)
        self.notebook = ttk.Notebook(self.main_container)
        self.notebook.pack(fill=tk.BOTH, expand=True)
        
        # Create tabs
        self.tabs = {
            "Agar Plates": AgarPlatesTab(self.notebook, self.db),
            "Liquid Culture": LiquidCultureTab(self.notebook, self.db),
            "Grain Jars": GrainJarsTab(self.notebook, self.db),
            "Bulk Tubs": BulkTubsTab(self.notebook, self.db),
            "Clone Library": CloneLibraryTab(self.notebook, self.db)
        }
        
        # Add tabs to notebook
        for tab_name, tab_frame in self.tabs.items():
            self.notebook.add(tab_frame, text=tab_name)

    def toggle_theme(self):
        """Toggle between light and dark mode"""
        is_dark = self.theme_manager.toggle_theme()
        self.theme_button.configure(text="☀️ Light Mode" if is_dark else "🌙 Dark Mode")

def main():
    root = ThemedTk(theme="arc")  # Using a clean, modern theme
    app = MycoTrackerApp(root)
    root.mainloop()

if __name__ == "__main__":
    main() 