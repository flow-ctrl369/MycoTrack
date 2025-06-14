import tkinter as tk
from tkinter import ttk

class DashboardTab(ttk.Frame):
    def __init__(self, parent, db):
        super().__init__(parent)
        self.db = db
        self.setup_ui()

    def setup_ui(self):
        ttk.Label(self, text="Welcome to your MycoTracker Dashboard!").pack(pady=20)
        
        # Placeholder for summary statistics
        self.summary_frame = ttk.LabelFrame(self, text="Summary Statistics")
        self.summary_frame.pack(fill=tk.X, padx=10, pady=10)

        self.total_agar_plates_label = ttk.Label(self.summary_frame, text="Total Agar Plates: ")
        self.total_agar_plates_label.pack(anchor=tk.W, padx=10, pady=2)

        self.total_liquid_cultures_label = ttk.Label(self.summary_frame, text="Total Liquid Cultures: ")
        self.total_liquid_cultures_label.pack(anchor=tk.W, padx=10, pady=2)

        self.total_grain_jars_label = ttk.Label(self.summary_frame, text="Total Grain Jars: ")
        self.total_grain_jars_label.pack(anchor=tk.W, padx=10, pady=2)

        self.total_bulk_tubs_label = ttk.Label(self.summary_frame, text="Total Bulk Tubs: ")
        self.total_bulk_tubs_label.pack(anchor=tk.W, padx=10, pady=2)

        self.total_clones_label = ttk.Label(self.summary_frame, text="Total Clones: ")
        self.total_clones_label.pack(anchor=tk.W, padx=10, pady=2)

        self.load_summary_data()

    def load_summary_data(self):
        # Fetch counts from the database
        total_agar = self.db.cursor.execute("SELECT COUNT(*) FROM agar_plates").fetchone()[0]
        total_liquid = self.db.cursor.execute("SELECT COUNT(*) FROM liquid_cultures").fetchone()[0]
        total_grain = self.db.cursor.execute("SELECT COUNT(*) FROM grain_jars").fetchone()[0]
        total_bulk = self.db.cursor.execute("SELECT COUNT(*) FROM bulk_tubs").fetchone()[0]
        total_clones = self.db.cursor.execute("SELECT COUNT(*) FROM clone_library WHERE archived = 0").fetchone()[0]

        self.total_agar_plates_label.config(text=f"Total Agar Plates: {total_agar}")
        self.total_liquid_cultures_label.config(text=f"Total Liquid Cultures: {total_liquid}")
        self.total_grain_jars_label.config(text=f"Total Grain Jars: {total_grain}")
        self.total_bulk_tubs_label.config(text=f"Total Bulk Tubs: {total_bulk}")
        self.total_clones_label.config(text=f"Total Clones: {total_clones}")

    def refresh(self):
        self.load_summary_data() 