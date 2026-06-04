"""
Example script demonstrating the three new features:
1. Daily Backup Service
2. PDF Report Generation
3. Multi-Language Support (i18n)

Run this script to see the features in action.
"""

import sys
from pathlib import Path
from datetime import datetime

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from service.backup_service import BackupService
from service.pdf_service import PDFReportService
from service.i18n import I18nService
from config import EXCEL_FILE_PATH


def demo_backup_service():
    """Demonstrate backup service functionality."""
    print("\n" + "="*60)
    print("DEMO 1: BACKUP SERVICE (Multi-Format)")
    print("="*60)
    
    backup_service = BackupService()
    
    # Create a manual backup (SQLite + XLSX + ODS)
    print("\n1. Creating manual backup (all formats)...")
    if backup_service.manual_backup():
        print("✓ Manual backup created successfully")
        print("  - SQLite database backed up")
        print("  - Excel file backed up")
        print("  - ODS file backed up")
    
    # List all backups
    print("\n2. Listing all backups...")
    backups = backup_service.list_backups()
    print(f"Found {len(backups)} backup file(s):")
    for backup in backups:
        size_kb = backup.stat().st_size / 1024
        print(f"  - {backup.name} ({size_kb:.2f} KB)")
    
    # List backups by format
    print("\n3. Backups by format:")
    sqlite_backups = backup_service.list_sqlite_backups()
    xlsx_backups = backup_service.list_xlsx_backups()
    ods_backups = backup_service.list_ods_backups()
    print(f"  SQLite: {len(sqlite_backups)} backups")
    print(f"  Excel:  {len(xlsx_backups)} backups")
    print(f"  ODS:    {len(ods_backups)} backups")
    
    # Get backup statistics
    print("\n4. Backup Statistics:")
    stats = backup_service.get_backup_stats()
    for key, value in stats.items():
        print(f"  {key}: {value}")
    
    # Note about backup on close
    print("\n5. Backup on Application Close:")
    print(f"  Backup on close enabled: {backup_service.backup_on_close}")
    print(f"  Auto-empty DB: {backup_service.auto_empty}")
    print(f"  Retention enabled: {backup_service.retention_enabled}")
    
    return backup_service


def demo_pdf_service():
    """Demonstrate PDF report generation."""
    print("\n" + "="*60)
    print("DEMO 2: PDF REPORT GENERATION")
    print("="*60)
    
    pdf_service = PDFReportService()
    
    # Generate Family Assessment Summary
    print("\n1. Generating Family Assessment Summary...")
    sample_families = [
        {
            'family_code': 'FAM-000001',
            'status': 'Active',
            'number_of_children': 3,
            'monthly_income': '$450',
            'monthly_expenses': '$750',
            'assessment_status': 'Complete'
        },
        {
            'family_code': 'FAM-000002',
            'status': 'Active',
            'number_of_children': 2,
            'monthly_income': '$300',
            'monthly_expenses': '$600',
            'assessment_status': 'Pending'
        },
        {
            'family_code': 'FAM-000003',
            'status': 'Inactive',
            'number_of_children': 4,
            'monthly_income': '$500',
            'monthly_expenses': '$850',
            'assessment_status': 'Complete'
        }
    ]
    
    pdf_path = pdf_service.generate_family_assessment_summary(sample_families)
    if pdf_path:
        print(f"✓ Family Assessment Report: {pdf_path.name}")
    
    # Generate Volunteer Activity Report
    print("\n2. Generating Volunteer Activity Report...")
    sample_volunteers = [
        {
            'volunteer_code': 'VOL-000001',
            'name': 'Ahmed Hassan',
            'specialization': 'Education',
            'assignment_count': 3,
            'status': 'Active'
        },
        {
            'volunteer_code': 'VOL-000002',
            'name': 'Fatima Al-Dosari',
            'specialization': 'Healthcare',
            'assignment_count': 2,
            'status': 'Active'
        },
        {
            'volunteer_code': 'VOL-000003',
            'name': 'Mohammed Al-Oraini',
            'specialization': 'Financial Support',
            'assignment_count': 5,
            'status': 'Active'
        }
    ]
    
    pdf_path = pdf_service.generate_volunteer_activity_report(sample_volunteers)
    if pdf_path:
        print(f"✓ Volunteer Activity Report: {pdf_path.name}")
    
    # Generate Financial Overview
    print("\n3. Generating Financial Overview Report...")
    sample_financial = {
        'total_families': 45,
        'total_orphans': 120,
        'active_volunteers': 12,
        'eligible_donors': 28,
        'average_monthly_income': '$425',
        'total_monthly_support': '$18900',
        'average_sponsorship': '$1575'
    }
    
    pdf_path = pdf_service.generate_financial_overview(sample_financial)
    if pdf_path:
        print(f"✓ Financial Overview Report: {pdf_path.name}")
    
    # List all reports
    print("\n4. Listing all generated reports...")
    reports = pdf_service.list_reports()
    print(f"Total reports generated: {len(reports)}")
    for report in reports[:5]:  # Show first 5
        print(f"  - {report.name}")
    if len(reports) > 5:
        print(f"  ... and {len(reports) - 5} more")
    
    return pdf_service


