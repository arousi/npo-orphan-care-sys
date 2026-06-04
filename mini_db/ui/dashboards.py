import tkinter as tk
from tkinter import messagebox, ttk
import logging
from config import COLORS, FONT_FAMILY, FONT_SIZE_NORMAL, FONT_SIZE_LARGE, ROLES
from ui.components import (
    StyledFrame, StyledButton, StyledLabel, StyledEntry, FormField, 
    DataTable, SearchBar, ConfirmDialog
)
from models.models import (
    Family, Orphan, Volunteer, Assessment, Sponsorship, Donor, Person
)
from datetime import datetime

logger = logging.getLogger(__name__)

class BaseDashboard(StyledFrame):
    """Base dashboard for all roles."""
    
    def __init__(self, parent, user, repo, on_logout, **kwargs):
        super().__init__(parent, **kwargs)
        self.user = user
        self.repo = repo
        self.on_logout = on_logout
        self.role = user.role if hasattr(user, 'role') else user.get('role')
        
        # Header
        self._create_header()
        
        # Content area
        self.content_frame = StyledFrame(self)
        self.content_frame.pack(fill='both', expand=True, padx=10, pady=10)
    
    def _create_header(self):
        """Create header with user info and logout button."""
        header = StyledFrame(self, bg=COLORS['primary'])
        header.pack(fill='x')
        
        # Title and user info
        username = self.user.username if hasattr(self.user, 'username') else self.user.get('username')
        role_desc = ROLES.get(self.role, {}).get('description', self.role)
        
        title = StyledLabel(header, text=f"Welcome {username} ({role_desc})", 
                           size='large', weight='bold', 
                           fg='white', bg=COLORS['primary'])
        title.pack(side='left', padx=20, pady=10)
        
        # Logout button
        logout_btn = StyledButton(header, text="Logout", style='danger', 
                                 command=self.on_logout)
        logout_btn.pack(side='right', padx=20, pady=10)

