import tkinter as tk
from tkinter import ttk
from ttkthemes import ThemedTk

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
            'tree_selected_fg': '#ffffff'
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
            'tree_selected_fg': '#ffffff'
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

        # Configure Text widget colors
        self.root.option_add('*Text.background', colors['entry_bg'])
        self.root.option_add('*Text.foreground', colors['entry_fg'])
        self.root.option_add('*Text.selectBackground', colors['select_bg'])
        self.root.option_add('*Text.selectForeground', colors['select_fg'])

        # Update root window background
        self.root.configure(bg=colors['bg'])

    def get_current_theme(self):
        """Return the current theme state"""
        return "Dark" if self.is_dark_mode else "Light" 