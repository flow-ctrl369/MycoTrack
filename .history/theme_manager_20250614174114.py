import tkinter as tk
from tkinter import ttk
from ttkthemes import ThemedTk
from tkcalendar import DateEntry, Calendar

class ThemeManager:
    def __init__(self, root):
        self.root = root
        self.is_dark_mode = False
        self.setup_theme()

    def setup_theme(self):
        """Initialize the theme settings"""
        # Define color schemes
        self.light_colors = {
            'bg': '#ffffff',
            'fg': '#000000',
            'select_bg': '#0078d7',
            'select_fg': '#ffffff',
            'button_bg': '#f0f0f0',
            'button_fg': '#000000',
            'entry_bg': '#ffffff',
            'entry_fg': '#000000',
            'tree_bg': '#ffffff',
            'tree_fg': '#000000',
            'tree_selected_bg': '#0078d7',
            'tree_selected_fg': '#ffffff',
            'labelframe_bg': '#ffffff',
            'labelframe_fg': '#000000',
            'notebook_bg': '#ffffff',
            'notebook_fg': '#000000',
            'combobox_bg': '#ffffff',
            'combobox_fg': '#000000',
            'spinbox_bg': '#ffffff',
            'spinbox_fg': '#000000',
            'calendar_bg': '#ffffff',
            'calendar_fg': '#000000',
            'calendar_select_bg': '#0078d7',
            'calendar_select_fg': '#ffffff'
        }

        self.dark_colors = {
            'bg': '#2d2d2d',
            'fg': '#ffffff',
            'select_bg': '#0078d7',
            'select_fg': '#ffffff',
            'button_bg': '#3d3d3d',
            'button_fg': '#ffffff',
            'entry_bg': '#3d3d3d',
            'entry_fg': '#ffffff',
            'tree_bg': '#2d2d2d',
            'tree_fg': '#ffffff',
            'tree_selected_bg': '#0078d7',
            'tree_selected_fg': '#ffffff',
            'labelframe_bg': '#2d2d2d',
            'labelframe_fg': '#ffffff',
            'notebook_bg': '#2d2d2d',
            'notebook_fg': '#ffffff',
            'combobox_bg': '#3d3d3d',
            'combobox_fg': '#ffffff',
            'spinbox_bg': '#3d3d3d',
            'spinbox_fg': '#ffffff',
            'calendar_bg': '#2d2d2d',
            'calendar_fg': '#ffffff',
            'calendar_select_bg': '#0078d7',
            'calendar_select_fg': '#ffffff'
        }

        # Apply initial theme
        self.apply_theme(self.light_colors)

    def toggle_theme(self):
        """Toggle between light and dark mode"""
        self.is_dark_mode = not self.is_dark_mode
        colors = self.dark_colors if self.is_dark_mode else self.light_colors
        self.apply_theme(colors)
        return self.is_dark_mode

    def apply_theme(self, colors):
        """Apply the given color scheme to all widgets"""
        style = ttk.Style()
        
        # Configure common elements
        style.configure('.',
            background=colors['bg'],
            foreground=colors['fg'],
            fieldbackground=colors['entry_bg'],
            selectbackground=colors['select_bg'],
            selectforeground=colors['select_fg']
        )

        # Configure specific widgets
        style.configure('TFrame',
            background=colors['bg']
        )
        
        style.configure('TLabel',
            background=colors['bg'],
            foreground=colors['fg']
        )
        
        style.configure('TButton',
            background=colors['button_bg'],
            foreground=colors['button_fg']
        )
        
        style.configure('TEntry',
            fieldbackground=colors['entry_bg'],
            foreground=colors['entry_fg']
        )
        
        style.configure('Treeview',
            background=colors['tree_bg'],
            foreground=colors['tree_fg'],
            fieldbackground=colors['tree_bg']
        )
        
        style.map('Treeview',
            background=[('selected', colors['tree_selected_bg'])],
            foreground=[('selected', colors['tree_selected_fg'])]
        )

        style.configure('TLabelframe',
            background=colors['labelframe_bg'],
            foreground=colors['labelframe_fg']
        )

        style.configure('TLabelframe.Label',
            background=colors['labelframe_bg'],
            foreground=colors['labelframe_fg']
        )

        style.configure('TNotebook',
            background=colors['notebook_bg'],
            foreground=colors['notebook_fg']
        )

        style.configure('TNotebook.Tab',
            background=colors['button_bg'],
            foreground=colors['button_fg']
        )

        style.map('TNotebook.Tab',
            background=[('selected', colors['select_bg'])],
            foreground=[('selected', colors['select_fg'])]
        )

        style.configure('TCombobox',
            fieldbackground=colors['combobox_bg'],
            background=colors['combobox_bg'],
            foreground=colors['combobox_fg'],
            arrowcolor=colors['combobox_fg']
        )

        style.configure('TSpinbox',
            fieldbackground=colors['spinbox_bg'],
            background=colors['spinbox_bg'],
            foreground=colors['spinbox_fg'],
            arrowcolor=colors['spinbox_fg']
        )

        # Configure Text widget colors
        self.root.option_add('*Text.background', colors['entry_bg'])
        self.root.option_add('*Text.foreground', colors['entry_fg'])
        self.root.option_add('*Text.selectBackground', colors['select_bg'])
        self.root.option_add('*Text.selectForeground', colors['select_fg'])

        # Update root window background
        self.root.configure(bg=colors['bg'])

        # Recursively update all widgets
        self.update_widget_colors(self.root, colors)

    def update_widget_colors(self, widget, colors):
        """Recursively update colors for all child widgets"""
        try:
            if isinstance(widget, DateEntry):
                # Configure DateEntry widget
                widget.configure(
                    background=colors['calendar_bg'],
                    foreground=colors['calendar_fg'],
                    selectbackground=colors['calendar_select_bg'],
                    selectforeground=colors['calendar_select_fg'],
                    normalbackground=colors['calendar_bg'],
                    normalforeground=colors['calendar_fg'],
                    weekendbackground=colors['calendar_bg'],
                    weekendforeground=colors['calendar_fg'],
                    headersbackground=colors['calendar_bg'],
                    headersforeground=colors['calendar_fg']
                )
                # Update the internal calendar widget if it exists
                if hasattr(widget, '_top_cal'):
                    calendar = widget._top_cal
                    calendar.configure(
                        background=colors['calendar_bg'],
                        foreground=colors['calendar_fg'],
                        selectbackground=colors['calendar_select_bg'],
                        selectforeground=colors['calendar_select_fg'],
                        normalbackground=colors['calendar_bg'],
                        normalforeground=colors['calendar_fg'],
                        weekendbackground=colors['calendar_bg'],
                        weekendforeground=colors['calendar_fg'],
                        headersbackground=colors['calendar_bg'],
                        headersforeground=colors['calendar_fg']
                    )
            elif isinstance(widget, Calendar):
                # Configure Calendar widget
                widget.configure(
                    background=colors['calendar_bg'],
                    foreground=colors['calendar_fg'],
                    selectbackground=colors['calendar_select_bg'],
                    selectforeground=colors['calendar_select_fg'],
                    normalbackground=colors['calendar_bg'],
                    normalforeground=colors['calendar_fg'],
                    weekendbackground=colors['calendar_bg'],
                    weekendforeground=colors['calendar_fg'],
                    headersbackground=colors['calendar_bg'],
                    headersforeground=colors['calendar_fg']
                )
            # Explicitly configure tk widgets as ttk.Style does not apply to them
            if isinstance(widget, tk.Frame):
                widget.configure(bg=colors['bg'])
            elif isinstance(widget, tk.Label):
                widget.configure(bg=colors['bg'], fg=colors['fg'])
            elif isinstance(widget, tk.Button):
                widget.configure(bg=colors['button_bg'], fg=colors['button_fg'])
            elif isinstance(widget, tk.Entry):
                widget.configure(bg=colors['entry_bg'], fg=colors['entry_fg'],
                               insertbackground=colors['fg'])
            elif isinstance(widget, tk.Text):
                widget.configure(bg=colors['entry_bg'], fg=colors['entry_fg'],
                               insertbackground=colors['fg'])
            elif isinstance(widget, tk.Listbox):
                widget.configure(bg=colors['entry_bg'], fg=colors['entry_fg'],
                               selectbackground=colors['select_bg'],
                               selectforeground=colors['select_fg'])
            elif isinstance(widget, tk.Canvas):
                widget.configure(bg=colors['bg'])
            # For ttk widgets, re-apply the style configuration
            elif isinstance(widget, ttk.Frame):
                style = ttk.Style()
                style.configure('TFrame', background=colors['bg'])
            elif isinstance(widget, ttk.Label):
                style = ttk.Style()
                style.configure('TLabel', background=colors['bg'], foreground=colors['fg'])
            elif isinstance(widget, ttk.Button):
                style = ttk.Style()
                style.configure('TButton', background=colors['button_bg'], foreground=colors['button_fg'])
            elif isinstance(widget, ttk.Entry):
                style = ttk.Style()
                style.configure('TEntry', fieldbackground=colors['entry_bg'], foreground=colors['entry_fg'])
            elif isinstance(widget, ttk.Treeview):
                style = ttk.Style()
                style.configure('Treeview', background=colors['tree_bg'], foreground=colors['tree_fg'], fieldbackground=colors['tree_bg'])
                style.map('Treeview', background=[('selected', colors['tree_selected_bg'])], foreground=[('selected', colors['tree_selected_fg'])])
            elif isinstance(widget, ttk.LabelFrame):
                style = ttk.Style()
                style.configure('TLabelframe', background=colors['labelframe_bg'], foreground=colors['labelframe_fg'])
                style.configure('TLabelframe.Label', background=colors['labelframe_bg'], foreground=colors['labelframe_fg'])
            elif isinstance(widget, ttk.Notebook):
                style = ttk.Style()
                style.configure('TNotebook', background=colors['notebook_bg'], foreground=colors['notebook_fg'])
                style.configure('TNotebook.Tab', background=colors['button_bg'], foreground=colors['button_fg'])
                style.map('TNotebook.Tab', background=[('selected', colors['select_bg'])], foreground=[('selected', colors['select_fg'])])
            elif isinstance(widget, ttk.Combobox):
                style = ttk.Style()
                style.configure('TCombobox', fieldbackground=colors['combobox_bg'], background=colors['combobox_bg'], foreground=colors['combobox_fg'], arrowcolor=colors['combobox_fg'])
            elif isinstance(widget, ttk.Spinbox):
                style = ttk.Style()
                style.configure('TSpinbox', fieldbackground=colors['spinbox_bg'], background=colors['spinbox_bg'], foreground=colors['spinbox_fg'], arrowcolor=colors['spinbox_fg'])
        except tk.TclError:
            pass  # Skip widgets that can't be configured

        # Update all child widgets
        for child in widget.winfo_children():
            self.update_widget_colors(child, colors)

    def get_current_theme(self):
        """Return the current theme state"""
        return "Dark" if self.is_dark_mode else "Light" 