class ManagerDashboard(BaseDashboard):
    """Manager dashboard with full system access."""
    
    def __init__(self, parent, user, repo, on_logout, **kwargs):
        super().__init__(parent, user, repo, on_logout, **kwargs)
        self._create_manager_ui()
    
    def _create_manager_ui(self):
        """Create manager-specific UI."""
        # Navigation tabs
        notebook = ttk.Notebook(self.content_frame)
        notebook.pack(fill='both', expand=True)
        
        # Cases tab
        cases_frame = StyledFrame(notebook)
        notebook.add(cases_frame, text="Cases")
        self._create_cases_tab(cases_frame)
        
        # Volunteers tab
        volunteers_frame = StyledFrame(notebook)
        notebook.add(volunteers_frame, text="Volunteers")
        self._create_volunteers_tab(volunteers_frame)
        
        # Reports tab
        reports_frame = StyledFrame(notebook)
        notebook.add(reports_frame, text="Reports & Analytics")
        self._create_reports_tab(reports_frame)
        
        # Settings tab
        settings_frame = StyledFrame(notebook)
        notebook.add(settings_frame, text="Settings")
        self._create_settings_tab(settings_frame)
    
    def _create_cases_tab(self, parent):
        """Create cases management tab."""
        # Search and filter
        search_frame = StyledFrame(parent)
        search_frame.pack(fill='x', padx=10, pady=10)
        
        search = SearchBar(search_frame)
        search.pack(fill='x')
        
        # Create new case button
        new_btn = StyledButton(search_frame, text="+ New Case", style='success',
                              command=self._open_new_case)
        new_btn.pack(anchor='w', pady=5)
        
        # Cases table
        columns = ['ID', 'Family Code', 'Status', 'Children', 'Actions']
        self.cases_table = DataTable(parent, columns)
        self.cases_table.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Load cases
        self._load_cases()
    
    def _load_cases(self):
        """Load cases from repository."""
        try:
            families = self.repo.get_all(Family)
            self.cases_table.clear()
            for family in families:
                if isinstance(family, dict):
                    family_id = family.get('id', 'N/A')
                    code = family.get('family_code', 'N/A')
                    status = family.get('status', 'Active')
                    children = family.get('number_of_children', 0)
                else:
                    family_id = family.id
                    code = family.family_code
                    status = family.status
                    children = family.number_of_children
                
                self.cases_table.add_row([family_id, code, status, children, "Edit/View"])
        except Exception as e:
            logger.error(f"Error loading cases: {e}")
            messagebox.showerror("Error", f"Failed to load cases: {e}")
    
    def _open_new_case(self):
        """Open new case creation window."""
        messagebox.showinfo("New Case", "New case creation form would open here")
        # TODO: Implement case creation form
    
    def _create_volunteers_tab(self, parent):
        """Create volunteers management tab."""
        # New volunteer button
        new_btn = StyledButton(parent, text="+ Add Volunteer", style='success',
                              command=lambda: messagebox.showinfo("Info", "Add volunteer form"))
        new_btn.pack(anchor='w', padx=10, pady=10)
        
        # Volunteers table
        columns = ['ID', 'Name', 'Code', 'Specialization', 'Status']
        table = DataTable(parent, columns)
        table.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Load volunteers
        try:
            volunteers = self.repo.get_all(Volunteer)
            for vol in volunteers:
                if isinstance(vol, dict):
                    table.add_row([vol.get('id'), vol.get('name', 'N/A'), 
                                 vol.get('volunteer_code', 'N/A'), 
                                 vol.get('specialization', 'N/A'),
                                 vol.get('status', 'Active')])
        except Exception as e:
            logger.error(f"Error loading volunteers: {e}")
    
    def _create_reports_tab(self, parent):
        """Create reports and analytics tab."""
        # Report options
        options_frame = StyledFrame(parent)
        options_frame.pack(fill='x', padx=10, pady=10)
        
        StyledLabel(options_frame, text="Generate Report:", weight='bold').pack(anchor='w', pady=5)
        
        reports = [
            ("Family Assessment Summary", "family_summary"),
            ("Volunteer Activity Report", "volunteer_activity"),
            ("Financial Overview", "financial"),
            ("Sponsorship Status", "sponsorship")
        ]
        
        for label, report_type in reports:
            btn = StyledButton(options_frame, text=f"📊 {label}", style='secondary',
                             command=lambda t=report_type: self._generate_report(t))
            btn.pack(anchor='w', padx=20, pady=5)
    
    def _generate_report(self, report_type):
        """Generate and display report."""
        messagebox.showinfo("Report", f"Generating {report_type} report...")
        # TODO: Implement report generation
    
    def _create_settings_tab(self, parent):
        """Create settings tab."""
        settings_frame = StyledFrame(parent)
        settings_frame.pack(fill='x', padx=10, pady=20)
        
        StyledLabel(settings_frame, text="System Settings", weight='bold', size='large').pack(anchor='w', pady=10)
        
        # Backup option
        backup_btn = StyledButton(settings_frame, text="Backup Data", style='secondary',
                                 command=lambda: messagebox.showinfo("Backup", "Backup completed"))
        backup_btn.pack(anchor='w', padx=20, pady=5)
        
        # User management
        users_btn = StyledButton(settings_frame, text="Manage Users", style='secondary',
                               command=lambda: messagebox.showinfo("Users", "User management form"))
        users_btn.pack(anchor='w', padx=20, pady=5)

