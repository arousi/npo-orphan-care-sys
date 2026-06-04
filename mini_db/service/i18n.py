import logging
from pathlib import Path
from typing import Dict, Optional
from config import DEFAULT_LANGUAGE, SUPPORTED_LANGUAGES

logger = logging.getLogger(__name__)


class I18nService:
    """
    Internationalization (i18n) service for multi-language support.
    Supports English and Arabic.
    """
    
    # Translation dictionary
    TRANSLATIONS = {
        'en': {
            # UI Buttons and Labels
            'logout': 'Logout',
            'login': 'Login',
            'username': 'Username',
            'password': 'Password',
            'email': 'Email',
            'new_case': '+ New Case',
            'add_volunteer': '+ Add Volunteer',
            'save': 'Save',
            'cancel': 'Cancel',
            'delete': 'Delete',
            'edit': 'Edit',
            'view': 'View',
            'submit': 'Submit',
            'backup': 'Backup',
            'restore': 'Restore',
            'export': 'Export',
            'import': 'Import',
            
            # Dashboard
            'welcome': 'Welcome',
            'dashboard': 'Dashboard',
            'manager_dashboard': 'Manager Dashboard',
            'volunteer_dashboard': 'Volunteer Dashboard',
            'staff_dashboard': 'Staff Dashboard',
            
            # Tabs
            'cases': 'Cases',
            'volunteers': 'Volunteers',
            'reports': 'Reports & Analytics',
            'settings': 'Settings',
            'my_assignments': 'My Assignments',
            'activity_log': 'Activity Log',
            'data_entry': 'Data Entry',
            'reports_analytics': 'Reports & Analytics',
            
            # Report Types
            'family_assessment_summary': 'Family Assessment Summary',
            'volunteer_activity_report': 'Volunteer Activity Report',
            'financial_overview': 'Financial Overview',
            'sponsorship_status': 'Sponsorship Status',
            'generate_report': 'Generate Report',
            'pdf_report': 'Generate PDF Report',
            'export_excel': 'Export to Excel',
            
            # Fields
            'family_code': 'Family Code',
            'status': 'Status',
            'children': 'Children',
            'actions': 'Actions',
            'name': 'Name',
            'specialization': 'Specialization',
            'volunteer_code': 'Volunteer Code',
            'family': 'Family',
            'last_update': 'Last Update',
            'activity_type': 'Activity Type',
            'description': 'Description',
            'details': 'Details',
            'date': 'Date',
            'time': 'Time',
            
            # Messages
            'backup_completed': 'Backup completed successfully',
            'backup_failed': 'Backup failed',
            'restore_completed': 'Data restored successfully',
            'restore_failed': 'Restore operation failed',
            'data_saved': 'Data saved successfully',
            'error': 'Error',
            'success': 'Success',
            'confirm': 'Confirm',
            'confirm_delete': 'Are you sure you want to delete this item?',
            'no_data': 'No data available',
            'loading': 'Loading...',
            'please_wait': 'Please wait...',
            
            # System
            'system_settings': 'System Settings',
            'user_management': 'Manage Users',
            'manage_users': 'Manage Users',
            'backup_data': 'Backup Data',
            'restore_backup': 'Restore Backup',
            'language': 'Language',
            'select_language': 'Select Language',
            'theme': 'Theme',
            'dark_mode': 'Dark Mode',
            'light_mode': 'Light Mode',
            
            # Navigation
            'home': 'Home',
            'profile': 'Profile',
            'settings': 'Settings',
            'help': 'Help',
            'about': 'About',
            
            # Titles
            'kahatayn_system': 'Kahatayn - Orphan Family Management System',
            'orphan_management': 'Orphan Management System',
            'family_cases': 'Family Cases',
            'volunteer_management': 'Volunteer Management',
            
            # Status options
            'active': 'Active',
            'inactive': 'Inactive',
            'pending': 'Pending',
            'completed': 'Completed',
            
            # Activity types
            'visit': 'Visit',
            'assessment': 'Assessment',
            'report': 'Report',
            'call': 'Call',
            'meeting': 'Meeting',
            'other': 'Other',
            
            # Months
            'january': 'January',
            'february': 'February',
            'march': 'March',
            'april': 'April',
            'may': 'May',
            'june': 'June',
            'july': 'July',
            'august': 'August',
            'september': 'September',
            'october': 'October',
            'november': 'November',
            'december': 'December',
        },
        'ar': {
            # UI Buttons and Labels
            'logout': 'تسجيل الخروج',
            'login': 'تسجيل الدخول',
            'username': 'اسم المستخدم',
            'password': 'كلمة المرور',
            'email': 'البريد الإلكتروني',
            'new_case': '+ حالة جديدة',
            'add_volunteer': '+ إضافة متطوع',
            'save': 'حفظ',
            'cancel': 'إلغاء',
            'delete': 'حذف',
            'edit': 'تعديل',
            'view': 'عرض',
            'submit': 'إرسال',
            'backup': 'نسخ احتياطي',
            'restore': 'استعادة',
            'export': 'تصدير',
            'import': 'استيراد',
            
            # Dashboard
            'welcome': 'أهلا وسهلا',
            'dashboard': 'لوحة التحكم',
            'manager_dashboard': 'لوحة تحكم المدير',
            'volunteer_dashboard': 'لوحة تحكم المتطوع',
            'staff_dashboard': 'لوحة تحكم الموظف',
            
            # Tabs
            'cases': 'الحالات',
            'volunteers': 'المتطوعون',
            'reports': 'التقارير والإحصائيات',
            'settings': 'الإعدادات',
            'my_assignments': 'مهامي',
            'activity_log': 'سجل النشاط',
            'data_entry': 'إدخال البيانات',
            'reports_analytics': 'التقارير والإحصائيات',
            
            # Report Types
            'family_assessment_summary': 'ملخص تقييم الأسرة',
            'volunteer_activity_report': 'تقرير نشاط المتطوع',
            'financial_overview': 'النظرة العامة المالية',
            'sponsorship_status': 'حالة الرعاية',
            'generate_report': 'إنشاء تقرير',
            'pdf_report': 'إنشاء تقرير PDF',
            'export_excel': 'تصدير إلى Excel',
            
            # Fields
            'family_code': 'رمز الأسرة',
            'status': 'الحالة',
            'children': 'الأطفال',
            'actions': 'الإجراءات',
            'name': 'الاسم',
            'specialization': 'التخصص',
            'volunteer_code': 'رمز المتطوع',
            'family': 'الأسرة',
            'last_update': 'آخر تحديث',
            'activity_type': 'نوع النشاط',
            'description': 'الوصف',
            'details': 'التفاصيل',
            'date': 'التاريخ',
            'time': 'الوقت',
            
            # Messages
            'backup_completed': 'تم إنشاء النسخة الاحتياطية بنجاح',
            'backup_failed': 'فشل إنشاء النسخة الاحتياطية',
            'restore_completed': 'تم استعادة البيانات بنجاح',
            'restore_failed': 'فشل عملية الاستعادة',
            'data_saved': 'تم حفظ البيانات بنجاح',
            'error': 'خطأ',
            'success': 'نجاح',
            'confirm': 'تأكيد',
            'confirm_delete': 'هل أنت متأكد من رغبتك في حذف هذا البند؟',
            'no_data': 'لا توجد بيانات متاحة',
            'loading': 'جاري التحميل...',
            'please_wait': 'يرجى الانتظار...',
            
            # System
            'system_settings': 'إعدادات النظام',
            'user_management': 'إدارة المستخدمين',
            'manage_users': 'إدارة المستخدمين',
            'backup_data': 'نسخ احتياطي للبيانات',
            'restore_backup': 'استعادة النسخة الاحتياطية',
            'language': 'اللغة',
            'select_language': 'اختر اللغة',
            'theme': 'المظهر',
            'dark_mode': 'الوضع الداكن',
            'light_mode': 'الوضع الفاتح',
            
            # Navigation
            'home': 'الرئيسية',
            'profile': 'الملف الشخصي',
            'settings': 'الإعدادات',
            'help': 'مساعدة',
            'about': 'حول',
            
            # Titles
            'kahatayn_system': 'كاتاين - نظام إدارة أسر الأيتام',
            'orphan_management': 'نظام إدارة الأيتام',
            'family_cases': 'حالات الأسرة',
            'volunteer_management': 'إدارة المتطوعين',
            
            # Status options
            'active': 'نشط',
            'inactive': 'غير نشط',
            'pending': 'قيد الانتظار',
            'completed': 'مكتمل',
            
            # Activity types
            'visit': 'زيارة',
            'assessment': 'تقييم',
            'report': 'تقرير',
            'call': 'اتصال',
            'meeting': 'اجتماع',
            'other': 'أخرى',
            
            # Months
            'january': 'يناير',
            'february': 'فبراير',
            'march': 'مارس',
            'april': 'أبريل',
            'may': 'مايو',
            'june': 'يونيو',
            'july': 'يوليو',
            'august': 'أغسطس',
            'september': 'سبتمبر',
            'october': 'أكتوبر',
            'november': 'نوفمبر',
            'december': 'ديسمبر',
        }
    }
    
    def __init__(self, language: str = DEFAULT_LANGUAGE):
        """
        Initialize I18n service.
        
        Args:
            language: Language code ('en' or 'ar')
        """
        self.current_language = language if language in SUPPORTED_LANGUAGES else DEFAULT_LANGUAGE
        logger.info(f"I18nService initialized with language: {self.current_language}")
    
    def set_language(self, language: str) -> bool:
        """
        Set the current language.
        
        Args:
            language: Language code ('en' or 'ar')
            
        Returns:
            True if language is supported
        """
        if language in SUPPORTED_LANGUAGES:
            self.current_language = language
            logger.info(f"Language changed to: {language}")
            return True
        else:
            logger.warning(f"Language not supported: {language}")
            return False
    
    def get_language(self) -> str:
        """Get the current language code."""
        return self.current_language
    
    def get_language_name(self) -> str:
        """Get the name of the current language."""
        return SUPPORTED_LANGUAGES.get(self.current_language, self.current_language)
    
    def translate(self, key: str, default: Optional[str] = None) -> str:
        """
        Translate a key to the current language.
        
        Args:
            key: Translation key
            default: Default value if key not found
            
        Returns:
            Translated string
        """
        try:
            lang_dict = self.TRANSLATIONS.get(self.current_language, {})
            return lang_dict.get(key.lower(), default or key)
        except Exception as e:
            logger.error(f"Error translating key '{key}': {e}")
            return default or key
    
    def t(self, key: str, default: Optional[str] = None) -> str:
        """
        Shorthand for translate().
        
        Args:
            key: Translation key
            default: Default value if key not found
            
        Returns:
            Translated string
        """
        return self.translate(key, default)
    
    def is_rtl(self) -> bool:
        """
        Check if current language is right-to-left (RTL).
        
        Returns:
            True if language is RTL (Arabic)
        """
        return self.current_language == 'ar'
    
    def get_supported_languages(self) -> Dict[str, str]:
        """
        Get all supported languages.
        
        Returns:
            Dictionary of language codes and names
        """
        return SUPPORTED_LANGUAGES.copy()
    
    def add_translation(self, language: str, key: str, value: str) -> bool:
        """
        Add or update a translation.
        
        Args:
            language: Language code
            key: Translation key
            value: Translated value
            
        Returns:
            True if successful
        """
        try:
            if language not in self.TRANSLATIONS:
                self.TRANSLATIONS[language] = {}
            
            self.TRANSLATIONS[language][key.lower()] = value
            logger.info(f"Added translation: {language}/{key}")
            return True
        except Exception as e:
            logger.error(f"Error adding translation: {e}")
            return False
    
    def export_translations(self, language: str, output_path: Path) -> bool:
        """
        Export translations to a file for external editing.
        
        Args:
            language: Language code
            output_path: Path to output file
            
        Returns:
            True if successful
        """
        try:
            import json
            lang_dict = self.TRANSLATIONS.get(language, {})
            
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(lang_dict, f, ensure_ascii=False, indent=2)
            
            logger.info(f"Exported {language} translations to: {output_path}")
            return True
        except Exception as e:
            logger.error(f"Error exporting translations: {e}")
            return False
    
    def import_translations(self, language: str, input_path: Path) -> bool:
        """
        Import translations from a file.
        
        Args:
            language: Language code
            input_path: Path to input file
            
        Returns:
            True if successful
        """
        try:
            import json
            
            if not input_path.exists():
                logger.error(f"Translation file not found: {input_path}")
                return False
            
            with open(input_path, 'r', encoding='utf-8') as f:
                translations = json.load(f)
            
            if language not in self.TRANSLATIONS:
                self.TRANSLATIONS[language] = {}
            
            self.TRANSLATIONS[language].update(translations)
            logger.info(f"Imported translations from {input_path} for language {language}")
            return True
        except Exception as e:
            logger.error(f"Error importing translations: {e}")
            return False
