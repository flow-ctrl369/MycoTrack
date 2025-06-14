import tkinter as tk
from tkinter import ttk, messagebox
import csv
from datetime import datetime
from tkcalendar import DateEntry

class AgarPlatesTab(ttk.Frame):
    def __init__(self, parent, db):
        super().__init__(parent)
        self.db = db
        self.setup_ui()

    def setup_ui(self):
        # Create main container with padding
        self.main_frame = ttk.Frame(self)
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        # Create left frame for form
        self.form_frame = ttk.LabelFrame(self.main_frame, text="New Agar Plate Entry")
        self.form_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))

        # Create right frame for table
        self.table_frame = ttk.LabelFrame(self.main_frame, text="Agar Plates List")
        self.table_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(5, 0))

        self.setup_form()
        self.setup_table()
        self.setup_search()
        self.load_data()

    def setup_form(self):
        # Form fields
        fields = [
            ("Plate ID:", "plate_id"),
            ("Strain Name:", "strain_name"),
            ("Transfer Round:", "transfer_round"),
            ("Date Inoculated:", "date_inoculated"),
            ("Growth Notes:", "growth_notes"),
            ("Contamination Status:", "contamination_status")
        ]

        # Create and pack form widgets
        self.form_vars = {}
        for i, (label_text, field_name) in enumerate(fields):
            ttk.Label(self.form_frame, text=label_text).grid(row=i, column=0, sticky="e", padx=5, pady=2)
            
            if field_name == "date_inoculated":
                self.form_vars[field_name] = DateEntry(self.form_frame, width=20, background="#262626", foreground="#f0f0f0", headersbackground="#262626", headersforeground="#f0f0f0")
                self.form_vars[field_name].grid(row=i, column=1, sticky="w", padx=5, pady=2)
            elif field_name == "contamination_status":
                self.form_vars[field_name] = ttk.Combobox(self.form_frame, values=["Clean", "Suspected", "Confirmed"])
                self.form_vars[field_name].grid(row=i, column=1, sticky="w", padx=5, pady=2)
            elif field_name == "growth_notes":
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

    def setup_table(self):
        # Create Treeview
        columns = ("Plate ID", "Strain Name", "Transfer Round", "Date Inoculated", 
                  "Growth Notes", "Contamination Status")
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
            # Get values from form
            values = {
                "plate_id": self.form_vars["plate_id"].get(),
                "strain_name": self.form_vars["strain_name"].get(),
                "transfer_round": self.form_vars["transfer_round"].get(),
                "date_inoculated": self.form_vars["date_inoculated"].get_date().isoformat(),
                "growth_notes": self.form_vars["growth_notes"].get("1.0", tk.END).strip(),
                "contamination_status": self.form_vars["contamination_status"].get(),
                "created_at": self.db.get_timestamp(),
                "updated_at": self.db.get_timestamp()
            }

            # Validate required fields
            if not all([values["plate_id"], values["strain_name"], values["transfer_round"]]):
                messagebox.showerror("Error", "Please fill in all required fields")
                return

            # Insert into database
            self.db.cursor.execute('''
                INSERT INTO agar_plates 
                (plate_id, strain_name, transfer_round, date_inoculated, growth_notes, 
                contamination_status, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', tuple(values.values()))
            
            self.db.conn.commit()
            self.load_data()
            self.clear_form()
            messagebox.showinfo("Success", "Record saved successfully")

        except sqlite3.IntegrityError:
            messagebox.showerror("Error", "Plate ID already exists")
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {str(e)}")

    def load_data(self):
        # Clear existing items
        for item in self.tree.get_children():
            self.tree.delete(item)

        # Fetch and display records
        self.db.cursor.execute("SELECT * FROM agar_plates ORDER BY date_inoculated DESC")
        for record in self.db.cursor.fetchall():
            self.tree.insert("", tk.END, values=record[:6])  # Exclude created_at and updated_at

    def filter_records(self, *args):
        search_term = self.search_var.get().lower()
        
        # Clear existing items
        for item in self.tree.get_children():
            self.tree.delete(item)

        # Fetch and filter records
        self.db.cursor.execute("SELECT * FROM agar_plates ORDER BY date_inoculated DESC")
        for record in self.db.cursor.fetchall():
            if any(search_term in str(value).lower() for value in record[:6]):
                self.tree.insert("", tk.END, values=record[:6])

    def edit_record(self, event):
        # Get selected item
        selected_item = self.tree.selection()[0]
        values = self.tree.item(selected_item)["values"]

        # Populate form with selected record
        self.form_vars["plate_id"].delete(0, tk.END)
        self.form_vars["plate_id"].insert(0, values[0])
        self.form_vars["strain_name"].delete(0, tk.END)
        self.form_vars["strain_name"].insert(0, values[1])
        self.form_vars["transfer_round"].delete(0, tk.END)
        self.form_vars["transfer_round"].insert(0, values[2])
        self.form_vars["date_inoculated"].set_date(datetime.strptime(values[3], "%Y-%m-%d"))
        self.form_vars["growth_notes"].delete("1.0", tk.END)
        self.form_vars["growth_notes"].insert("1.0", values[4])
        self.form_vars["contamination_status"].set(values[5])

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
            filename = f"agar_plates_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
            with open(filename, 'w', newline='') as csvfile:
                writer = csv.writer(csvfile)
                # Write headers
                writer.writerow(["Plate ID", "Strain Name", "Transfer Round", 
                               "Date Inoculated", "Growth Notes", "Contamination Status"])
                
                # Write data
                for item in self.tree.get_children():
                    writer.writerow(self.tree.item(item)["values"])
            
            messagebox.showinfo("Success", f"Data exported to {filename}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to export data: {str(e)}") 