class VolunteerDashboard(BaseDashboard):
    """Volunteer dashboard with limited access."""
    
    def __init__(self, parent, user, repo, on_logout, **kwargs):
        super().__init__(parent, user, repo, on_logout, **kwargs)
        self._create_volunteer_ui()
    
    def _create_volunteer_ui(self):
        """Create volunteer-specific UI."""
        # Navigation
        notebook = ttk.Notebook(self.content_frame)
        notebook.pack(fill='both', expand=True)
        
        # My Assignments tab
        assignments_frame = StyledFrame(notebook)
        notebook.add(assignments_frame, text="My Assignments")
        self._create_assignments_tab(assignments_frame)
        
        # Activity Log tab
        activity_frame = StyledFrame(notebook)
        notebook.add(activity_frame, text="Activity Log")
        self._create_activity_tab(activity_frame)
    
    def _create_assignments_tab(self, parent):
        """Create my assignments tab."""
        title = StyledLabel(parent, text="My Assigned Families", weight='bold', size='large')
        title.pack(anchor='w', padx=10, pady=10)
        
        columns = ['Family', 'Status', 'Orphans', 'Last Update']
        table = DataTable(parent, columns)
        table.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Sample data
        table.add_row(["FAM-000001", "Active", "2", "2 days ago"])
        table.add_row(["FAM-000002", "Active", "3", "5 days ago"])
    
    def _create_activity_tab(self, parent):
        """Create activity log tab."""
        title = StyledLabel(parent, text="Activity Log", weight='bold', size='large')
        title.pack(anchor='w', padx=10, pady=10)
        
        # Activity form
        form_frame = StyledFrame(parent)
        form_frame.pack(fill='x', padx=10, pady=10)
        
        activity_type = FormField(form_frame, "Activity Type", 'dropdown')
        activity_type.field['values'] = ['Visit', 'Assessment', 'Report', 'Call', 'Other']
        activity_type.pack(fill='x', padx=10, pady=5)
        
        description = FormField(form_frame, "Description", 'textarea')
        description.pack(fill='x', padx=10, pady=5)
        
        save_btn = StyledButton(form_frame, text="Save Activity", style='success',
                              command=lambda: messagebox.showinfo("Saved", "Activity recorded"))
        save_btn.pack(anchor='w', padx=10, pady=10)

class StaffDashboard(BaseDashboard):
    """Staff dashboard for data entry and reporting."""
    
    def __init__(self, parent, user, repo, on_logout, **kwargs):
        super().__init__(parent, user, repo, on_logout, **kwargs)
        self._create_staff_ui()
    
    def _create_staff_ui(self):
        """Create staff-specific UI."""
        notebook = ttk.Notebook(self.content_frame)
        notebook.pack(fill='both', expand=True)
        
        # Data Entry tab
        entry_frame = StyledFrame(notebook)
        notebook.add(entry_frame, text="Data Entry")
        self._create_entry_tab(entry_frame)
        
        # Reports tab
        reports_frame = StyledFrame(notebook)
        notebook.add(reports_frame, text="Reports")
        self._create_staff_reports_tab(reports_frame)
    
    def _create_entry_tab(self, parent):
        """Create data entry tab."""
        title = StyledLabel(parent, text="Quick Data Entry", weight='bold', size='large')
        title.pack(anchor='w', padx=10, pady=10)
        
        form_frame = StyledFrame(parent)
        form_frame.pack(fill='x', padx=10, pady=10)
        
        entry_type = FormField(form_frame, "Entry Type", 'dropdown')
        entry_type.field['values'] = ['New Family', 'Update Assessment', 'Add Document', 'Record Activity']
        entry_type.pack(fill='x', padx=10, pady=5)
        
        details = FormField(form_frame, "Details", 'textarea')
        details.pack(fill='x', padx=10, pady=5)
        
        submit_btn = StyledButton(form_frame, text="Submit Entry", style='success',
                                 command=lambda: messagebox.showinfo("Success", "Entry submitted"))
        submit_btn.pack(anchor='w', padx=10, pady=10)
    
    def _create_staff_reports_tab(self, parent):
        """Create staff reports tab."""
        title = StyledLabel(parent, text="Daily Reports", weight='bold', size='large')
        title.pack(anchor='w', padx=10, pady=10)
        
        columns = ['Date', 'Type', 'Count', 'Status']
        table = DataTable(parent, columns)
        table.pack(fill='both', expand=True, padx=10, pady=10)
        
        table.add_row(["2024-01-15", "Families", "25", "Complete"])
        table.add_row(["2024-01-15", "Assessments", "3", "Complete"])
