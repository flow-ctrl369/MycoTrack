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
from reminders_tab import RemindersTab
import tkinter.messagebox as messagebox
import sys
from datetime import datetime, timedelta
import calendar
import playsound # New import

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
            "Dashboard": DashboardTab(self.notebook, self.db),
            "Reminders": RemindersTab(self.notebook, self.db)
        }
        
        # Add tabs to notebook
        for tab_name, tab_frame in self.tabs.items():
            self.notebook.add(tab_frame, text=tab_name)

        # Bind tab change event to refresh function
        self.notebook.bind("<<NotebookTabChanged>>", self.on_tab_change)

        # Start reminder checking
        self.check_for_reminders()

    def on_tab_change(self, event):
        selected_tab_name = self.notebook.tab(self.notebook.select(), "text")
        if selected_tab_name in self.tabs:
            current_tab = self.tabs[selected_tab_name]
            if hasattr(current_tab, 'refresh'):
                current_tab.refresh()

    def check_for_reminders(self):
        now = datetime.now()
        current_date = now.strftime('%Y-%m-%d')
        current_time = now.strftime('%H:%M')

        # Select all active reminders that are due
        reminders_to_check = self.db.cursor.execute('''
            SELECT id, task, reminder_date, reminder_time, recurrence_type, recurrence_interval, recurrence_end_date, sound_file
            FROM reminders
            WHERE completed = 0 AND (reminder_date < ? OR (reminder_date = ? AND reminder_time <= ?))
            ORDER BY reminder_date, reminder_time
        ''', (current_date, current_date, current_time)).fetchall()

        for reminder_id, task, reminder_date_str, reminder_time_str, recurrence_type, recurrence_interval, recurrence_end_date_str, sound_file_path in reminders_to_check:
            # Construct datetime objects for comparison
            reminder_datetime = datetime.strptime(f"{reminder_date_str} {reminder_time_str}", '%Y-%m-%d %H:%M')

            messagebox.showinfo("Reminder", f"Reminder: {task} at {reminder_time_str} on {reminder_date_str}")

            if sound_file_path: # Play sound if a file is specified
                try:
                    playsound.playsound(sound_file_path)
                except Exception as e:
                    print(f"Error playing sound {sound_file_path}: {e}") # Log error, don't block app

            if recurrence_type == 'None':
                # Non-recurring reminder: mark as completed and notified
                self.db.cursor.execute("UPDATE reminders SET notified = 1, completed = 1 WHERE id = ?", (reminder_id,))
            else:
                # Recurring reminder: calculate next occurrence and update
                next_reminder_date = datetime.strptime(reminder_date_str, '%Y-%m-%d').date()
                if recurrence_type == 'Daily':
                    next_reminder_date += timedelta(days=recurrence_interval)
                elif recurrence_type == 'Weekly':
                    next_reminder_date += timedelta(weeks=recurrence_interval)
                elif recurrence_type == 'Monthly':
                    # Handle monthly recurrence, adjusting for month-end day overflows
                    next_month = next_reminder_date.month + recurrence_interval
                    next_year = next_reminder_date.year + (next_month - 1) // 12
                    next_month = (next_month - 1) % 12 + 1
                    
                    try:
                        next_reminder_date = next_reminder_date.replace(year=next_year, month=next_month)
                    except ValueError: # day is out of range for month
                        # Go to the last day of the next month
                        max_day = calendar.monthrange(next_year, next_month)[1]
                        next_reminder_date = next_reminder_date.replace(year=next_year, month=next_month, day=max_day)

                # Check against recurrence end date
                if recurrence_end_date_str and next_reminder_date > datetime.strptime(recurrence_end_date_str, '%Y-%m-%d').date():
                    # Recurrence ends, mark as completed
                    self.db.cursor.execute("UPDATE reminders SET completed = 1 WHERE id = ?", (reminder_id,))
                else:
                    # Continue recurrence, update reminder date and reset notified status
                    self.db.cursor.execute("UPDATE reminders SET reminder_date = ?, reminder_time = ?, notified = 0 WHERE id = ?",
                                           (next_reminder_date.strftime('%Y-%m-%d'), reminder_time_str, reminder_id))
            self.db.conn.commit()

        # Schedule the next check in 60 seconds
        self.root.after(60000, self.check_for_reminders) # Check every minute

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