import tkinter as tk
from tkinter import ttk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from datetime import datetime, timedelta
import numpy as np

class VisualizationFrame(ttk.Frame):
    def __init__(self, parent, db):
        super().__init__(parent)
        self.db = db
        self.figures = {}  # Cache for figures
        self.setup_ui()

    def setup_ui(self):
        # Create notebook for different visualizations
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        # Create tabs for different visualizations
        self.growth_tab = ttk.Frame(self.notebook)
        self.stats_tab = ttk.Frame(self.notebook)
        self.yield_tab = ttk.Frame(self.notebook)

        self.notebook.add(self.growth_tab, text="Growth Timeline")
        self.notebook.add(self.stats_tab, text="Statistics")
        self.notebook.add(self.yield_tab, text="Yield Analysis")

        # Initialize each tab
        self.setup_growth_timeline()
        self.setup_statistics()
        self.setup_yield_analysis()

        # Bind tab change event
        self.notebook.bind('<<NotebookTabChanged>>', self.on_tab_change)

    def on_tab_change(self, event):
        """Handle tab change events"""
        current_tab = self.notebook.select()
        tab_name = self.notebook.tab(current_tab, "text")
        
        # Only refresh the current tab
        if tab_name == "Growth Timeline":
            self.refresh_growth_timeline()
        elif tab_name == "Statistics":
            self.refresh_statistics()
        elif tab_name == "Yield Analysis":
            self.refresh_yield_analysis()

    def setup_growth_timeline(self):
        # Create figure for growth timeline
        plt.rcParams.update({'font.size': 14})
        fig, ax = plt.subplots(figsize=(10, 6))
        self.figures['growth'] = fig
        canvas = FigureCanvasTkAgg(fig, master=self.growth_tab)
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        self.refresh_growth_timeline()

    def setup_statistics(self):
        # Create figure for statistics
        plt.rcParams.update({'font.size': 14})
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 6))
        self.figures['stats'] = fig
        canvas = FigureCanvasTkAgg(fig, master=self.stats_tab)
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        self.refresh_statistics()

    def setup_yield_analysis(self):
        # Create figure for yield analysis
        plt.rcParams.update({'font.size': 14})
        fig, ax = plt.subplots(figsize=(10, 6))
        self.figures['yield'] = fig
        canvas = FigureCanvasTkAgg(fig, master=self.yield_tab)
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        self.refresh_yield_analysis()

    def refresh_growth_timeline(self):
        fig = self.figures['growth']
        ax = fig.axes[0]
        ax.clear()

        # Get data for the last 30 days
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
            plt.xticks(rotation=45)
        else:
            ax.text(0.5, 0.5, 'No data available for the last 30 days',
                   horizontalalignment='center',
                   verticalalignment='center',
                   transform=ax.transAxes)
            ax.set_title('Colonization Progress (Last 30 Days)')
        
        fig.tight_layout()
        fig.canvas.draw()

    def refresh_statistics(self):
        fig = self.figures['stats']
        ax1, ax2 = fig.axes
        ax1.clear()
        ax2.clear()

        # Contamination rate pie chart
        self.db.cursor.execute('''
            SELECT 
                COUNT(CASE WHEN contamination_notes != '' THEN 1 END) as contaminated,
                COUNT(CASE WHEN contamination_notes = '' THEN 1 END) as clean
            FROM grain_jars
        ''')
        contaminated, clean = self.db.cursor.fetchone()
        
        if contaminated + clean > 0:
            ax1.pie([contaminated, clean], 
                    labels=['Contaminated', 'Clean'],
                    autopct='%1.1f%%',
                    colors=['#ff9999', '#66b3ff'])
            ax1.set_title('Contamination Rate')
        else:
            ax1.text(0.5, 0.5, 'No data available',
                    horizontalalignment='center',
                    verticalalignment='center',
                    transform=ax1.transAxes)
            ax1.set_title('Contamination Rate')

        # Colonization speed histogram
        self.db.cursor.execute('''
            SELECT 
                JULIANDAY(shake_date) - JULIANDAY(inoculation_date) as days_to_colonize
            FROM grain_jars
            WHERE shake_date IS NOT NULL
        ''')
        days_data = [row[0] for row in self.db.cursor.fetchall()]
        
        if days_data:
            ax2.hist(days_data, bins=10, color='green', alpha=0.7)
            ax2.set_title('Colonization Speed Distribution')
            ax2.set_xlabel('Days to Colonize')
            ax2.set_ylabel('Number of Jars')
            ax2.grid(True)
        else:
            ax2.text(0.5, 0.5, 'No data available',
                    horizontalalignment='center',
                    verticalalignment='center',
                    transform=ax2.transAxes)
            ax2.set_title('Colonization Speed Distribution')

        fig.tight_layout()
        fig.canvas.draw()

    def refresh_yield_analysis(self):
        fig = self.figures['yield']
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

            ax.set_title('Yield by Flush')
            ax.set_xlabel('Date to Bulk')
            ax.set_ylabel('Harvest Weight (g)')
            ax.legend()
            ax.grid(True)
            
            # Rotate x-axis labels for better readability
            plt.xticks(rotation=45)
        else:
            ax.text(0.5, 0.5, 'No yield data available',
                   horizontalalignment='center',
                   verticalalignment='center',
                   transform=ax.transAxes)
            ax.set_title('Yield by Flush')
        
        fig.tight_layout()
        fig.canvas.draw()

    def refresh(self):
        """Refresh all visualizations"""
        current_tab = self.notebook.select()
        tab_name = self.notebook.tab(current_tab, "text")
        
        # Only refresh the current tab
        if tab_name == "Growth Timeline":
            self.refresh_growth_timeline()
        elif tab_name == "Statistics":
            self.refresh_statistics()
        elif tab_name == "Yield Analysis":
            self.refresh_yield_analysis() 