def demo_i18n_service():
    """Demonstrate multi-language support."""
    print("\n" + "="*60)
    print("DEMO 3: MULTI-LANGUAGE SUPPORT (i18n)")
    print("="*60)
    
    # Initialize with English
    i18n = I18nService('en')
    
    print("\n1. Testing English translations:")
    print(f"  welcome: '{i18n.t('welcome')}'")
    print(f"  logout: '{i18n.t('logout')}'")
    print(f"  backup: '{i18n.t('backup')}'")
    print(f"  status: '{i18n.t('status')}'")
    print(f"  Current language: {i18n.get_language_name()}")
    
    # Switch to Arabic
    print("\n2. Switching to Arabic...")
    i18n.set_language('ar')
    print(f"  Current language: {i18n.get_language_name()}")
    
    print("\n3. Testing Arabic translations:")
    print(f"  welcome: '{i18n.t('welcome')}'")
    print(f"  logout: '{i18n.t('logout')}'")
    print(f"  backup: '{i18n.t('backup')}'")
    print(f"  status: '{i18n.t('status')}'")
    print(f"  is_rtl(): {i18n.is_rtl()}")
    
    # List all supported languages
    print("\n4. Supported languages:")
    for code, name in i18n.get_supported_languages().items():
        print(f"  {code}: {name}")
    
    # Add custom translation
    print("\n5. Adding custom translation...")
    i18n.add_translation('en', 'orphan_database', 'Orphan Database')
    i18n.add_translation('ar', 'orphan_database', 'قاعدة بيانات الأيتام')
    
    i18n.set_language('en')
    print(f"  English: '{i18n.t('orphan_database')}'")
    i18n.set_language('ar')
    print(f"  Arabic: '{i18n.t('orphan_database')}'")
    
    # Show available translations
    print("\n6. Sample of available translations:")
    i18n.set_language('en')
    keys = ['kahatayn_system', 'manager_dashboard', 'volunteer', 'backup', 
            'error', 'success', 'loading']
    for key in keys:
        print(f"  {key}: '{i18n.t(key)}'")
    
    return i18n


def demo_integration():
    """Demonstrate how to use all services together."""
    print("\n" + "="*60)
    print("DEMO 4: INTEGRATION EXAMPLE")
    print("="*60)
    
    # Initialize all services
    print("\n1. Initializing all services...")
    backup_service = BackupService()
    pdf_service = PDFReportService()
    i18n = I18nService('en')
    
    print(f"✓ Backup Service initialized")
    print(f"✓ PDF Service initialized")
    print(f"✓ i18n Service initialized (Language: {i18n.get_language_name()})")
    
    # Example workflow
    print("\n2. Example workflow: Manager session with backup on close")
    
    # Change language
    i18n.set_language('ar')
    print(f"\n  Setting language to: {i18n.get_language_name()}")
    
    # Create backup (simulating app close)
    print(f"\n  Creating backup on app close...")
    backup_service.daily_backup()
    print(f"  {i18n.t('backup_completed')}")
    
    # Generate reports
    print(f"\n  Generating reports...")
    families = [
        {'family_code': 'FAM-000001', 'status': 'Active', 'number_of_children': 2,
         'monthly_income': '$400', 'monthly_expenses': '$700', 'assessment_status': 'Complete'}
    ]
    pdf_service.generate_family_assessment_summary(families)
    
    # Status message
    i18n.set_language('en')  # Show status in English
    print(f"  {i18n.t('success')}: {i18n.t('data_saved')}")
    
    print("\n3. Services ready for production use!")
    print("\n  Next: Integrate backup_service.daily_backup() into manager dashboard close handler")


def main():
    """Run all demonstrations."""
    print("\n" + "█"*60)
    print("█" + " "*58 + "█")
    print("█  KAHATAYN SYSTEM - NEW FEATURES DEMONSTRATION  " + " "*10 + "█")
    print("█" + " "*58 + "█")
    print("█"*60)
    
    print(f"\nExecution started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Run demonstrations
    try:
        backup_service = demo_backup_service()
        pdf_service = demo_pdf_service()
        i18n_service = demo_i18n_service()
        demo_integration()
        
        print("\n" + "="*60)
        print("ALL DEMONSTRATIONS COMPLETED SUCCESSFULLY")
        print("="*60)
        
        print("\nNext steps:")
        print("1. Review the generated backups in: data/backups/")
        print("   - Includes SQLite, Excel, and ODS files")
        print("2. Review the generated reports in: data/reports/")
        print("3. Integrate backup_service.daily_backup() into manager dashboard close handler")
        print("4. Update dashboard buttons to use i18n translations")
        print("5. Test PDF report generation with real data")
        
    except Exception as e:
        print(f"\n❌ Error during demonstration: {e}")
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    main()
