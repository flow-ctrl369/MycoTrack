import tkinter as tk
from tkinter import ttk, messagebox
import csv
from datetime import datetime
from tkcalendar import DateEntry
import sqlite3

class GrainJarsTab(ttk.Frame):
    def __init__(self, parent, db_path):
        super().__init__(parent)
        self.db_path = db_path
        self.setup_ui()

    def setup_ui(self):
        # Create main container with padding
        self.main_frame = ttk.Frame(self)
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        # Create left frame for form
        self.form_frame = ttk.LabelFrame(self.main_frame, text="New Grain Jar Entry")
        self.form_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))

        # Create right frame for table
        self.table_frame = ttk.LabelFrame(self.main_frame, text="Grain Jars List")
        self.table_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(5, 0))

        self.setup_form()
        self.setup_table()
        self.setup_search()
        self.load_data()

    def setup_form(self):
        # Form fields
        fields = [
            ("Jar ID:", "jar_id"),
            ("LC/Agar Source ID:", "source_id"),
            ("Inoculation Date:", "inoculation_date"),
            ("Colonization %:", "colonization_percentage"),
            ("Shake Date:", "shake_date"),
            ("Contamination Notes:", "contamination_notes")
        ]

        # Create and pack form widgets
        self.form_vars = {}
        for i, (label_text, field_name) in enumerate(fields):
            ttk.Label(self.form_frame, text=label_text).grid(row=i, column=0, sticky="e", padx=5, pady=2)
            
            if field_name in ["inoculation_date", "shake_date"]:
                self.form_vars[field_name] = DateEntry(self.form_frame, width=20, background="#262626", foreground="#f0f0f0", headersbackground="#262626", headersforeground="#f0f0f0")
                self.form_vars[field_name].grid(row=i, column=1, sticky="w", padx=5, pady=2)
            elif field_name == "colonization_percentage":
                self.form_vars[field_name] = ttk.Spinbox(
                    self.form_frame, 
                    from_=0, 
                    to=100, 
                    width=20,
                    validate='key',
                    validatecommand=(self.register(self.validate_percentage), '%P')
                )
                self.form_vars[field_name].grid(row=i, column=1, sticky="w", padx=5, pady=2)
            elif field_name == "contamination_notes":
                self.form_vars[field_name] = tk.Text(self.form_frame, height=3, width=30, bg="#262626", fg="#f0f0f0", insertbackground="#f0f0f0")
                self.form_vars[field_name].grid(row=i, column=1, sticky="w", padx=5, pady=2)
            else:
                self.form_vars[field_name] = ttk.Entry(self.form_frame, width=30)
                self.form_vars[field_name].grid(row=i, column=1, sticky="w", padx=5, pady=2)

        # Buttons frame
        button_frame = ttk.Frame(self.form_frame)
        button_frame.grid(row=len(fields), column=0, columnspan=2, pady=10)

        ttk.Button(button_frame, text="Save", command=self.save_record).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Clear", command=self.clear_form).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Mark as Shaken", command=self.mark_as_shaken).pack(side=tk.LEFT, padx=5)

    def validate_percentage(self, value):
        """Validate that the percentage input is between 0 and 100"""
        if value == "":
            return True
        try:
            num = int(value)
            return 0 <= num <= 100
        except ValueError:
            return False

    def setup_table(self):
        # Create Treeview
        columns = ("Jar ID", "Source ID", "Inoculation Date", "Colonization %", 
                  "Shake Date", "Contamination Notes")
        self.tree = ttk.Treeview(self.table_frame, columns=columns, show="headings")
        
        # Set column headings
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=100)

        # Add scrollbar
        scrollbar = ttk.Scrollbar(self.table_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        # Pack table and scrollbar
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Bind double-click event for editing
        self.tree.bind("<Double-1>", self.edit_record)

    def setup_search(self):
        # Search frame
        search_frame = ttk.Frame(self.table_frame)
        search_frame.pack(fill=tk.X, pady=5)

        ttk.Label(search_frame, text="Search:").pack(side=tk.LEFT, padx=5)
        self.search_var = tk.StringVar()
        self.search_var.trace("w", self.filter_records)
        ttk.Entry(search_frame, textvariable=self.search_var).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)

        # Export button
        ttk.Button(search_frame, text="Export to CSV", command=self.export_to_csv).pack(side=tk.RIGHT, padx=5)

    def save_record(self):
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Get values from form
            values = {
                "jar_id": self.form_vars["jar_id"].get(),
                "source_id": self.form_vars["source_id"].get(),
                "inoculation_date": self.form_vars["inoculation_date"].get_date().isoformat(),
                "colonization_percentage": int(self.form_vars["colonization_percentage"].get() or 0),
                "shake_date": self.form_vars["shake_date"].get_date().isoformat() if self.form_vars["shake_date"].get() else None,
                "contamination_notes": self.form_vars["contamination_notes"].get("1.0", tk.END).strip(),
                "created_at": datetime.now().isoformat(),
                "updated_at": datetime.now().isoformat()
            }

            # Validate required fields
            if not all([values["jar_id"], values["source_id"]]):
                messagebox.showerror("Error", "Please fill in all required fields")
                return

            # Insert into database
            cursor.execute('''
                INSERT INTO grain_jars 
                (jar_id, source_id, inoculation_date, colonization_percentage, 
                shake_date, contamination_notes, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', tuple(values.values()))
            
            conn.commit()
            conn.close()
            
            self.load_data()
            self.clear_form()
            messagebox.showinfo("Success", "Record saved successfully")

        except sqlite3.IntegrityError:
            messagebox.showerror("Error", "Jar ID already exists")
        except ValueError:
            messagebox.showerror("Error", "Colonization percentage must be between 0 and 100")
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {str(e)}")

    def mark_as_shaken(self):
        """Mark the selected jar as shaken with today's date"""
        try:
            selected_item = self.tree.selection()[0]
            jar_id = self.tree.item(selected_item)["values"][0]
            
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Update shake date in database
            cursor.execute('''
                UPDATE grain_jars 
                SET shake_date = ?, updated_at = ?
                WHERE jar_id = ?
            ''', (datetime.now().isoformat(), datetime.now().isoformat(), jar_id))
            
            conn.commit()
            conn.close()
            
            self.load_data()
            messagebox.showinfo("Success", f"Jar {jar_id} marked as shaken")
        except IndexError:
            messagebox.showerror("Error", "Please select a jar to mark as shaken")
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {str(e)}")

    def load_data(self):
        try:
            # Clear existing items
            for item in self.tree.get_children():
                self.tree.delete(item)

            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Fetch and display records
            cursor.execute("SELECT * FROM grain_jars ORDER BY inoculation_date DESC")
            for record in cursor.fetchall():
                self.tree.insert("", tk.END, values=record[:6])  # Exclude created_at and updated_at
                
            conn.close()
            
        except sqlite3.Error as e:
            messagebox.showerror("Database Error", f"Error loading data: {str(e)}")

    def filter_records(self, *args):
        try:
            search_term = self.search_var.get().lower()
            
            # Clear existing items
            for item in self.tree.get_children():
                self.tree.delete(item)

            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Fetch and filter records
            cursor.execute("SELECT * FROM grain_jars ORDER BY inoculation_date DESC")
            for record in cursor.fetchall():
                if any(search_term in str(value).lower() for value in record[:6]):
                    self.tree.insert("", tk.END, values=record[:6])
                    
            conn.close()
            
        except sqlite3.Error as e:
            messagebox.showerror("Database Error", f"Error filtering data: {str(e)}")

    def edit_record(self, event):
        # Get selected item
        selected_item = self.tree.selection()[0]
        values = self.tree.item(selected_item)["values"]

        # Populate form with selected record
        self.form_vars["jar_id"].delete(0, tk.END)
        self.form_vars["jar_id"].insert(0, values[0])
        self.form_vars["source_id"].delete(0, tk.END)
        self.form_vars["source_id"].insert(0, values[1])
        self.form_vars["inoculation_date"].set_date(datetime.strptime(values[2], "%Y-%m-%d"))
        self.form_vars["colonization_percentage"].delete(0, tk.END)
        self.form_vars["colonization_percentage"].insert(0, values[3])
        if values[4]:  # Shake date
            self.form_vars["shake_date"].set_date(datetime.strptime(values[4], "%Y-%m-%d"))
        self.form_vars["contamination_notes"].delete("1.0", tk.END)
        self.form_vars["contamination_notes"].insert("1.0", values[5])

    def clear_form(self):
        for field_name, widget in self.form_vars.items():
            if isinstance(widget, tk.Text):
                widget.delete("1.0", tk.END)
            elif isinstance(widget, ttk.Entry):
                widget.delete(0, tk.END)
            elif isinstance(widget, ttk.Spinbox):
                widget.delete(0, tk.END)
                widget.insert(0, "0")
            elif isinstance(widget, DateEntry):
                widget.set_date(datetime.now())

    def export_to_csv(self):
        try:
            filename = "grain_jars_export.csv"
            
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Get all data
            cursor.execute("SELECT * FROM grain_jars")
            rows = cursor.fetchall()
            
            # Get column names
            cursor.execute("PRAGMA table_info(grain_jars)")
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