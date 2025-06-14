import tkinter as tk
from tkinter import ttk, messagebox
import csv
from datetime import datetime
from tkcalendar import DateEntry
import sqlite3

class BulkTubsTab(ttk.Frame):
    def __init__(self, parent, db_path):
        super().__init__(parent)
        self.db_path = db_path
        self.setup_ui()

    def setup_ui(self):
        # Create main container with padding
        self.main_frame = ttk.Frame(self)
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        # Create left frame for form
        self.form_frame = ttk.LabelFrame(self.main_frame, text="New Bulk Tub Entry")
        self.form_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))

        # Create right frame for table
        self.table_frame = ttk.LabelFrame(self.main_frame, text="Bulk Tubs List")
        self.table_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(5, 0))

        self.setup_form()
        self.setup_table()
        self.setup_search()
        self.load_data()

    def setup_form(self):
        # Form fields
        fields = [
            ("Tub ID:", "tub_id"),
            ("Spawn Source (Jar ID):", "spawn_source"),
            ("Substrate Type:", "substrate_type"),
            ("Date to Bulk:", "date_to_bulk"),
            ("First Pins Date:", "first_pins_date"),
            ("Harvest Weight - Flush 1 (g):", "harvest_weight_flush1"),
            ("Harvest Weight - Flush 2 (g):", "harvest_weight_flush2"),
            ("Harvest Weight - Flush 3 (g):", "harvest_weight_flush3"),
            ("Performance Notes:", "performance_notes")
        ]

        # Create and pack form widgets
        self.form_vars = {}
        for i, (label_text, field_name) in enumerate(fields):
            ttk.Label(self.form_frame, text=label_text).grid(row=i, column=0, sticky="e", padx=5, pady=2)
            
            if field_name in ["date_to_bulk", "first_pins_date"]:
                self.form_vars[field_name] = DateEntry(self.form_frame, width=20, background="#262626", foreground="#f0f0f0", headersbackground="#262626", headersforeground="#f0f0f0")
                self.form_vars[field_name].grid(row=i, column=1, sticky="w", padx=5, pady=2)
            elif field_name.startswith("harvest_weight"):
                self.form_vars[field_name] = ttk.Entry(self.form_frame, width=20)
                self.form_vars[field_name].grid(row=i, column=1, sticky="w", padx=5, pady=2)
                # Add validation for numeric input
                vcmd = (self.register(self.validate_weight), '%P')
                self.form_vars[field_name].configure(validate='key', validatecommand=vcmd)
            elif field_name == "substrate_type":
                self.form_vars[field_name] = ttk.Combobox(self.form_frame, values=[
                    "CVG (Coir/Verm/Gypsum)",
                    "Manure Based",
                    "Straw Based",
                    "Custom Mix"
                ])
                self.form_vars[field_name].grid(row=i, column=1, sticky="w", padx=5, pady=2)
            elif field_name == "performance_notes":
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
        ttk.Button(button_frame, text="Mark First Pins", command=self.mark_first_pins).pack(side=tk.LEFT, padx=5)

    def validate_weight(self, value):
        """Validate that the weight input is a positive number"""
        if value == "":
            return True
        try:
            num = float(value)
            return num >= 0
        except ValueError:
            return False

    def setup_table(self):
        # Create Treeview
        columns = ("Tub ID", "Spawn Source", "Substrate Type", "Date to Bulk", 
                  "First Pins", "Flush 1 (g)", "Flush 2 (g)", "Flush 3 (g)", "Notes")
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
                "tub_id": self.form_vars["tub_id"].get(),
                "spawn_source": self.form_vars["spawn_source"].get(),
                "substrate_type": self.form_vars["substrate_type"].get(),
                "date_to_bulk": self.form_vars["date_to_bulk"].get_date().isoformat(),
                "first_pins_date": self.form_vars["first_pins_date"].get_date().isoformat() if self.form_vars["first_pins_date"].get() else None,
                "harvest_weight_flush1": float(self.form_vars["harvest_weight_flush1"].get() or 0),
                "harvest_weight_flush2": float(self.form_vars["harvest_weight_flush2"].get() or 0),
                "harvest_weight_flush3": float(self.form_vars["harvest_weight_flush3"].get() or 0),
                "performance_notes": self.form_vars["performance_notes"].get("1.0", tk.END).strip(),
                "created_at": datetime.now().isoformat(),
                "updated_at": datetime.now().isoformat()
            }

            # Validate required fields
            if not all([values["tub_id"], values["spawn_source"], values["substrate_type"]]):
                messagebox.showerror("Error", "Please fill in all required fields")
                return

            # Insert into database
            cursor.execute('''
                INSERT INTO bulk_tubs 
                (tub_id, spawn_source, substrate_type, date_to_bulk, first_pins_date,
                harvest_weight_flush1, harvest_weight_flush2, harvest_weight_flush3,
                performance_notes, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', tuple(values.values()))
            
            conn.commit()
            conn.close()
            
            self.load_data()
            self.clear_form()
            messagebox.showinfo("Success", "Record saved successfully")

        except sqlite3.IntegrityError:
            messagebox.showerror("Error", "Tub ID already exists")
        except ValueError:
            messagebox.showerror("Error", "Harvest weights must be valid numbers")
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {str(e)}")

    def mark_first_pins(self):
        """Mark the selected tub as having first pins with today's date"""
        try:
            selected_item = self.tree.selection()[0]
            tub_id = self.tree.item(selected_item)["values"][0]
            
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Update first pins date in database
            cursor.execute('''
                UPDATE bulk_tubs 
                SET first_pins_date = ?, updated_at = ?
                WHERE tub_id = ?
            ''', (datetime.now().isoformat(), datetime.now().isoformat(), tub_id))
            
            conn.commit()
            conn.close()
            
            self.load_data()
            messagebox.showinfo("Success", f"Tub {tub_id} marked as having first pins")
        except IndexError:
            messagebox.showerror("Error", "Please select a tub to mark as having first pins")
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
            cursor.execute("SELECT * FROM bulk_tubs ORDER BY date_to_bulk DESC")
            for record in cursor.fetchall():
                self.tree.insert("", tk.END, values=record[:9])  # Exclude created_at and updated_at
                
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
            cursor.execute("SELECT * FROM bulk_tubs ORDER BY date_to_bulk DESC")
            for record in cursor.fetchall():
                if any(search_term in str(value).lower() for value in record[:9]):
                    self.tree.insert("", tk.END, values=record[:9])
                    
            conn.close()
            
        except sqlite3.Error as e:
            messagebox.showerror("Database Error", f"Error filtering data: {str(e)}")

    def edit_record(self, event):
        # Get selected item
        selected_item = self.tree.selection()[0]
        values = self.tree.item(selected_item)["values"]

        # Populate form with selected record
        self.form_vars["tub_id"].delete(0, tk.END)
        self.form_vars["tub_id"].insert(0, values[0])
        self.form_vars["spawn_source"].delete(0, tk.END)
        self.form_vars["spawn_source"].insert(0, values[1])
        self.form_vars["substrate_type"].set(values[2])
        self.form_vars["date_to_bulk"].set_date(datetime.strptime(values[3], "%Y-%m-%d"))
        if values[4]:  # First pins date
            self.form_vars["first_pins_date"].set_date(datetime.strptime(values[4], "%Y-%m-%d"))
        self.form_vars["harvest_weight_flush1"].delete(0, tk.END)
        self.form_vars["harvest_weight_flush1"].insert(0, values[5])
        self.form_vars["harvest_weight_flush2"].delete(0, tk.END)
        self.form_vars["harvest_weight_flush2"].insert(0, values[6])
        self.form_vars["harvest_weight_flush3"].delete(0, tk.END)
        self.form_vars["harvest_weight_flush3"].insert(0, values[7])
        self.form_vars["performance_notes"].delete("1.0", tk.END)
        self.form_vars["performance_notes"].insert("1.0", values[8])

    def clear_form(self):
        for field_name, widget in self.form_vars.items():
            if isinstance(widget, tk.Text):
                widget.delete("1.0", tk.END)
            elif isinstance(widget, ttk.Entry):
                widget.delete(0, tk.END)
            elif isinstance(widget, ttk.Combobox):
                widget.set("")
            elif isinstance(widget, DateEntry):
                widget.set_date(datetime.now())

    def export_to_csv(self):
        try:
            filename = "bulk_tubs_export.csv"
            
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Get all data
            cursor.execute("SELECT * FROM bulk_tubs")
            rows = cursor.fetchall()
            
            # Get column names
            cursor.execute("PRAGMA table_info(bulk_tubs)")
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