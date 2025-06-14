import tkinter as tk
from tkinter import ttk, messagebox
import csv
from datetime import datetime
from tkcalendar import DateEntry

class BulkTubsTab(ttk.Frame):
    def __init__(self, parent, db):
        super().__init__(parent)
        self.db = db
        self.cached_records = []  # Add cache for records
        self.setup_ui()

    def setup_ui(self):
        # Create main container with padding
        self.main_frame = ttk.Frame(self)
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=12)

        # Create left frame for form
        self.form_frame = ttk.LabelFrame(self.main_frame, text="New Bulk Tub Entry")
        self.form_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 12))

        # Create right frame for table
        self.table_frame = ttk.LabelFrame(self.main_frame, text="Bulk Tubs List")
        self.table_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(12, 0))

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
            ttk.Label(self.form_frame, text=label_text).grid(row=i, column=0, sticky="e", padx=10, pady=6)
            
            if field_name in ["date_to_bulk", "first_pins_date"]:
                self.form_vars[field_name] = DateEntry(self.form_frame, width=24, background="#262626", foreground="#f0f0f0", headersbackground="#262626", headersforeground="#f0f0f0")
                self.form_vars[field_name].grid(row=i, column=1, sticky="w", padx=10, pady=6)
            elif field_name.startswith("harvest_weight"):
                self.form_vars[field_name] = ttk.Entry(self.form_frame, width=24, font=(None, 14))
                self.form_vars[field_name].grid(row=i, column=1, sticky="w", padx=10, pady=6)
                # Add validation for numeric input
                vcmd = (self.register(self.validate_weight), '%P')
                self.form_vars[field_name].configure(validate='key', validatecommand=vcmd)
            elif field_name == "substrate_type":
                self.form_vars[field_name] = ttk.Combobox(self.form_frame, values=[
                    "CVG (Coir/Verm/Gypsum)",
                    "Manure Based",
                    "Straw Based",
                    "Custom Mix"
                ], width=36, font=(None, 14))
                self.form_vars[field_name].grid(row=i, column=1, sticky="w", padx=10, pady=6)
            elif field_name == "performance_notes":
                self.form_vars[field_name] = tk.Text(self.form_frame, height=4, width=38, bg="#262626", fg="#f0f0f0", insertbackground="#f0f0f0", font=(None, 14))
                self.form_vars[field_name].grid(row=i, column=1, sticky="w", padx=10, pady=6)
            else:
                self.form_vars[field_name] = ttk.Entry(self.form_frame, width=38, font=(None, 14))
                self.form_vars[field_name].grid(row=i, column=1, sticky="w", padx=10, pady=6)

        # Buttons frame
        button_frame = ttk.Frame(self.form_frame)
        button_frame.grid(row=len(fields), column=0, columnspan=2, pady=18)

        ttk.Button(button_frame, text="Save", command=self.save_record).pack(side=tk.LEFT, padx=10, ipadx=8, ipady=4)
        ttk.Button(button_frame, text="Clear", command=self.clear_form).pack(side=tk.LEFT, padx=10, ipadx=8, ipady=4)
        ttk.Button(button_frame, text="Mark First Pins", command=self.mark_first_pins).pack(side=tk.LEFT, padx=10, ipadx=8, ipady=4)

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
        col_widths = [120, 140, 180, 140, 140, 120, 120, 120, 220]
        for col, width in zip(columns, col_widths):
            self.tree.heading(col, text=col)
            self.tree.column(col, width=width, anchor="center")

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
        search_frame.pack(fill=tk.X, pady=10) # Pack at the top of table_frame

        ttk.Label(search_frame, text="Search:").pack(side=tk.LEFT, padx=10)
        self.search_var = tk.StringVar()
        self.search_var.trace("w", self.filter_records)
        ttk.Entry(search_frame, textvariable=self.search_var, width=32, font=(None, 14)).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=10)

        # Export button
        ttk.Button(search_frame, text="Export to CSV", command=self.export_to_csv).pack(side=tk.RIGHT, padx=10, ipadx=8, ipady=4)

    def save_record(self):
        try:
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
                "created_at": self.db.get_timestamp(),
                "updated_at": self.db.get_timestamp()
            }

            # Validate required fields
            if not all([values["tub_id"], values["spawn_source"], values["substrate_type"]]):
                messagebox.showerror("Error", "Please fill in all required fields")
                return

            # Insert into database
            self.db.cursor.execute('''
                INSERT INTO bulk_tubs 
                (tub_id, spawn_source, substrate_type, date_to_bulk, first_pins_date,
                harvest_weight_flush1, harvest_weight_flush2, harvest_weight_flush3,
                performance_notes, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', tuple(values.values()))
            
            self.db.conn.commit()
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
            
            # Update first pins date in database
            self.db.cursor.execute('''
                UPDATE bulk_tubs 
                SET first_pins_date = ?, updated_at = ?
                WHERE tub_id = ?
            ''', (datetime.now().isoformat(), self.db.get_timestamp(), tub_id))
            
            self.db.conn.commit()
            self.load_data()
            messagebox.showinfo("Success", f"Tub {tub_id} marked as having first pins")
        except IndexError:
            messagebox.showerror("Error", "Please select a tub to mark as having first pins")
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {str(e)}")

    def load_data(self):
        # Clear existing items
        for item in self.tree.get_children():
            self.tree.delete(item)

        # Fetch records and cache them
        self.db.cursor.execute("SELECT * FROM bulk_tubs ORDER BY date_to_bulk DESC")
        self.cached_records = self.db.cursor.fetchall()
        
        # Display records
        for record in self.cached_records:
            self.tree.insert("", tk.END, values=record[:9])  # Exclude created_at and updated_at

    def filter_records(self, *args):
        search_term = self.search_var.get().lower()
        
        # Clear existing items
        for item in self.tree.get_children():
            self.tree.delete(item)

        # Filter cached records instead of querying database
        for record in self.cached_records:
            if any(search_term in str(value).lower() for value in record[:9]):
                self.tree.insert("", tk.END, values=record[:9])

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
        if values[4]: # First pins date might be empty
            self.form_vars["first_pins_date"].set_date(datetime.strptime(values[4], "%Y-%m-%d"))
        else:
            self.form_vars["first_pins_date"].set_date(None) # Clear date if empty
        self.form_vars["harvest_weight_flush1"].delete(0, tk.END)
        self.form_vars["harvest_weight_flush1"].insert(0, values[5])
        self.form_vars["harvest_weight_flush2"].delete(0, tk.END)
        self.form_vars["harvest_weight_flush2"].insert(0, values[6])
        self.form_vars["harvest_weight_flush3"].delete(0, tk.END)
        self.form_vars["harvest_weight_flush3"].insert(0, values[7])
        self.form_vars["performance_notes"].delete("1.0", tk.END)
        self.form_vars["performance_notes"].insert("1.0", values[8])

    def clear_form(self):
        for var in self.form_vars.values():
            if isinstance(var, tk.Text):
                var.delete("1.0", tk.END)
            elif isinstance(var, DateEntry):
                var.set_date(datetime.now())
            elif isinstance(var, ttk.Combobox):
                var.set("") # Clear combobox
            else:
                var.delete(0, tk.END)
        
        # Set default for substrate type combobox
        self.form_vars["substrate_type"].set("CVG (Coir/Verm/Gypsum)")

    def export_to_csv(self):
        try:
            filename = f"bulk_tubs_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
            with open(filename, 'w', newline='') as csvfile:
                writer = csv.writer(csvfile)
                # Write headers
                writer.writerow(["Tub ID", "Spawn Source", "Substrate Type", "Date to Bulk", 
                               "First Pins Date", "Harvest Weight Flush 1 (g)", 
                               "Harvest Weight Flush 2 (g)", "Harvest Weight Flush 3 (g)", "Performance Notes"])
                
                # Write data
                for item in self.tree.get_children():
                    writer.writerow(self.tree.item(item)["values"])
            
            messagebox.showinfo("Success", f"Data exported to {filename}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to export data: {str(e)}") 