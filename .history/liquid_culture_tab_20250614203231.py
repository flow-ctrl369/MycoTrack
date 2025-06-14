import tkinter as tk
from tkinter import ttk, messagebox
import csv
from datetime import datetime
from tkcalendar import DateEntry

class LiquidCultureTab(ttk.Frame):
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
        self.form_frame = ttk.LabelFrame(self.main_frame, text="New Liquid Culture Entry")
        self.form_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 12))

        # Create right frame for table
        self.table_frame = ttk.LabelFrame(self.main_frame, text="Liquid Cultures List")
        self.table_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(12, 0))

        self.setup_form()
        self.setup_table()
        self.load_data()

    def setup_form(self):
        # Form fields
        fields = [
            ("LC ID:", "lc_id"),
            ("Source Plate/Clone:", "source_id"),
            ("Strain Name:", "strain_name"),
            ("Inoculation Date:", "inoculation_date"),
            ("Growth Description:", "growth_description"),
            ("Viability:", "viability"),
            ("Volume Remaining (mL):", "volume_remaining")
        ]

        # Create and pack form widgets
        self.form_vars = {}
        for i, (label_text, field_name) in enumerate(fields):
            ttk.Label(self.form_frame, text=label_text).grid(row=i, column=0, sticky="e", padx=10, pady=6)
            
            if field_name == "inoculation_date":
                self.form_vars[field_name] = DateEntry(self.form_frame, width=24, background="#262626", foreground="#f0f0f0", headersbackground="#262626", headersforeground="#f0f0f0")
                self.form_vars[field_name].grid(row=i, column=1, sticky="w", padx=10, pady=6)
            elif field_name == "viability":
                self.form_vars[field_name] = ttk.Combobox(self.form_frame, values=["Untested", "Passed", "Contaminated"], width=36, font=(None, 14))
                self.form_vars[field_name].grid(row=i, column=1, sticky="w", padx=10, pady=6)
            elif field_name == "growth_description":
                self.form_vars[field_name] = tk.Text(self.form_frame, height=4, width=38, bg="#262626", fg="#f0f0f0", insertbackground="#f0f0f0", font=(None, 14))
                self.form_vars[field_name].grid(row=i, column=1, sticky="w", padx=10, pady=6)
            elif field_name == "volume_remaining":
                self.form_vars[field_name] = ttk.Entry(self.form_frame, width=38, font=(None, 14))
                self.form_vars[field_name].grid(row=i, column=1, sticky="w", padx=10, pady=6)
                # Add validation for numeric input
                vcmd = (self.register(self.validate_volume), '%P')
                self.form_vars[field_name].configure(validate='key', validatecommand=vcmd)
            else:
                self.form_vars[field_name] = ttk.Entry(self.form_frame, width=38, font=(None, 14))
                self.form_vars[field_name].grid(row=i, column=1, sticky="w", padx=10, pady=6)

        # Buttons frame
        button_frame = ttk.Frame(self.form_frame)
        button_frame.grid(row=len(fields), column=0, columnspan=2, pady=18)

        ttk.Button(button_frame, text="Save", command=self.save_record).pack(side=tk.LEFT, padx=10, ipadx=8, ipady=4)
        ttk.Button(button_frame, text="Clear", command=self.clear_form).pack(side=tk.LEFT, padx=10, ipadx=8, ipady=4)

        # Search frame (moved from setup_search)
        search_frame = ttk.Frame(self.form_frame)
        search_frame.grid(row=len(fields) + 1, column=0, columnspan=2, sticky="ew", pady=(0, 10))

        ttk.Label(search_frame, text="Search:").pack(side=tk.LEFT, padx=(10,0))
        self.search_var = tk.StringVar()
        self.search_var.trace("w", self.filter_records)
        ttk.Entry(search_frame, textvariable=self.search_var, font=(None, 14)).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=10)

        # Export button (moved from setup_search)
        ttk.Button(search_frame, text="Export to CSV", command=self.export_to_csv).pack(side=tk.RIGHT, padx=(0,10), ipadx=8, ipady=4)

    def validate_volume(self, value):
        """Validate that the volume input is a positive number"""
        if value == "":
            return True
        try:
            float(value)
            return True
        except ValueError:
            return False

    def setup_table(self):
        # Create Treeview
        columns = ("LC ID", "Source ID", "Strain Name", "Inoculation Date", 
                  "Growth Description", "Viability", "Volume (mL)")
        self.tree = ttk.Treeview(self.table_frame, columns=columns, show="headings")
        
        # Set column headings
        col_widths = [120, 140, 180, 140, 220, 120, 120]
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

    def save_record(self):
        try:
            # Get values from form
            values = {
                "lc_id": self.form_vars["lc_id"].get(),
                "source_id": self.form_vars["source_id"].get(),
                "strain_name": self.form_vars["strain_name"].get(),
                "inoculation_date": self.form_vars["inoculation_date"].get_date().isoformat(),
                "growth_description": self.form_vars["growth_description"].get("1.0", tk.END).strip(),
                "viability": self.form_vars["viability"].get(),
                "volume_remaining": float(self.form_vars["volume_remaining"].get() or 0),
                "created_at": self.db.get_timestamp(),
                "updated_at": self.db.get_timestamp()
            }

            # Validate required fields
            if not all([values["lc_id"], values["source_id"], values["strain_name"]]):
                messagebox.showerror("Error", "Please fill in all required fields")
                return

            # Insert into database
            self.db.cursor.execute('''
                INSERT INTO liquid_cultures 
                (lc_id, source_id, strain_name, inoculation_date, growth_description, 
                viability, volume_remaining, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', tuple(values.values()))
            
            self.db.conn.commit()
            self.load_data()
            self.clear_form()
            messagebox.showinfo("Success", "Record saved successfully")

        except sqlite3.IntegrityError:
            messagebox.showerror("Error", "LC ID already exists")
        except ValueError:
            messagebox.showerror("Error", "Volume must be a valid number")
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {str(e)}")

    def load_data(self):
        # Clear existing items
        for item in self.tree.get_children():
            self.tree.delete(item)

        # Fetch records and cache them
        self.db.cursor.execute("SELECT * FROM liquid_cultures ORDER BY inoculation_date DESC")
        self.cached_records = self.db.cursor.fetchall()
        
        # Display records
        for record in self.cached_records:
            self.tree.insert("", tk.END, values=record[:7])  # Exclude created_at and updated_at

    def filter_records(self, *args):
        search_term = self.search_var.get().lower()
        
        # Clear existing items
        for item in self.tree.get_children():
            self.tree.delete(item)

        # Filter cached records instead of querying database
        for record in self.cached_records:
            if any(search_term in str(value).lower() for value in record[:7]):
                self.tree.insert("", tk.END, values=record[:7])

    def edit_record(self, event):
        # Get selected item
        selected_item = self.tree.selection()[0]
        values = self.tree.item(selected_item)["values"]

        # Populate form with selected record
        self.form_vars["lc_id"].delete(0, tk.END)
        self.form_vars["lc_id"].insert(0, values[0])
        self.form_vars["source_id"].delete(0, tk.END)
        self.form_vars["source_id"].insert(0, values[1])
        self.form_vars["strain_name"].delete(0, tk.END)
        self.form_vars["strain_name"].insert(0, values[2])
        self.form_vars["inoculation_date"].set_date(datetime.strptime(values[3], "%Y-%m-%d"))
        self.form_vars["growth_description"].delete("1.0", tk.END)
        self.form_vars["growth_description"].insert("1.0", values[4])
        self.form_vars["viability"].set(values[5])
        self.form_vars["volume_remaining"].delete(0, tk.END)
        self.form_vars["volume_remaining"].insert(0, values[6])

    def clear_form(self):
        for var in self.form_vars.values():
            if isinstance(var, tk.Text):
                var.delete("1.0", tk.END)
            elif isinstance(var, DateEntry):
                var.set_date(datetime.now())
            elif isinstance(var, ttk.Combobox):
                var.set("")
            else:
                var.delete(0, tk.END)

    def export_to_csv(self):
        try:
            filename = f"liquid_cultures_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
            with open(filename, 'w', newline='') as csvfile:
                writer = csv.writer(csvfile)
                # Write headers
                writer.writerow(["LC ID", "Source ID", "Strain Name", "Inoculation Date", 
                               "Growth Description", "Viability", "Volume (mL)"])
                
                # Write data
                for item in self.tree.get_children():
                    writer.writerow(self.tree.item(item)["values"])
            
            messagebox.showinfo("Success", f"Data exported to {filename}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to export data: {str(e)}") 