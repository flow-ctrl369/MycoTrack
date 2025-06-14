import tkinter as tk
from tkinter import ttk, messagebox
import csv
from datetime import datetime
from tkcalendar import DateEntry

class CloneLibraryTab(ttk.Frame):
    def __init__(self, parent, db):
        super().__init__(parent)
        self.db = db
        self.setup_ui()

    def setup_ui(self):
        # Create main container with padding
        self.main_frame = ttk.Frame(self)
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=12)

        # Create left frame for form
        self.form_frame = ttk.LabelFrame(self.main_frame, text="New Clone Entry")
        self.form_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 12))

        # Create right frame for table
        self.table_frame = ttk.LabelFrame(self.main_frame, text="Clone Library")
        self.table_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(12, 0))

        self.setup_form()
        self.setup_table()
        self.setup_search()
        self.load_data()

    def setup_form(self):
        # Form fields
        fields = [
            ("Clone ID:", "clone_id"),
            ("Parent Strain:", "parent_strain"),
            ("Date Taken:", "date_taken"),
            ("Tissue Source:", "tissue_source"),
            ("Growth Characteristics:", "growth_characteristics"),
            ("Performance Notes:", "performance_notes")
        ]

        # Create and pack form widgets
        self.form_vars = {}
        for i, (label_text, field_name) in enumerate(fields):
            ttk.Label(self.form_frame, text=label_text).grid(row=i, column=0, sticky="e", padx=10, pady=6)
            
            if field_name == "date_taken":
                self.form_vars[field_name] = DateEntry(self.form_frame, width=24, background="#262626", foreground="#f0f0f0", headersbackground="#262626", headersforeground="#f0f0f0")
                self.form_vars[field_name].grid(row=i, column=1, sticky="w", padx=10, pady=6)
            elif field_name == "tissue_source":
                self.form_vars[field_name] = ttk.Combobox(self.form_frame, values=[
                    "Cap",
                    "Stem Base",
                    "Stem Middle",
                    "Stem Top",
                    "Gill Tissue",
                    "Other"
                ], width=36, font=(None, 14))
                self.form_vars[field_name].grid(row=i, column=1, sticky="w", padx=10, pady=6)
            elif field_name in ["growth_characteristics", "performance_notes"]:
                self.form_vars[field_name] = tk.Text(self.form_frame, height=4, width=38, bg="#262626", fg="#f0f0f0", insertbackground="#f0f0f0", font=(None, 14))
                self.form_vars[field_name].grid(row=i, column=1, sticky="w", padx=10, pady=6)
            else:
                self.form_vars[field_name] = ttk.Entry(self.form_frame, width=38, font=(None, 14))
                self.form_vars[field_name].grid(row=i, column=1, sticky="w", padx=10, pady=6)

        # Add tooltips
        self.add_tooltips()

        # Buttons frame
        button_frame = ttk.Frame(self.form_frame)
        button_frame.grid(row=len(fields), column=0, columnspan=2, pady=18)

        ttk.Button(button_frame, text="Save", command=self.save_record).pack(side=tk.LEFT, padx=10, ipadx=8, ipady=4)
        ttk.Button(button_frame, text="Clear", command=self.clear_form).pack(side=tk.LEFT, padx=10, ipadx=8, ipady=4)
        ttk.Button(button_frame, text="Archive Clone", command=self.archive_clone).pack(side=tk.LEFT, padx=10, ipadx=8, ipady=4)

    def add_tooltips(self):
        """Add tooltips to form fields"""
        tooltips = {
            "clone_id": "Unique identifier for the clone (e.g., CL-001)",
            "parent_strain": "Original strain name of the parent mushroom",
            "date_taken": "Date when the clone was taken",
            "tissue_source": "Part of the mushroom used for cloning",
            "growth_characteristics": "Describe growth patterns, speed, and morphology",
            "performance_notes": "Notes on fruiting performance, yield, and characteristics"
        }

        for field_name, tooltip_text in tooltips.items():
            self.create_tooltip(self.form_vars[field_name], tooltip_text)

    def create_tooltip(self, widget, text):
        """Create a tooltip for a given widget"""
        def show_tooltip(event):
            tooltip = tk.Toplevel()
            tooltip.wm_overrideredirect(True)
            tooltip.wm_geometry(f"+{event.x_root+10}+{event.y_root+10}")
            
            label = ttk.Label(tooltip, text=text, justify=tk.LEFT,
                            background="#262626", foreground="#f0f0f0", relief=tk.SOLID, borderwidth=1)
            label.pack()
            
            def hide_tooltip():
                tooltip.destroy()
            
            widget.tooltip = tooltip
            widget.bind('<Leave>', lambda e: hide_tooltip())
            tooltip.bind('<Leave>', lambda e: hide_tooltip())

        widget.bind('<Enter>', show_tooltip)

    def setup_table(self):
        # Create Treeview
        columns = ("Clone ID", "Parent Strain", "Date Taken", "Tissue Source", 
                  "Growth Characteristics", "Performance Notes")
        self.tree = ttk.Treeview(self.table_frame, columns=columns, show="headings")
        
        # Set column headings
        col_widths = [120, 180, 140, 140, 220, 220]
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
        search_frame.pack(fill=tk.X, pady=10)

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
                "clone_id": self.form_vars["clone_id"].get(),
                "parent_strain": self.form_vars["parent_strain"].get(),
                "date_taken": self.form_vars["date_taken"].get_date().isoformat(),
                "tissue_source": self.form_vars["tissue_source"].get(),
                "growth_characteristics": self.form_vars["growth_characteristics"].get("1.0", tk.END).strip(),
                "performance_notes": self.form_vars["performance_notes"].get("1.0", tk.END).strip(),
                "created_at": self.db.get_timestamp(),
                "updated_at": self.db.get_timestamp()
            }

            # Validate required fields
            if not all([values["clone_id"], values["parent_strain"], values["tissue_source"]]):
                messagebox.showerror("Error", "Please fill in all required fields")
                return

            # Insert into database
            self.db.cursor.execute('''
                INSERT INTO clone_library 
                (clone_id, parent_strain, date_taken, tissue_source,
                growth_characteristics, performance_notes, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', tuple(values.values()))
            
            self.db.conn.commit()
            self.load_data()
            self.clear_form()
            messagebox.showinfo("Success", "Record saved successfully")

        except sqlite3.IntegrityError:
            messagebox.showerror("Error", "Clone ID already exists")
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {str(e)}")

    def archive_clone(self):
        """Archive the selected clone"""
        try:
            selected_item = self.tree.selection()[0]
            clone_id = self.tree.item(selected_item)["values"][0]
            
            if messagebox.askyesno("Confirm Archive", 
                                 f"Are you sure you want to archive clone {clone_id}?"):
                # Update clone status in database
                self.db.cursor.execute('''
                    UPDATE clone_library 
                    SET archived = 1, updated_at = ?
                    WHERE clone_id = ?
                ''', (self.db.get_timestamp(), clone_id))
                
                self.db.conn.commit()
                self.load_data()
                messagebox.showinfo("Success", f"Clone {clone_id} has been archived")
        except IndexError:
            messagebox.showerror("Error", "Please select a clone to archive")
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {str(e)}")

    def load_data(self):
        # Clear existing items
        for item in self.tree.get_children():
            self.tree.delete(item)

        # Fetch and display records
        self.db.cursor.execute("SELECT * FROM clone_library WHERE archived = 0 ORDER BY date_taken DESC")
        for record in self.db.cursor.fetchall():
            self.tree.insert("", tk.END, values=record[:6])  # Exclude created_at and updated_at

    def filter_records(self, *args):
        search_term = self.search_var.get().lower()
        
        # Clear existing items
        for item in self.tree.get_children():
            self.tree.delete(item)

        # Fetch and filter records
        self.db.cursor.execute("SELECT * FROM clone_library WHERE archived = 0 ORDER BY date_taken DESC")
        for record in self.db.cursor.fetchall():
            if any(search_term in str(value).lower() for value in record[:6]):
                self.tree.insert("", tk.END, values=record[:6])

    def edit_record(self, event):
        # Get selected item
        selected_item = self.tree.selection()[0]
        values = self.tree.item(selected_item)["values"]

        # Populate form with selected record
        self.form_vars["clone_id"].delete(0, tk.END)
        self.form_vars["clone_id"].insert(0, values[0])
        self.form_vars["parent_strain"].delete(0, tk.END)
        self.form_vars["parent_strain"].insert(0, values[1])
        self.form_vars["date_taken"].set_date(datetime.strptime(values[2], "%Y-%m-%d"))
        self.form_vars["tissue_source"].set(values[3])
        self.form_vars["growth_characteristics"].delete("1.0", tk.END)
        self.form_vars["growth_characteristics"].insert("1.0", values[4])
        self.form_vars["performance_notes"].delete("1.0", tk.END)
        self.form_vars["performance_notes"].insert("1.0", values[5])

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
            filename = f"clone_library_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
            with open(filename, 'w', newline='') as csvfile:
                writer = csv.writer(csvfile)
                # Write headers
                writer.writerow(["Clone ID", "Parent Strain", "Date Taken", 
                               "Tissue Source", "Growth Characteristics", "Performance Notes"])
                
                # Write data
                for item in self.tree.get_children():
                    writer.writerow(self.tree.item(item)["values"])
            
            messagebox.showinfo("Success", f"Data exported to {filename}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to export data: {str(e)}") 