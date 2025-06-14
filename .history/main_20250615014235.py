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
import smtplib
from email.mime.text import MIMEText
import os
from dotenv import load_dotenv
import time # Import time module for delay

# Load environment variables from .env file
load_dotenv()

class SplashScreen(tk.Toplevel):
    def __init__(self, parent):
        tk.Toplevel.__init__(self, parent)
        self.parent = parent
        self.title("Loading MycoTracker...")
        
        # Get the main window's geometry from the parent
        main_geometry = self.parent.geometry()
        self.geometry(main_geometry)

        self.overrideredirect(True) # Remove window decorations
        self.attributes("-topmost", True) # Keep on top
        self.attributes("-alpha", 0.0) # Start fully transparent

        # No need to re-center here, as main_geometry already contains position
        self.update_idletasks()

        ttk.Label(self, text="Loading MycoTracker...", font=("TkDefaultFont", 18, "bold")).pack(expand=True)

        self.fade_in()

    def fade_in(self):
        alpha = self.attributes("-alpha")
        if alpha < 1.0:
            alpha += 0.05 # Increment transparency
            self.attributes("-alpha", alpha)
            self.after(50, self.fade_in) # Call fade_in again after 50ms
        else:
            # Once fully faded in, keep it for a moment, then fade out or destroy
            self.after(1000, self.fade_out) # Keep for 1 second, then start fading out

    def fade_out(self):
        alpha = self.attributes("-alpha")
        if alpha > 0.0:
            alpha -= 0.05 # Decrement transparency
            self.attributes("-alpha", alpha)
            self.after(50, self.fade_out) # Call fade_out again after 50ms
        else:
            self.destroy() # Destroy splash screen when fully transparent

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

    def send_email_notification(self, recipient_email, task, reminder_date, reminder_time, recurrence_type, recurrence_interval, recurrence_end_date, priority, notes, category):
        sender_email = os.getenv("SENDER_EMAIL")
        sender_password = os.getenv("SENDER_PASSWORD")
        smtp_server = os.getenv("SMTP_SERVER")
        smtp_port = int(os.getenv("SMTP_PORT")) # Convert port to integer

        if not all([sender_email, sender_password, smtp_server, smtp_port]):
            messagebox.showerror("Configuration Error", "Email sender credentials are not fully configured in .env file.")
            return

        subject = f"MycoTracker Reminder: {task}"
        
        # Build a more detailed email body
        body = f"""
Dear User,

This is a reminder from your MycoTracker application for the following task:

Task: {task}
Date: {reminder_date}
Time: {reminder_time}
Category: {category}
Priority: {priority}

"""
        if recurrence_type != 'None':
            recurrence_info = f"Recurrence: {recurrence_type} every {recurrence_interval} "
            if recurrence_type == 'Daily':
                recurrence_info += "day(s)"
            elif recurrence_type == 'Weekly':
                recurrence_info += "week(s)"
            elif recurrence_type == 'Monthly':
                recurrence_info += "month(s)"
            
            if recurrence_end_date:
                recurrence_info += f" until {recurrence_end_date}"
            body += f"{recurrence_info}\n"

        if notes:
            body += f"Notes: {notes}\n"

        body += f"""

To manage your reminders, please open the MycoTracker application.

Best regards,
MycoTracker App
"""

        msg = MIMEText(body)
        msg['Subject'] = subject
        msg['From'] = sender_email
        msg['To'] = recipient_email

        try:
            with smtplib.SMTP(smtp_server, smtp_port) as server:
                server.starttls() # Secure the connection
                server.login(sender_email, sender_password)
                server.send_message(msg)
            print(f"Email reminder sent to {recipient_email} for task: {task}")
        except Exception as e:
            print(f"Failed to send email reminder to {recipient_email}: {e}")
            messagebox.showerror("Email Error", f"Failed to send email to {recipient_email} for task {task}: {e}")

    def check_for_reminders(self):
        now = datetime.now()
        current_date = now.strftime('%Y-%m-%d')
        current_time = now.strftime('%H:%M')

        # Select all active reminders that are due
        reminders_to_check = self.db.cursor.execute('''
            SELECT id, task, reminder_date, reminder_time, recurrence_type, recurrence_interval, recurrence_end_date, send_email, email_address, priority, notes, category
            FROM reminders
            WHERE completed = 0 AND (reminder_date < ? OR (reminder_date = ? AND reminder_time <= ?))
            ORDER BY reminder_date, reminder_time
        ''', (current_date, current_date, current_time)).fetchall()

        for reminder_id, task, reminder_date_str, reminder_time_str, recurrence_type, recurrence_interval, recurrence_end_date_str, send_email, email_address, priority, notes, category in reminders_to_check:
            # Construct datetime objects for comparison
            reminder_datetime = datetime.strptime(f"{reminder_date_str} {reminder_time_str}", '%Y-%m-%d %H:%M')

            messagebox.showinfo("Reminder", f"Reminder: {task} at {reminder_time_str} on {reminder_date_str}")

            # Send email notification if enabled and email address is provided
            if send_email == 1 and email_address:
                self.send_email_notification(email_address, task, reminder_date_str, reminder_time_str, recurrence_type, recurrence_interval, recurrence_end_date_str, priority, notes, category)

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
    root = ThemedTk(theme="equilux")
    
    # Set main window geometry and center it before splash screen
    app_width = 1200
    app_height = 800
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()

    x = (screen_width - app_width) // 2
    y = (screen_height - app_height) // 2

    root.geometry(f"{app_width}x{app_height}+{x}+{y}")
    root.withdraw() # Hide the main window initially

    # Pass root to splash screen, so it can inherit geometry
    splash = SplashScreen(root)
    root.wait_window(splash) # Wait for the splash screen to close

    style = ttk.Style(root)
    root.set_theme("equilux")
    style.theme_use("equilux")
    
    app = MycoTrackerApp(root)
    root.deiconify() # Show the main window after splash screen is done
    root.mainloop() 