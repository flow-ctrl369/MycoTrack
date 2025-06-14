import tkinter as tk
from tkinter import ttk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from datetime import datetime, timedelta
import numpy as np # New import for numpy

class DashboardTab(ttk.Frame):
    def __init__(self, parent, db):
        super().__init__(parent)
        self.db = db
        self.figures = {} # To store matplotlib figures
        self.setup_ui()

    def setup_ui(self):
        # Main notebook for dashboard sections
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        # Summary tab
        self.summary_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.summary_tab, text="Overview")

        # Add welcome message to summary tab
        ttk.Label(self.summary_tab, text="Welcome to your MycoTracker Dashboard!").pack(pady=20)
        
        # Placeholder for summary statistics
        self.summary_frame = ttk.LabelFrame(self.summary_tab, text="Summary Statistics")
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

        # Visualizations tab (now a notebook)
        self.visualizations_notebook = ttk.Notebook(self.notebook) # Nested notebook
        self.notebook.add(self.visualizations_notebook, text="Visualizations")

        # Sub-tabs within Visualizations
        self.record_distribution_tab = ttk.Frame(self.visualizations_notebook)
        self.visualizations_notebook.add(self.record_distribution_tab, text="Record Distribution")
        self.setup_record_distribution_chart()

        self.growth_timeline_tab = ttk.Frame(self.visualizations_notebook)
        self.visualizations_notebook.add(self.growth_timeline_tab, text="Growth Timeline")
        self.setup_growth_timeline_chart()

        self.statistics_tab = ttk.Frame(self.visualizations_notebook) # New sub-tab
        self.visualizations_notebook.add(self.statistics_tab, text="Statistics")
        self.setup_statistics_chart()

        self.yield_analysis_tab = ttk.Frame(self.visualizations_notebook) # New sub-tab
        self.visualizations_notebook.add(self.yield_analysis_tab, text="Yield Analysis")
        self.setup_yield_analysis_chart()

        # Bind internal tab change event
        self.visualizations_notebook.bind('<<NotebookTabChanged>>', self.on_internal_tab_change)

    def on_internal_tab_change(self, event):
        current_tab = self.visualizations_notebook.select() # Changed to use internal notebook
        tab_name = self.visualizations_notebook.tab(current_tab, "text")
        if tab_name == "Record Distribution":
            self.refresh_record_distribution_chart()
        elif tab_name == "Growth Timeline":
            self.refresh_growth_timeline_chart()
        elif tab_name == "Statistics": # New condition
            self.refresh_statistics_chart()
        elif tab_name == "Yield Analysis": # New condition
            self.refresh_yield_analysis_chart()
        # Add more conditions for other visualization tabs as they are added

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

    def setup_record_distribution_chart(self):
        plt.rcParams.update({'font.size': 10})
        fig, ax = plt.subplots(figsize=(6, 6))
        self.figures['record_distribution'] = fig
        canvas = FigureCanvasTkAgg(fig, master=self.record_distribution_tab) # Changed master
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        self.refresh_record_distribution_chart()

    def refresh_record_distribution_chart(self):
        fig = self.figures['record_distribution']
        ax = fig.axes[0]
        ax.clear()

        # Fetch counts from the database
        counts = {
            "Agar Plates": self.db.cursor.execute("SELECT COUNT(*) FROM agar_plates").fetchone()[0],
            "Liquid Cultures": self.db.cursor.execute("SELECT COUNT(*) FROM liquid_cultures").fetchone()[0],
            "Grain Jars": self.db.cursor.execute("SELECT COUNT(*) FROM grain_jars").fetchone()[0],
            "Bulk Tubs": self.db.cursor.execute("SELECT COUNT(*) FROM bulk_tubs").fetchone()[0],
            "Clone Library": self.db.cursor.execute("SELECT COUNT(*) FROM clone_library WHERE archived = 0").fetchone()[0]
        }

        labels = [k for k, v in counts.items() if v > 0]
        sizes = [v for k, v in counts.items() if v > 0]

        if sizes:
            ax.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=90)
            ax.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.
            ax.set_title('Record Distribution by Category')
        else:
            ax.text(0.5, 0.5, 'No data available',
                   horizontalalignment='center',
                   verticalalignment='center',
                   transform=ax.transAxes)
            ax.set_title('Record Distribution by Category')

        fig.tight_layout()
        fig.canvas.draw()

    def setup_growth_timeline_chart(self):
        plt.rcParams.update({'font.size': 10})
        fig, ax = plt.subplots(figsize=(10, 6))
        self.figures['growth_timeline'] = fig
        canvas = FigureCanvasTkAgg(fig, master=self.growth_timeline_tab)
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        self.refresh_growth_timeline_chart()

    def refresh_growth_timeline_chart(self):
        fig = self.figures['growth_timeline']
        ax = fig.axes[0]
        ax.clear()

        # Get data for the last 30 days (or all data if less than 30 days)
        end_date = datetime.now()
        start_date = end_date - timedelta(days=30)
        
        self.db.cursor.execute('''
            SELECT inoculation_date, colonization_percentage
            FROM grain_jars
            WHERE inoculation_date >= ?
            ORDER BY inoculation_date
        ''', (start_date.isoformat(),))
        
        data = self.db.cursor.fetchall()
        
        if data:
            dates = [datetime.fromisoformat(row[0]) for row in data]
            percentages = [row[1] for row in data]

            # Plot data
            ax.plot(dates, percentages, 'b-', marker='o')
            ax.set_title('Colonization Progress (Last 30 Days)')
            ax.set_xlabel('Date')
            ax.set_ylabel('Colonization %')
            ax.grid(True)
            
            # Rotate x-axis labels for better readability
            fig.autofmt_xdate() # Auto-format dates
        else:
            ax.text(0.5, 0.5, 'No data available for the last 30 days',
                   horizontalalignment='center',
                   verticalalignment='center',
                   transform=ax.transAxes)
            ax.set_title('Colonization Progress (Last 30 Days)')
        
        fig.tight_layout()
        fig.canvas.draw()

    def setup_statistics_chart(self):
        plt.rcParams.update({'font.size': 10})
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 6))
        self.figures['statistics'] = fig
        canvas = FigureCanvasTkAgg(fig, master=self.statistics_tab)
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        self.refresh_statistics_chart()

    def refresh_statistics_chart(self):
        fig = self.figures['statistics']
        ax1, ax2 = fig.axes
        ax1.clear()
        ax2.clear()

        # Contamination rate pie chart
        self.db.cursor.execute('''
            SELECT 
                COUNT(CASE WHEN contamination_notes != '' THEN 1 END) as contaminated,
                COUNT(CASE WHEN contamination_notes = '' OR contamination_notes IS NULL THEN 1 END) as clean
            FROM grain_jars
        ''')
        contaminated, clean = self.db.cursor.fetchone()
        
        if contaminated + clean > 0:
            ax1.pie([contaminated, clean], 
                    labels=['Contaminated', 'Clean'],
                    autopct='%1.1f%%',
                    colors=['#ff9999', '#66b3ff'])
            ax1.set_title('Contamination Rate (Grain Jars)')
        else:
            ax1.text(0.5, 0.5, 'No data available',
                    horizontalalignment='center',
                    verticalalignment='center',
                    transform=ax1.transAxes)
            ax1.set_title('Contamination Rate (Grain Jars)')

        # Colonization speed histogram
        self.db.cursor.execute('''
            SELECT 
                JULIANDAY(shake_date) - JULIANDAY(inoculation_date) as days_to_colonize
            FROM grain_jars
            WHERE shake_date IS NOT NULL AND inoculation_date IS NOT NULL
        ''')
        days_data = [row[0] for row in self.db.cursor.fetchall() if row[0] is not None]
        
        if days_data:
            ax2.hist(days_data, bins=10, color='green', alpha=0.7)
            ax2.set_title('Colonization Speed Distribution (Grain Jars)')
            ax2.set_xlabel('Days to Colonize')
            ax2.set_ylabel('Number of Jars')
            ax2.grid(True)
        else:
            ax2.text(0.5, 0.5, 'No data available',
                    horizontalalignment='center',
                    verticalalignment='center',
                    transform=ax2.transAxes)
            ax2.set_title('Colonization Speed Distribution (Grain Jars)')

        fig.tight_layout()
        fig.canvas.draw()

    def setup_yield_analysis_chart(self):
        plt.rcParams.update({'font.size': 10})
        fig, ax = plt.subplots(figsize=(10, 6))
        self.figures['yield_analysis'] = fig
        canvas = FigureCanvasTkAgg(fig, master=self.yield_analysis_tab)
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        self.refresh_yield_analysis_chart()

    def refresh_yield_analysis_chart(self):
        fig = self.figures['yield_analysis']
        ax = fig.axes[0]
        ax.clear()

        # Get yield data from bulk tubs
        self.db.cursor.execute('''
            SELECT 
                date_to_bulk,
                harvest_weight_flush1,
                harvest_weight_flush2,
                harvest_weight_flush3
            FROM bulk_tubs
            WHERE date_to_bulk IS NOT NULL
            ORDER BY date_to_bulk
        ''')
        
        data = self.db.cursor.fetchall()
        
        if data:
            dates = [datetime.fromisoformat(row[0]) for row in data]
            flush1 = [row[1] or 0 for row in data]
            flush2 = [row[2] or 0 for row in data]
            flush3 = [row[3] or 0 for row in data]

            # Plot stacked bar chart
            ax.bar(dates, flush1, label='Flush 1', color='#2ecc71')
            ax.bar(dates, flush2, bottom=flush1, label='Flush 2', color='#3498db')
            ax.bar(dates, flush3, bottom=[f1 + f2 for f1, f2 in zip(flush1, flush2)], 
                   label='Flush 3', color='#9b59b6')

            ax.set_title('Yield by Flush (Bulk Tubs)')
            ax.set_xlabel('Date to Bulk')
            ax.set_ylabel('Harvest Weight (g)')
            ax.legend()
            ax.grid(True)
            
            # Rotate x-axis labels for better readability
            fig.autofmt_xdate()
        else:
            ax.text(0.5, 0.5, 'No yield data available',
                   horizontalalignment='center',
                   verticalalignment='center',
                   transform=ax.transAxes)
            ax.set_title('Yield by Flush (Bulk Tubs)')
        
        fig.tight_layout()
        fig.canvas.draw()

    def refresh(self):
        self.load_summary_data()
        # Refresh the currently visible sub-tab within the dashboard
        current_main_tab_name = self.notebook.tab(self.notebook.select(), "text")
        if current_main_tab_name == "Visualizations":
            current_sub_tab = self.visualizations_notebook.select()
            sub_tab_name = self.visualizations_notebook.tab(current_sub_tab, "text")
            if sub_tab_name == "Record Distribution":
                self.refresh_record_distribution_chart()
            elif sub_tab_name == "Growth Timeline":
                self.refresh_growth_timeline_chart()
            elif sub_tab_name == "Statistics": # New refresh call
                self.refresh_statistics_chart()
            elif sub_tab_name == "Yield Analysis": # New refresh call
                self.refresh_yield_analysis_chart()
            # Add more refresh calls for other visualization tabs as they are added 