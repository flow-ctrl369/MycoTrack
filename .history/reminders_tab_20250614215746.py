import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime

class RemindersTab(ttk.Frame):
    def __init__(self, parent, db):
        super().__init__(parent)
        self.db = db
        self.show_completed = False  # Track whether we're showing completed reminders
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

        add_button = ttk.Button(form_frame, text="Add Reminder", command=self.add_reminder)
        add_button.grid(row=3, column=0, columnspan=2, pady=10)

        # Reminders List
        list_frame = ttk.LabelFrame(self, text="Pending Reminders")
        list_frame.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

        # View toggle button
        toggle_frame = ttk.Frame(list_frame)
        toggle_frame.pack(fill=tk.X, padx=5, pady=5)
        
        self.view_label = ttk.Label(toggle_frame, text="Currently showing: Pending Reminders")
        self.view_label.pack(side=tk.LEFT, padx=5)
        
        self.toggle_button = ttk.Button(toggle_frame, text="Show Completed", command=self.toggle_view)
        self.toggle_button.pack(side=tk.RIGHT, padx=5)

        self.reminders_tree = ttk.Treeview(list_frame, columns=("Task", "Date", "Time"), show="headings")
        self.reminders_tree.heading("Task", text="Task")
        self.reminders_tree.heading("Date", text="Date")
        self.reminders_tree.heading("Time", text="Time")
        self.reminders_tree.column("Task", width=300)
        self.reminders_tree.column("Date", width=100, anchor=tk.CENTER)
        self.reminders_tree.column("Time", width=100, anchor=tk.CENTER)
        self.reminders_tree.pack(fill=tk.BOTH, expand=True)

        self.load_reminders()

        button_frame = ttk.Frame(list_frame)
        button_frame.pack(pady=5)
        
        mark_complete_button = ttk.Button(button_frame, text="Mark Complete", command=self.mark_reminder_complete)
        mark_complete_button.pack(side=tk.LEFT, padx=5)
        
        delete_button = ttk.Button(button_frame, text="Delete Reminder", command=self.delete_reminder)
        delete_button.pack(side=tk.LEFT, padx=5)

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

        if not task or not date_str or not time_str:
            messagebox.showerror("Input Error", "All fields are required.")
            return

        try:
            # Validate date and time format
            reminder_datetime_str = f"{date_str} {time_str}"
            datetime.strptime(reminder_datetime_str, '%Y-%m-%d %H:%M')
        except ValueError:
            messagebox.showerror("Input Error", "Date format should be YYYY-MM-DD and Time HH:MM.")
            return

        self.db.cursor.execute("INSERT INTO reminders (task, reminder_date, reminder_time, completed) VALUES (?, ?, ?, ?)",
                                (task, date_str, time_str, 0))
        self.db.conn.commit()
        messagebox.showinfo("Success", "Reminder added successfully!")
        self.clear_entries()
        self.load_reminders()

    def load_reminders(self):
        for item in self.reminders_tree.get_children():
            self.reminders_tree.delete(item)

        # Query based on whether we're showing completed or pending reminders
        completed_value = 1 if self.show_completed else 0
        reminders = self.db.cursor.execute(
            "SELECT id, task, reminder_date, reminder_time FROM reminders WHERE completed = ? ORDER BY reminder_date, reminder_time",
            (completed_value,)
        ).fetchall()
        
        for reminder in reminders:
            self.reminders_tree.insert("", "end", iid=reminder[0], values=(reminder[1], reminder[2], reminder[3]))

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

    def refresh(self):
        self.load_reminders() 