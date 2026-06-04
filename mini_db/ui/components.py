import tkinter as tk
from tkinter import ttk, messagebox
from config import COLORS, FONT_FAMILY, FONT_SIZE_NORMAL, FONT_SIZE_LARGE
import logging

logger = logging.getLogger(__name__)

class StyledFrame(tk.Frame):
    """Custom frame with styling."""
    def __init__(self, parent, bg=None, **kwargs):
        super().__init__(parent, bg=bg or COLORS['light'], **kwargs)

class StyledButton(tk.Button):
    """Custom button with styling."""
    def __init__(self, parent, text="", style="primary", **kwargs):
        bg_color = COLORS.get(style, COLORS['primary'])
        super().__init__(
            parent,
            text=text,
            font=(FONT_FAMILY, FONT_SIZE_NORMAL),
            bg=bg_color,
            fg='white',
            padx=15,
            pady=10,
            relief=tk.RAISED,
            cursor='hand2',
            **kwargs
        )
        self.bind('<Enter>', lambda e: self.config(bg=self._darken_color(bg_color)))
        self.bind('<Leave>', lambda e: self.config(bg=bg_color))
    
    @staticmethod
    def _darken_color(color):
        """Simple color darkening (basic implementation)."""
        return color

class StyledLabel(tk.Label):
    """Custom label with styling."""
    def __init__(self, parent, text="", size="normal", weight="normal", **kwargs):
        font_size = FONT_SIZE_LARGE if size == "large" else FONT_SIZE_NORMAL
        font_weight = "bold" if weight == "bold" else "normal"
        super().__init__(
            parent,
            text=text,
            font=(FONT_FAMILY, font_size, font_weight),
            bg=kwargs.pop('bg', COLORS['light']),
            fg=kwargs.pop('fg', COLORS['text']),
            **kwargs
        )

class StyledEntry(tk.Entry):
    """Custom entry field with styling."""
    def __init__(self, parent, **kwargs):
        super().__init__(
            parent,
            font=(FONT_FAMILY, FONT_SIZE_NORMAL),
            relief=tk.FLAT,
            bd=2,
            **kwargs
        )

class FormField:
    """Reusable form field wrapper."""
    def __init__(self, parent, label_text, field_type='text', required=False):
        self.frame = StyledFrame(parent)
        self.required = required
        self.field_type = field_type
        
        # Label
        label_text_with_req = label_text + (' *' if required else '')
        self.label = StyledLabel(self.frame, text=label_text_with_req)
        self.label.pack(anchor='w', pady=(5, 2))
        
        # Field
        if field_type == 'text':
            self.field = StyledEntry(self.frame)
        elif field_type == 'textarea':
            self.field = tk.Text(self.frame, height=4, width=40, 
                               font=(FONT_FAMILY, FONT_SIZE_NORMAL))
        elif field_type == 'password':
            self.field = StyledEntry(self.frame, show='*')
        elif field_type == 'date':
            self.field = StyledEntry(self.frame)
            self.field.insert(0, 'YYYY-MM-DD')
        elif field_type == 'dropdown':
            self.field = ttk.Combobox(self.frame)
        else:
            self.field = StyledEntry(self.frame)
        
        self.field.pack(fill='x', pady=5)
    
    def get_value(self):
        """Get the field value."""
        if isinstance(self.field, tk.Text):
            return self.field.get('1.0', tk.END).strip()
        else:
            return self.field.get().strip()
    
    def set_value(self, value):
        """Set the field value."""
        if isinstance(self.field, tk.Text):
            self.field.delete('1.0', tk.END)
            self.field.insert('1.0', value)
        else:
            self.field.delete(0, tk.END)
            self.field.insert(0, value)
    
    def validate(self):
        """Validate the field."""
        if self.required and not self.get_value():
            messagebox.showerror("Validation Error", 
                               f"{self.label.cget('text')} is required")
            return False
        return True
    
    def pack(self, **kwargs):
        """Pack the frame."""
        self.frame.pack(**kwargs)

class DataTable(tk.Frame):
    """Reusable data table widget."""
    def __init__(self, parent, columns, **kwargs):
        super().__init__(parent, **kwargs)
        self.columns = columns
        self.data = []
        
        # Create treeview
        self.tree = ttk.Treeview(self, columns=columns, show='headings', height=15)
        
        # Define columns
        for col in columns:
            self.tree.column(col, width=100)
            self.tree.heading(col, text=col)
        
        self.tree.pack(fill='both', expand=True)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(self, orient='vertical', command=self.tree.yview)
        scrollbar.pack(side='right', fill='y')
        self.tree.configure(yscroll=scrollbar.set)
    
    def add_row(self, row_data):
        """Add a row to the table."""
        self.tree.insert('', 'end', values=row_data)
    
    def clear(self):
        """Clear all rows."""
        for item in self.tree.get_children():
            self.tree.delete(item)
    
    def get_selected(self):
        """Get selected row data."""
        selection = self.tree.selection()
        if selection:
            return self.tree.item(selection[0], 'values')
        return None

class SearchBar(tk.Frame):
    """Search and filter bar."""
    def __init__(self, parent, search_callback=None, **kwargs):
        super().__init__(parent, **kwargs)
        
        self.search_var = tk.StringVar()
        
        # Search label
        label = StyledLabel(self, text="Search:")
        label.pack(side='left', padx=5)
        
        # Search entry
        entry = StyledEntry(self)
        entry.pack(side='left', padx=5, fill='x', expand=True)
        self.search_var.trace('w', lambda *args: search_callback(self.search_var.get()) if search_callback else None)
    
    def get_search_text(self):
        """Get search text."""
        return self.search_var.get()

class ConfirmDialog(tk.Toplevel):
    """Confirmation dialog."""
    def __init__(self, parent, title="Confirm", message="Are you sure?", on_confirm=None):
        super().__init__(parent)
        self.title(title)
        self.resizable(False, False)
        self.geometry('400x150')
        self.result = False
        
        # Message
        msg_label = StyledLabel(self, text=message, size='large')
        msg_label.pack(pady=20)
        
        # Buttons
        button_frame = tk.Frame(self, bg=COLORS['light'])
        button_frame.pack(pady=10)
        
        confirm_btn = StyledButton(button_frame, text="Confirm", style='success',
                                  command=self._on_confirm)
        confirm_btn.pack(side='left', padx=5)
        
        cancel_btn = StyledButton(button_frame, text="Cancel", style='danger',
                                 command=self._on_cancel)
        cancel_btn.pack(side='left', padx=5)
        
        self.on_confirm = on_confirm
    
    def _on_confirm(self):
        """Handle confirm."""
        self.result = True
        if self.on_confirm:
            self.on_confirm()
        self.destroy()
    
    def _on_cancel(self):
        """Handle cancel."""
        self.result = False
        self.destroy()
