import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime, timedelta

class RemindersTab(ttk.Frame):
    def __init__(self, parent, db):
        super().__init__(parent)
        self.db = db
        self.show_completed = False  # Track whether we're showing completed reminders
        self.current_filter = "All"  # Track current filter
        self.setup_ui()

    def setup_ui(self):
        # Reminder Entry Form
        form_frame = ttk.LabelFrame(self, text="Add New Reminder")
        form_frame.pack(padx=10, pady=10, fill=tk.X)

        ttk.Label(form_frame, text="Task:").grid(row=0, column=0, padx=5, pady=2, sticky=tk.W)
        self.task_entry = ttk.Entry(form_frame, width=50)
        self.task_entry.grid(row=0, column=1, padx=5, pady=2, sticky=tk.EW)

        ttk.Label(form_frame, text="Date (YYYY-MM-DD):").grid(row=1, column=0, padx=5, pady=2, sticky=tk.W)
        self.date_entry = ttk.Entry(form_frame, width=20)
        self.date_entry.grid(row=1, column=1, padx=5, pady=2, sticky=tk.W)

        ttk.Label(form_frame, text="Time (HH:MM - 24hr):").grid(row=2, column=0, padx=5, pady=2, sticky=tk.W)
        self.time_entry = ttk.Entry(form_frame, width=20)
        self.time_entry.grid(row=2, column=1, padx=5, pady=2, sticky=tk.W)

        # Recurrence Options
        ttk.Label(form_frame, text="Recurrence:").grid(row=4, column=0, padx=5, pady=2, sticky=tk.W)
        self.recurrence_type_var = tk.StringVar(value="None")
        self.recurrence_type_dropdown = ttk.Combobox(form_frame, textvariable=self.recurrence_type_var,
                                                   values=["None", "Daily", "Weekly", "Monthly"],
                                                   state="readonly", width=15)
        self.recurrence_type_dropdown.grid(row=4, column=1, padx=5, pady=2, sticky=tk.W)

        ttk.Label(form_frame, text="Interval:").grid(row=5, column=0, padx=5, pady=2, sticky=tk.W)
        self.recurrence_interval_entry = ttk.Entry(form_frame, width=10)
        self.recurrence_interval_entry.grid(row=5, column=1, padx=5, pady=2, sticky=tk.W)
        self.recurrence_interval_entry.insert(0, "1") # Default to 1

        ttk.Label(form_frame, text="End Date (YYYY-MM-DD - optional):").grid(row=6, column=0, padx=5, pady=2, sticky=tk.W)
        self.recurrence_end_date_entry = ttk.Entry(form_frame, width=20)
        self.recurrence_end_date_entry.grid(row=6, column=1, padx=5, pady=2, sticky=tk.W)

        # Priority Option
        ttk.Label(form_frame, text="Priority:").grid(row=3, column=0, padx=5, pady=2, sticky=tk.W)
        self.priority_var = tk.StringVar(value="Medium")
        self.priority_dropdown = ttk.Combobox(form_frame, textvariable=self.priority_var,
                                              values=["High", "Medium", "Low"],
                                              state="readonly", width=15)
        self.priority_dropdown.grid(row=3, column=1, padx=5, pady=2, sticky=tk.W)

        add_button = ttk.Button(form_frame, text="Add Reminder", command=self.add_reminder)
        add_button.grid(row=7, column=0, columnspan=2, pady=10)

        # Reminders List
        list_frame = ttk.LabelFrame(self, text="Pending Reminders")
        list_frame.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

        # View toggle and filter controls
        control_frame = ttk.Frame(list_frame)
        control_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Left side: View toggle
        toggle_frame = ttk.Frame(control_frame)
        toggle_frame.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        self.view_label = ttk.Label(toggle_frame, text="Currently showing: Pending Reminders")
        self.view_label.pack(side=tk.LEFT, padx=5)
        
        self.toggle_button = ttk.Button(toggle_frame, text="Show Completed", command=self.toggle_view)
        self.toggle_button.pack(side=tk.LEFT, padx=5)

        # Right side: Filter dropdown
        filter_frame = ttk.Frame(control_frame)
        filter_frame.pack(side=tk.RIGHT, fill=tk.X)
        
        ttk.Label(filter_frame, text="Filter:").pack(side=tk.LEFT, padx=5)
        self.filter_var = tk.StringVar(value="All")
        filter_dropdown = ttk.Combobox(filter_frame, textvariable=self.filter_var, 
                                     values=["All", "Due Today", "Due This Week", "Due Next Week"],
                                     state="readonly", width=15)
        filter_dropdown.pack(side=tk.LEFT, padx=5)
        filter_dropdown.bind("<<ComboboxSelected>>", self.on_filter_change)

        self.reminders_tree = ttk.Treeview(list_frame, columns=("Task", "Date", "Time", "Priority", "Recurrence"), show="headings")
        self.reminders_tree.heading("Task", text="Task")
        self.reminders_tree.heading("Date", text="Date")
        self.reminders_tree.heading("Time", text="Time")
        self.reminders_tree.heading("Priority", text="Priority")
        self.reminders_tree.heading("Recurrence", text="Recurrence")
        self.reminders_tree.column("Task", width=200)
        self.reminders_tree.column("Date", width=90, anchor=tk.CENTER)
        self.reminders_tree.column("Time", width=80, anchor=tk.CENTER)
        self.reminders_tree.column("Priority", width=80, anchor=tk.CENTER)
        self.reminders_tree.column("Recurrence", width=100, anchor=tk.CENTER)
        self.reminders_tree.pack(fill=tk.BOTH, expand=True)

        self.load_reminders()

        button_frame = ttk.Frame(list_frame)
        button_frame.pack(pady=5)
        
        mark_complete_button = ttk.Button(button_frame, text="Mark Complete", command=self.mark_reminder_complete)
        mark_complete_button.pack(side=tk.LEFT, padx=5)
        
        delete_button = ttk.Button(button_frame, text="Delete Reminder", command=self.delete_reminder)
        delete_button.pack(side=tk.LEFT, padx=5)

    def on_filter_change(self, event=None):
        self.current_filter = self.filter_var.get()
        self.load_reminders()

    def get_date_range(self):
        today = datetime.now().date()
        if self.current_filter == "All":
            return None, None
        elif self.current_filter == "Due Today":
            return today, today
        elif self.current_filter == "Due This Week":
            # Get the start of the week (Monday)
            start_of_week = today - timedelta(days=today.weekday())
            end_of_week = start_of_week + timedelta(days=6)
            return start_of_week, end_of_week
        elif self.current_filter == "Due Next Week":
            # Get the start of next week (Monday)
            start_of_week = today - timedelta(days=today.weekday())
            start_of_next_week = start_of_week + timedelta(days=7)
            end_of_next_week = start_of_next_week + timedelta(days=6)
            return start_of_next_week, end_of_next_week
        return None, None

    def toggle_view(self):
        self.show_completed = not self.show_completed
        if self.show_completed:
            self.view_label.config(text="Currently showing: Completed Reminders")
            self.toggle_button.config(text="Show Pending")
            self.reminders_tree.master.config(text="Completed Reminders")
        else:
            self.view_label.config(text="Currently showing: Pending Reminders")
            self.toggle_button.config(text="Show Completed")
            self.reminders_tree.master.config(text="Pending Reminders")
        self.load_reminders()

    def add_reminder(self):
        task = self.task_entry.get().strip()
        date_str = self.date_entry.get().strip()
        time_str = self.time_entry.get().strip()
        recurrence_type = self.recurrence_type_var.get()
        recurrence_interval_str = self.recurrence_interval_entry.get().strip()
        recurrence_end_date_str = self.recurrence_end_date_entry.get().strip()
        priority = self.priority_var.get()

        if not task or not date_str or not time_str:
            messagebox.showerror("Input Error", "Task, Date, and Time are required.")
            return

        try:
            # Validate date and time format
            reminder_datetime_str = f"{date_str} {time_str}"
            datetime.strptime(reminder_datetime_str, '%Y-%m-%d %H:%M')
        except ValueError:
            messagebox.showerror("Input Error", "Date format should be YYYY-MM-DD and Time HH:MM.")
            return

        # Validate recurrence interval
        recurrence_interval = 0
        if recurrence_type != "None":
            if not recurrence_interval_str.isdigit() or int(recurrence_interval_str) <= 0:
                messagebox.showerror("Input Error", "Interval must be a positive number for recurring reminders.")
                return
            recurrence_interval = int(recurrence_interval_str)
        
        # Validate recurrence end date if provided
        if recurrence_end_date_str:
            try:
                datetime.strptime(recurrence_end_date_str, '%Y-%m-%d')
            except ValueError:
                messagebox.showerror("Input Error", "Recurrence End Date format should be YYYY-MM-DD.")
                return

        self.db.cursor.execute("INSERT INTO reminders (task, reminder_date, reminder_time, completed, recurrence_type, recurrence_interval, recurrence_end_date, priority) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                                (task, date_str, time_str, 0, recurrence_type, recurrence_interval, recurrence_end_date_str if recurrence_end_date_str else None, priority))
        self.db.conn.commit()
        messagebox.showinfo("Success", "Reminder added successfully!")
        self.clear_entries()
        self.load_reminders()

    def load_reminders(self):
        for item in self.reminders_tree.get_children():
            self.reminders_tree.delete(item)

        # Get date range based on current filter
        start_date, end_date = self.get_date_range()
        
        # Base query
        query = "SELECT id, task, reminder_date, reminder_time, recurrence_type, recurrence_interval, recurrence_end_date, priority FROM reminders WHERE completed = ?"
        params = [1 if self.show_completed else 0]

        # Add date range filter if applicable
        if start_date and end_date:
            query += " AND DATE(reminder_date) BETWEEN DATE(?) AND DATE(?)"
            params.extend([start_date.isoformat(), end_date.isoformat()])

        # Add ordering
        query += " ORDER BY reminder_date, reminder_time"

        reminders = self.db.cursor.execute(query, params).fetchall()
        
        for reminder in reminders:
            recurrence_display = reminder[4] # Recurrence Type
            if reminder[4] != 'None':
                recurrence_display += f" every {reminder[5]} " # Recurrence Interval
                if reminder[4] == 'Daily':
                    recurrence_display += "day(s)"
                elif reminder[4] == 'Weekly':
                    recurrence_display += "week(s)"
                elif reminder[4] == 'Monthly':
                    recurrence_display += "month(s)"
                
                if reminder[6]: # Recurrence End Date
                    recurrence_display += f" until {reminder[6]}"

            self.reminders_tree.insert("", "end", iid=reminder[0], values=(reminder[1], reminder[2], reminder[3], reminder[7], recurrence_display))

        self.date_entry.delete(0, tk.END)
        self.time_entry.delete(0, tk.END)
        self.recurrence_type_var.set("None")
        self.recurrence_interval_entry.delete(0, tk.END)
        self.recurrence_interval_entry.insert(0, "1") # Reset to default
        self.recurrence_end_date_entry.delete(0, tk.END)
        self.priority_var.set("Medium")

    def mark_reminder_complete(self):
        if self.show_completed:
            messagebox.showwarning("Action Error", "Cannot mark completed reminders as complete.")
            return

        selected_item = self.reminders_tree.focus()
        if not selected_item:
            messagebox.showwarning("Selection Error", "Please select a reminder to mark as complete.")
            return

        # Get the reminder ID from the selected item
        reminder_id = selected_item  # The item ID is the reminder ID
        self.db.cursor.execute("UPDATE reminders SET completed = 1 WHERE id = ?", (reminder_id,))
        self.db.conn.commit()
        messagebox.showinfo("Success", "Reminder marked as complete!")
        self.load_reminders()

    def delete_reminder(self):
        selected_item = self.reminders_tree.focus()
        if not selected_item:
            messagebox.showwarning("Selection Error", "Please select a reminder to delete.")
            return

        if messagebox.askyesno("Confirm Delete", "Are you sure you want to delete this reminder?"):
            # Get the reminder ID from the selected item
            reminder_id = selected_item  # The item ID is the reminder ID
            self.db.cursor.execute("DELETE FROM reminders WHERE id = ?", (reminder_id,))
            self.db.conn.commit()
            messagebox.showinfo("Success", "Reminder deleted successfully!")
            self.load_reminders()

    def clear_entries(self):
        self.task_entry.delete(0, tk.END)
        self.date_entry.delete(0, tk.END)
        self.time_entry.delete(0, tk.END)
        self.recurrence_type_var.set("None")
        self.recurrence_interval_entry.delete(0, tk.END)
        self.recurrence_interval_entry.insert(0, "1") # Reset to default
        self.recurrence_end_date_entry.delete(0, tk.END)
        self.priority_var.set("Medium")

    def refresh(self):
        self.load_reminders() 