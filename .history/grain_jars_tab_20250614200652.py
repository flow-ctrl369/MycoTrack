import tkinter as tk
from tkinter import ttk, messagebox
import csv
from datetime import datetime
from tkcalendar import DateEntry
import sqlite3
import re

class GrainJarsTab(ttk.Frame):
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
        self.form_frame = ttk.LabelFrame(self.main_frame, text="New Grain Jar Entry")
        self.form_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 12))

        # Create right frame for table
        self.table_frame = ttk.LabelFrame(self.main_frame, text="Grain Jars List")
        self.table_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(12, 0))

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
            ttk.Label(self.form_frame, text=label_text).grid(row=i, column=0, sticky="e", padx=10, pady=6)
            
            if field_name in ["inoculation_date", "shake_date"]:
                self.form_vars[field_name] = DateEntry(self.form_frame, width=24, background="#262626", foreground="#f0f0f0", headersbackground="#262626", headersforeground="#f0f0f0")
                self.form_vars[field_name].grid(row=i, column=1, sticky="w", padx=10, pady=6)
            elif field_name == "colonization_percentage":
                self.form_vars[field_name] = ttk.Spinbox(
                    self.form_frame, 
                    from_=0, 
                    to=100, 
                    width=24,
                    validate='key',
                    validatecommand=(self.register(self.validate_percentage), '%P'),
                    font=(None, 14)
                )
                self.form_vars[field_name].grid(row=i, column=1, sticky="w", padx=10, pady=6)
            elif field_name == "contamination_notes":
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
        ttk.Button(button_frame, text="Mark as Shaken", command=self.mark_as_shaken).pack(side=tk.LEFT, padx=10, ipadx=8, ipady=4)

        # Source ID
        ttk.Label(self.form_frame, text="LC/Agar Source ID:").grid(row=1, column=0, padx=5, pady=5, sticky="w")
        self.form_vars["source_id"] = ttk.Combobox(self.form_frame, textvariable=self.source_id_var, font=("TkDefaultFont", 14))
        self.form_vars["source_id"].grid(row=1, column=1, padx=5, pady=5, sticky="ew")
        self.form_vars["source_id"].bind("<KeyRelease>", self.update_source_suggestions)
        self.form_vars["source_id"].bind("<<ComboboxSelected>>", self.clear_source_suggestions)
        self.all_source_ids = self.get_all_source_ids()

    def validate_percentage(self, value):
        """Validate that the percentage input is between 0 and 100"""
        if value == "":
            return True
        try:
            num = int(value)
            return 0 <= num <= 100
        except ValueError:
            return False

    def validate_dates(self, inoculation_date, shake_date):
        """Validate date consistency"""
        if not inoculation_date or not shake_date:
            return True
        return inoculation_date <= shake_date

    def validate_source_id(self, source_id):
        """Validate that the source ID exists in either agar_plates or liquid_cultures"""
        if not source_id:
            return False
        # Check agar_plates
        self.db.cursor.execute("SELECT 1 FROM agar_plates WHERE plate_id = ?", (source_id,))
        if self.db.cursor.fetchone():
            return True
        # Check liquid_cultures
        self.db.cursor.execute("SELECT 1 FROM liquid_cultures WHERE lc_id = ?", (source_id,))
        return bool(self.db.cursor.fetchone())

    def validate_jar_id(self, jar_id):
        """Validate jar ID format"""
        if not jar_id:
            return False
        # Check if it matches the pattern GJ-XXXX or GT-XXXX where X is a digit
        return bool(re.match(r"^(GJ|GT)-\d{4}$", jar_id))

    def setup_table(self):
        # Create Treeview
        columns = ("Jar ID", "Source ID", "Inoculation Date", "Colonization %", 
                  "Shake Date", "Contamination Notes")
        self.tree = ttk.Treeview(self.table_frame, columns=columns, show="headings", selectmode="extended")
        
        # Set column headings
        col_widths = [120, 140, 140, 140, 140, 220]
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
        
        # Add right-click menu for batch operations
        self.context_menu = tk.Menu(self.tree, tearoff=0)
        self.context_menu.add_command(label="Mark Selected as Shaken", command=self.batch_mark_shaken)
        self.context_menu.add_command(label="Update Colonization %", command=self.batch_update_colonization)
        self.context_menu.add_command(label="Export Selected", command=self.export_selected)
        self.context_menu.add_separator()
        self.context_menu.add_command(label="Delete Selected", command=self.batch_delete)
        
        self.tree.bind("<Button-3>", self.show_context_menu)

    def show_context_menu(self, event):
        """Show the context menu on right-click"""
        if self.tree.selection():  # Only show menu if items are selected
            self.context_menu.post(event.x_root, event.y_root)

    def batch_mark_shaken(self):
        """Mark all selected jars as shaken with today's date"""
        selected_items = self.tree.selection()
        if not selected_items:
            messagebox.showwarning("Warning", "Please select jars to mark as shaken")
            return

        if messagebox.askyesno("Confirm", f"Mark {len(selected_items)} jars as shaken?"):
            try:
                today = datetime.now().isoformat()
                for item in selected_items:
                    jar_id = self.tree.item(item)["values"][0]
                    self.db.cursor.execute('''
                        UPDATE grain_jars 
                        SET shake_date = ?, updated_at = ?
                        WHERE jar_id = ?
                    ''', (today, self.db.get_timestamp(), jar_id))
                
                self.db.conn.commit()
                self.load_data()
                messagebox.showinfo("Success", f"Marked {len(selected_items)} jars as shaken")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to update jars: {str(e)}")

    def batch_update_colonization(self):
        """Update colonization percentage for selected jars"""
        selected_items = self.tree.selection()
        if not selected_items:
            messagebox.showwarning("Warning", "Please select jars to update")
            return

        # Create dialog for new percentage
        dialog = tk.Toplevel(self)
        dialog.title("Update Colonization %")
        dialog.geometry("300x150")
        
        ttk.Label(dialog, text="New Colonization %:").pack(pady=10)
        percentage_var = tk.StringVar()
        percentage_entry = ttk.Spinbox(
            dialog, 
            from_=0, 
            to=100, 
            textvariable=percentage_var,
            validate='key',
            validatecommand=(self.register(self.validate_percentage), '%P')
        )
        percentage_entry.pack(pady=5)
        
        def apply_update():
            try:
                new_percentage = int(percentage_var.get())
                if not 0 <= new_percentage <= 100:
                    raise ValueError("Percentage must be between 0 and 100")
                
                for item in selected_items:
                    jar_id = self.tree.item(item)["values"][0]
                    self.db.cursor.execute('''
                        UPDATE grain_jars 
                        SET colonization_percentage = ?, updated_at = ?
                        WHERE jar_id = ?
                    ''', (new_percentage, self.db.get_timestamp(), jar_id))
                
                self.db.conn.commit()
                self.load_data()
                dialog.destroy()
                messagebox.showinfo("Success", f"Updated {len(selected_items)} jars")
            except ValueError as e:
                messagebox.showerror("Error", str(e))
            except Exception as e:
                messagebox.showerror("Error", f"Failed to update jars: {str(e)}")
        
        ttk.Button(dialog, text="Apply", command=apply_update).pack(pady=10)

    def batch_delete(self):
        """Delete selected jars after confirmation"""
        selected_items = self.tree.selection()
        if not selected_items:
            messagebox.showwarning("Warning", "Please select jars to delete")
            return

        if messagebox.askyesno("Confirm Delete", 
                             f"Are you sure you want to delete {len(selected_items)} jars?\nThis action cannot be undone."):
            try:
                for item in selected_items:
                    jar_id = self.tree.item(item)["values"][0]
                    self.db.cursor.execute("DELETE FROM grain_jars WHERE jar_id = ?", (jar_id,))
                
                self.db.conn.commit()
                self.load_data()
                messagebox.showinfo("Success", f"Deleted {len(selected_items)} jars")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to delete jars: {str(e)}")

    def export_selected(self):
        """Export selected jars to CSV"""
        selected_items = self.tree.selection()
        if not selected_items:
            messagebox.showwarning("Warning", "Please select jars to export")
            return

        try:
            filename = f"grain_jars_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
            with open(filename, 'w', newline='') as csvfile:
                writer = csv.writer(csvfile)
                # Write headers
                writer.writerow(["Jar ID", "Source ID", "Inoculation Date", 
                               "Colonization %", "Shake Date", "Contamination Notes"])
                
                # Write selected data
                for item in selected_items:
                    writer.writerow(self.tree.item(item)["values"])
            
            messagebox.showinfo("Success", f"Exported {len(selected_items)} jars to {filename}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to export data: {str(e)}")

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
                "jar_id": self.form_vars["jar_id"].get().strip(),
                "source_id": self.form_vars["source_id"].get().strip(),
                "inoculation_date": self.form_vars["inoculation_date"].get_date(),
                "colonization_percentage": int(self.form_vars["colonization_percentage"].get() or 0),
                "shake_date": self.form_vars["shake_date"].get_date() if self.form_vars["shake_date"].get() else None,
                "contamination_notes": self.form_vars["contamination_notes"].get("1.0", tk.END).strip(),
                "created_at": self.db.get_timestamp(),
                "updated_at": self.db.get_timestamp()
            }

            # Enhanced validation
            if not self.validate_jar_id(values["jar_id"]):
                messagebox.showerror("Error", "Jar ID must be in format GJ-XXXX or GT-XXXX (e.g., GJ-0001, GT-0001)")
                return

            if not self.validate_source_id(values["source_id"]):
                messagebox.showerror("Error", "Source ID must exist in Agar Plates or Liquid Cultures")
                return

            if not self.validate_dates(values["inoculation_date"], values["shake_date"]):
                messagebox.showerror("Error", "Shake date cannot be before inoculation date")
                return

            if not 0 <= values["colonization_percentage"] <= 100:
                messagebox.showerror("Error", "Colonization percentage must be between 0 and 100")
                return

            # Convert dates to ISO format for database storage
            values["inoculation_date"] = values["inoculation_date"].isoformat()
            if values["shake_date"]:
                values["shake_date"] = values["shake_date"].isoformat()

            # Insert into database
            self.db.cursor.execute('''
                INSERT INTO grain_jars 
                (jar_id, source_id, inoculation_date, colonization_percentage, 
                shake_date, contamination_notes, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', tuple(values.values()))
            
            self.db.conn.commit()
            self.load_data()
            self.clear_form()
            messagebox.showinfo("Success", "Record saved successfully")

        except sqlite3.IntegrityError:
            messagebox.showerror("Error", "Jar ID already exists")
        except ValueError as e:
            messagebox.showerror("Error", str(e))
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {str(e)}")

    def mark_as_shaken(self):
        """Mark the selected jar as shaken with today's date"""
        try:
            selected_item = self.tree.selection()[0]
            jar_id = self.tree.item(selected_item)["values"][0]
            
            # Update shake date in database
            self.db.cursor.execute('''
                UPDATE grain_jars 
                SET shake_date = ?, updated_at = ?
                WHERE jar_id = ?
            ''', (datetime.now().isoformat(), self.db.get_timestamp(), jar_id))
            
            self.db.conn.commit()
            self.load_data()
            messagebox.showinfo("Success", f"Jar {jar_id} marked as shaken")
        except IndexError:
            messagebox.showerror("Error", "Please select a jar to mark as shaken")
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {str(e)}")

    def load_data(self):
        # Clear existing items
        for item in self.tree.get_children():
            self.tree.delete(item)

        # Fetch records and cache them
        self.db.cursor.execute("SELECT * FROM grain_jars ORDER BY inoculation_date DESC")
        self.cached_records = self.db.cursor.fetchall()
        
        # Display records
        for record in self.cached_records:
            self.tree.insert("", tk.END, values=record[:6])  # Exclude created_at and updated_at

    def filter_records(self, *args):
        search_term = self.search_var.get().lower()
        
        # Clear existing items
        for item in self.tree.get_children():
            self.tree.delete(item)

        # Filter cached records instead of querying database
        for record in self.cached_records:
            if any(search_term in str(value).lower() for value in record[:6]):
                self.tree.insert("", tk.END, values=record[:6])

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
        for var in self.form_vars.values():
            if isinstance(var, tk.Text):
                var.delete("1.0", tk.END)
            elif isinstance(var, DateEntry):
                var.set_date(datetime.now())
            else:
                var.delete(0, tk.END)

    def export_to_csv(self):
        try:
            filename = f"grain_jars_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
            with open(filename, 'w', newline='') as csvfile:
                writer = csv.writer(csvfile)
                # Write headers
                writer.writerow(["Jar ID", "Source ID", "Inoculation Date", 
                               "Colonization %", "Shake Date", "Contamination Notes"])
                
                # Write data
                for item in self.tree.get_children():
                    writer.writerow(self.tree.item(item)["values"])
            
            messagebox.showinfo("Success", f"Data exported to {filename}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to export data: {str(e)}")

    def get_all_source_ids(self):
        """Fetch all LC and Agar Plate IDs from the database"""
        lc_ids = []
        agar_ids = []
        try:
            self.db.cursor.execute("SELECT lc_id FROM liquid_cultures")
            lc_ids = [row[0] for row in self.db.cursor.fetchall()]
            self.db.cursor.execute("SELECT plate_id FROM agar_plates")
            agar_ids = [row[0] for row in self.db.cursor.fetchall()]
        except Exception as e:
            print(f"Error fetching source IDs: {e}") # For debugging
        return sorted(list(set(lc_ids + agar_ids)))

    def update_source_suggestions(self, event):
        """Update combobox suggestions based on current input"""
        search_term = self.source_id_var.get().lower()
        if search_term:
            filtered_ids = [s for s in self.all_source_ids if search_term in s.lower()]
            self.form_vars["source_id"]['values'] = filtered_ids
        else:
            self.form_vars["source_id"]['values'] = self.all_source_ids
        
    def clear_source_suggestions(self, event):
        """Clear combobox values after selection to prevent stale suggestions"""
        self.form_vars["source_id"]['values'] = [] 