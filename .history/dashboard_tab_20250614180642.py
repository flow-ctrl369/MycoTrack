import tkinter as tk
from tkinter import ttk
import sqlite3
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import pandas as pd
from tkcalendar import Calendar
from tkinter import messagebox

class DashboardTab(ttk.Frame):
    def __init__(self, parent, db_path):
        super().__init__(parent)
        self.db_path = db_path
        
        # Create main container with padding
        self.main_container = ttk.Frame(self, padding="10")
        self.main_container.pack(fill=tk.BOTH, expand=True)
        
        # Create top row for summary cards
        self.summary_frame = ttk.Frame(self.main_container)
        self.summary_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Create summary cards
        self.create_summary_cards()
        
        # Create bottom row for charts
        self.charts_frame = ttk.Frame(self.main_container)
        self.charts_frame.pack(fill=tk.BOTH, expand=True)
        
        # Create charts
        self.create_charts()
        
        # Initial data load
        self.load_data()
        
    def create_summary_cards(self):
        # Create 4 summary cards
        self.cards = []
        for i in range(4):
            card = ttk.Frame(self.summary_frame, style='Card.TFrame')
            card.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5)
            
            # Title
            title = ttk.Label(card, text="", style='CardTitle.TLabel')
            title.pack(pady=(10, 5))
            
            # Value
            value = ttk.Label(card, text="0", style='CardValue.TLabel')
            value.pack(pady=(0, 10))
            
            self.cards.append((title, value))
            
    def create_charts(self):
        # Create left and right chart containers
        left_frame = ttk.Frame(self.charts_frame)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5)
        
        right_frame = ttk.Frame(self.charts_frame)
        right_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5)
        
        # Create charts
        self.create_growth_chart(left_frame)
        self.create_success_rate_chart(right_frame)
        
    def create_growth_chart(self, parent):
        # Create figure for growth chart
        self.growth_fig = plt.Figure(figsize=(6, 4), dpi=100)
        self.growth_ax = self.growth_fig.add_subplot(111)
        self.growth_canvas = FigureCanvasTkAgg(self.growth_fig, parent)
        self.growth_canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
    def create_success_rate_chart(self, parent):
        # Create figure for success rate chart
        self.success_fig = plt.Figure(figsize=(6, 4), dpi=100)
        self.success_ax = self.success_fig.add_subplot(111)
        self.success_canvas = FigureCanvasTkAgg(self.success_fig, parent)
        self.success_canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
    def load_data(self):
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Get total counts
            cursor.execute("SELECT COUNT(*) FROM agar_plates")
            agar_count = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM liquid_cultures")
            lc_count = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM grain_jars")
            grain_count = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM bulk_tubs")
            tub_count = cursor.fetchone()[0]
            
            # Update summary cards
            self.cards[0][0].config(text="Agar Plates")
            self.cards[0][1].config(text=str(agar_count))
            
            self.cards[1][0].config(text="Liquid Cultures")
            self.cards[1][1].config(text=str(lc_count))
            
            self.cards[2][0].config(text="Grain Jars")
            self.cards[2][1].config(text=str(grain_count))
            
            self.cards[3][0].config(text="Bulk Tubs")
            self.cards[3][1].config(text=str(tub_count))
            
            # Get growth data for charts
            self.update_growth_chart(cursor)
            self.update_success_rate_chart(cursor)
            
            conn.close()
            
        except sqlite3.Error as e:
            messagebox.showerror("Database Error", f"Error loading dashboard data: {str(e)}")
            
    def update_growth_chart(self, cursor):
        # Clear previous data
        self.growth_ax.clear()
        
        # Get data for last 30 days
        end_date = datetime.now()
        start_date = end_date - timedelta(days=30)
        
        # Query for agar plates
        cursor.execute("""
            SELECT date_created, COUNT(*) 
            FROM agar_plates 
            WHERE date_created BETWEEN ? AND ?
            GROUP BY date_created
        """, (start_date.strftime('%Y-%m-%d'), end_date.strftime('%Y-%m-%d')))
        agar_data = cursor.fetchall()
        
        # Query for liquid cultures
        cursor.execute("""
            SELECT date_created, COUNT(*) 
            FROM liquid_cultures 
            WHERE date_created BETWEEN ? AND ?
            GROUP BY date_created
        """, (start_date.strftime('%Y-%m-%d'), end_date.strftime('%Y-%m-%d')))
        lc_data = cursor.fetchall()
        
        # Plot data
        dates = pd.date_range(start=start_date, end=end_date)
        agar_counts = pd.Series(0, index=dates)
        lc_counts = pd.Series(0, index=dates)
        
        for date, count in agar_data:
            agar_counts[date] = count
        for date, count in lc_data:
            lc_counts[date] = count
            
        self.growth_ax.plot(dates, agar_counts, label='Agar Plates', marker='o')
        self.growth_ax.plot(dates, lc_counts, label='Liquid Cultures', marker='s')
        
        self.growth_ax.set_title('Growth Over Time')
        self.growth_ax.set_xlabel('Date')
        self.growth_ax.set_ylabel('Count')
        self.growth_ax.legend()
        self.growth_ax.grid(True)
        
        # Rotate x-axis labels
        plt.setp(self.growth_ax.get_xticklabels(), rotation=45)
        
        self.growth_fig.tight_layout()
        self.growth_canvas.draw()
        
    def update_success_rate_chart(self, cursor):
        # Clear previous data
        self.success_ax.clear()
        
        # Get success rates
        cursor.execute("""
            SELECT 
                COUNT(*) as total,
                SUM(CASE WHEN contamination = 0 THEN 1 ELSE 0 END) as success
            FROM agar_plates
        """)
        agar_stats = cursor.fetchone()
        agar_success_rate = (agar_stats[1] / agar_stats[0] * 100) if agar_stats[0] > 0 else 0
        
        cursor.execute("""
            SELECT 
                COUNT(*) as total,
                SUM(CASE WHEN contamination = 0 THEN 1 ELSE 0 END) as success
            FROM liquid_cultures
        """)
        lc_stats = cursor.fetchone()
        lc_success_rate = (lc_stats[1] / lc_stats[0] * 100) if lc_stats[0] > 0 else 0
        
        # Create bar chart
        categories = ['Agar Plates', 'Liquid Cultures']
        success_rates = [agar_success_rate, lc_success_rate]
        
        bars = self.success_ax.bar(categories, success_rates)
        
        # Add value labels on top of bars
        for bar in bars:
            height = bar.get_height()
            self.success_ax.text(bar.get_x() + bar.get_width()/2., height,
                               f'{height:.1f}%',
                               ha='center', va='bottom')
        
        self.success_ax.set_title('Success Rate by Category')
        self.success_ax.set_ylabel('Success Rate (%)')
        self.success_ax.set_ylim(0, 100)
        self.success_ax.grid(True, axis='y')
        
        self.success_fig.tight_layout()
        self.success_canvas.draw() 