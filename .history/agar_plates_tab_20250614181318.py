import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
from datetime import datetime
from tkcalendar import Calendar
import csv
import os

class AgarPlatesTab(ttk.Frame):
    def __init__(self, parent, db_path):
        super().__init__(parent)
        self.db_path = db_path
        self.setup_ui()
        
    def setup_ui(self):
        # Create main container with padding
        self.main_container = ttk.Frame(self, padding="10")
        self.main_container.pack(fill=tk.BOTH, expand=True)
        
        # Create left and right frames
        self.left_frame = ttk.Frame(self.main_container)
        self.left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))
        
        self.right_frame = ttk.Frame(self.main_container)
        self.right_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(5, 0))
        
        # Create form
        self.create_form()
        
        # Create table
        self.create_table()
        
        # Load initial data
        self.load_data()
        
    def create_form(self):
        # Form container
        form_frame = ttk.LabelFrame(self.left_frame, text="Add New Agar Plate", padding="10")
        form_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Strain Name
        ttk.Label(form_frame, text="Strain Name:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.strain_name_var = tk.StringVar()
        ttk.Entry(form_frame, textvariable=self.strain_name_var).grid(row=0, column=1, sticky=tk.EW, pady=5)
        
        # Date Created
        ttk.Label(form_frame, text="Date Created:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.date_created_var = tk.StringVar(value=datetime.now().strftime("%Y-%m-%d"))
        date_entry = ttk.Entry(form_frame, textvariable=self.date_created_var)
        date_entry.grid(row=1, column=1, sticky=tk.EW, pady=5)
        date_entry.bind('<Button-1>', self.show_calendar)
        
        # Media Type
        ttk.Label(form_frame, text="Media Type:").grid(row=2, column=0, sticky=tk.W, pady=5)
        self.media_type_var = tk.StringVar()
        media_types = ["MEA", "PDA", "YMA", "Custom"]
        ttk.Combobox(form_frame, textvariable=self.media_type_var, values=media_types).grid(row=2, column=1, sticky=tk.EW, pady=5)
        
        # Notes
        ttk.Label(form_frame, text="Notes:").grid(row=3, column=0, sticky=tk.W, pady=5)
        self.notes_var = tk.StringVar()
        ttk.Entry(form_frame, textvariable=self.notes_var).grid(row=3, column=1, sticky=tk.EW, pady=5)
        
        # Storage Location
        ttk.Label(form_frame, text="Storage Location:").grid(row=4, column=0, sticky=tk.W, pady=5)
        self.storage_location_var = tk.StringVar()
        ttk.Entry(form_frame, textvariable=self.storage_location_var).grid(row=4, column=1, sticky=tk.EW, pady=5)
        
        # Submit button
        ttk.Button(form_frame, text="Add Plate", command=self.add_plate).grid(row=5, column=0, columnspan=2, pady=10)
        
        # Configure grid
        form_frame.columnconfigure(1, weight=1)
        
    def create_table(self):
        # Table container
        table_frame = ttk.LabelFrame(self.right_frame, text="Agar Plates", padding="10")
        table_frame.pack(fill=tk.BOTH, expand=True)
        
        # Create Treeview
        columns = ("id", "strain_name", "date_created", "media_type", "notes", "contamination", "transfer_count", "storage_location", "status")
        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings")
        
        # Define headings
        self.tree.heading("id", text="ID")
        self.tree.heading("strain_name", text="Strain Name")
        self.tree.heading("date_created", text="Date Created")
        self.tree.heading("media_type", text="Media Type")
        self.tree.heading("notes", text="Notes")
        self.tree.heading("contamination", text="Contaminated")
        self.tree.heading("transfer_count", text="Transfers")
        self.tree.heading("storage_location", text="Storage Location")
        self.tree.heading("status", text="Status")
        
        # Define columns
        self.tree.column("id", width=50)
        self.tree.column("strain_name", width=150)
        self.tree.column("date_created", width=100)
        self.tree.column("media_type", width=100)
        self.tree.column("notes", width=200)
        self.tree.column("contamination", width=100)
        self.tree.column("transfer_count", width=100)
        self.tree.column("storage_location", width=150)
        self.tree.column("status", width=100)
        
        # Add scrollbar
        scrollbar = ttk.Scrollbar(table_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        # Pack tree and scrollbar
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Add right-click menu
        self.create_context_menu()
        
    def create_context_menu(self):
        self.context_menu = tk.Menu(self, tearoff=0)
        self.context_menu.add_command(label="Mark as Contaminated", command=self.mark_contaminated)
        self.context_menu.add_command(label="Record Transfer", command=self.record_transfer)
        self.context_menu.add_command(label="Delete", command=self.delete_plate)
        self.context_menu.add_command(label="Export to CSV", command=self.export_to_csv)
        
        self.tree.bind("<Button-3>", self.show_context_menu)
        
    def show_context_menu(self, event):
        item = self.tree.identify_row(event.y)
        if item:
            self.tree.selection_set(item)
            self.context_menu.post(event.x_root, event.y_root)
            
    def show_calendar(self, event):
        def set_date():
            self.date_created_var.set(cal.get_date())
            top.destroy()
            
        top = tk.Toplevel(self)
        cal = Calendar(top, selectmode='day', date_pattern='yyyy-mm-dd')
        cal.pack(padx=10, pady=10)
        ttk.Button(top, text="OK", command=set_date).pack(pady=5)
        
    def add_plate(self):
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO agar_plates (strain_name, date_created, media_type, notes, storage_location)
                VALUES (?, ?, ?, ?, ?)
            """, (
                self.strain_name_var.get(),
                self.date_created_var.get(),
                self.media_type_var.get(),
                self.notes_var.get(),
                self.storage_location_var.get()
            ))
            
            conn.commit()
            conn.close()
            
            # Clear form
            self.strain_name_var.set("")
            self.media_type_var.set("")
            self.notes_var.set("")
            self.storage_location_var.set("")
            
            # Refresh table
            self.load_data()
            
        except sqlite3.Error as e:
            messagebox.showerror("Database Error", f"Error adding plate: {str(e)}")
            
    def load_data(self):
        try:
            # Clear existing items
            for item in self.tree.get_children():
                self.tree.delete(item)

            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Fetch and display records
            cursor.execute("SELECT * FROM agar_plates ORDER BY date_inoculated DESC")
            for record in cursor.fetchall():
                self.tree.insert("", tk.END, values=record[:8])  # Exclude created_at and updated_at
                
            conn.close()
            
        except sqlite3.Error as e:
            messagebox.showerror("Database Error", f"Error loading data: {str(e)}")
            
    def mark_contaminated(self):
        selected = self.tree.selection()
        if not selected:
            return
            
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            for item in selected:
                plate_id = self.tree.item(item)["values"][0]
                cursor.execute("""
                    UPDATE agar_plates 
                    SET contamination = 1, 
                        date_contaminated = ?,
                        status = 'Contaminated'
                    WHERE id = ?
                """, (datetime.now().strftime("%Y-%m-%d"), plate_id))
                
            conn.commit()
            conn.close()
            
            self.load_data()
            
        except sqlite3.Error as e:
            messagebox.showerror("Database Error", f"Error marking plate as contaminated: {str(e)}")
            
    def record_transfer(self):
        selected = self.tree.selection()
        if not selected:
            return
            
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            for item in selected:
                plate_id = self.tree.item(item)["values"][0]
                cursor.execute("""
                    UPDATE agar_plates 
                    SET transfer_count = transfer_count + 1,
                        last_transfer_date = ?
                    WHERE id = ?
                """, (datetime.now().strftime("%Y-%m-%d"), plate_id))
                
            conn.commit()
            conn.close()
            
            self.load_data()
            
        except sqlite3.Error as e:
            messagebox.showerror("Database Error", f"Error recording transfer: {str(e)}")
            
    def delete_plate(self):
        selected = self.tree.selection()
        if not selected:
            return
            
        if not messagebox.askyesno("Confirm Delete", "Are you sure you want to delete the selected plates?"):
            return
            
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            for item in selected:
                plate_id = self.tree.item(item)["values"][0]
                cursor.execute("DELETE FROM agar_plates WHERE id = ?", (plate_id,))
                
            conn.commit()
            conn.close()
            
            self.load_data()
            
        except sqlite3.Error as e:
            messagebox.showerror("Database Error", f"Error deleting plate: {str(e)}")
            
    def export_to_csv(self):
        try:
            filename = "agar_plates_export.csv"
            
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Get all data
            cursor.execute("SELECT * FROM agar_plates")
            rows = cursor.fetchall()
            
            # Get column names
            cursor.execute("PRAGMA table_info(agar_plates)")
            columns = [column[1] for column in cursor.fetchall()]
            
            # Write to CSV
            with open(filename, 'w', newline='') as f:
                writer = csv.writer(f)
                writer.writerow(columns)
                writer.writerows(rows)
                
            conn.close()
            
            messagebox.showinfo("Export Successful", f"Data exported to {filename}")
            
        except (sqlite3.Error, IOError) as e:
            messagebox.showerror("Export Error", f"Error exporting data: {str(e)}") 