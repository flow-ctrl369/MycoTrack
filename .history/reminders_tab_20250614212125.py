import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime

class RemindersTab(ttk.Frame):
    def __init__(self, parent, db):
        super().__init__(parent)
        self.db = db
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

        self.reminders_tree = ttk.Treeview(list_frame, columns=("Task", "Date", "Time"), show="headings")
        self.reminders_tree.heading("Task", text="Task")
        self.reminders_tree.heading("Date", text="Date")
        self.reminders_tree.heading("Time", text="Time")
        self.reminders_tree.column("Task", width=300)
        self.reminders_tree.column("Date", width=100, anchor=tk.CENTER)
        self.reminders_tree.column("Time", width=100, anchor=tk.CENTER)
        self.reminders_tree.pack(fill=tk.BOTH, expand=True)

        self.load_reminders()

        mark_complete_button = ttk.Button(list_frame, text="Mark Complete", command=self.mark_reminder_complete)
        mark_complete_button.pack(pady=5)

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

        reminders = self.db.cursor.execute("SELECT id, task, reminder_date, reminder_time FROM reminders WHERE completed = 0 ORDER BY reminder_date, reminder_time").fetchall()
        for reminder in reminders:
            self.reminders_tree.insert("", "end", iid=reminder[0], values=(reminder[1], reminder[2], reminder[3]))

    def mark_reminder_complete(self):
        selected_item = self.reminders_tree.focus()
        if not selected_item:
            messagebox.showwarning("Selection Error", "Please select a reminder to mark as complete.")
            return

        reminder_id = self.reminders_tree.item(selected_item)['iid']
        self.db.cursor.execute("UPDATE reminders SET completed = 1 WHERE id = ?", (reminder_id,))
        self.db.conn.commit()
        messagebox.showinfo("Success", "Reminder marked as complete!")
        self.load_reminders()

    def clear_entries(self):
        self.task_entry.delete(0, tk.END)
        self.date_entry.delete(0, tk.END)
        self.time_entry.delete(0, tk.END)

    def refresh(self):
        self.load_reminders() 