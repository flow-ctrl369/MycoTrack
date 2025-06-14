import tkinter as tk
from tkinter import ttk
from ttkthemes import ThemedTk
from database import Database
from agar_plates_tab import AgarPlatesTab
from liquid_culture_tab import LiquidCultureTab
from grain_jars_tab import GrainJarsTab
from bulk_tubs_tab import BulkTubsTab
from clone_library_tab import CloneLibraryTab
from dashboard_tab import DashboardTab
import tkinter.messagebox as messagebox
import sys

class MycoTrackerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("MycoTracker - Psilocybe Cubensis Cultivation Tracker")
        self.root.geometry("1200x800")  # Reduced window size
        self.root.minsize(1000, 600)  # Set minimum window size
        
        # Handle window close event
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

        # Set default font scaling for all widgets
        default_font = tk.font.nametofont("TkDefaultFont")
        default_font.configure(size=14)
        text_font = tk.font.nametofont("TkTextFont")
        text_font.configure(size=14)
        fixed_font = tk.font.nametofont("TkFixedFont")
        fixed_font.configure(size=14)
        heading_font = tk.font.nametofont("TkHeadingFont")
        heading_font.configure(size=16, weight="bold")

        # Initialize database
        self.db = Database()
        
        # Create main container
        self.main_container = ttk.Frame(self.root)
        self.main_container.pack(fill=tk.BOTH, expand=True, padx=20, pady=12)  # More padding
        
        # Create notebook (tabbed interface)
        self.notebook = ttk.Notebook(self.main_container)
        self.notebook.pack(fill=tk.BOTH, expand=True)
        
        # Create tabs
        self.tabs = {
            "Agar Plates": AgarPlatesTab(self.notebook, self.db),
            "Liquid Culture": LiquidCultureTab(self.notebook, self.db),
            "Grain Jars": GrainJarsTab(self.notebook, self.db),
            "Bulk Tubs": BulkTubsTab(self.notebook, self.db),
            "Clone Library": CloneLibraryTab(self.notebook, self.db),
            "Dashboard": DashboardTab(self.notebook, self.db)
        }
        
        # Add tabs to notebook
        for tab_name, tab_frame in self.tabs.items():
            self.notebook.add(tab_frame, text=tab_name)

        # Bind tab change event to refresh function
        self.notebook.bind("<<NotebookTabChanged>>", self.on_tab_change)

    def on_tab_change(self, event):
        selected_tab_name = self.notebook.tab(self.notebook.select(), "text")
        if selected_tab_name in self.tabs:
            current_tab = self.tabs[selected_tab_name]
            if hasattr(current_tab, 'refresh'):
                current_tab.refresh()

    def on_closing(self):
        """Handles the window closing event."""
        if messagebox.askokcancel("Quit", "Do you want to quit?"):
            self.db.close()
            self.root.destroy()
            sys.exit()

def main():
    import tkinter.font as tkfont
    root = ThemedTk(theme="equilux")  # Using a dark theme
    style = ttk.Style(root)
    root.set_theme("equilux")
    style.theme_use("equilux")
    app = MycoTrackerApp(root)
    root.mainloop()

if __name__ == "__main__":
    main() 