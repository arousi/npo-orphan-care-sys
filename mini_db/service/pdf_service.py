import logging
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional
from config import DATA_DIR, COLORS
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak
from reportlab.lib import colors as rl_colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT

logger = logging.getLogger(__name__)


class PDFReportService:
    """Generates PDF reports from application data."""
    
    def __init__(self):
        """Initialize PDF report service."""
        self.output_dir = DATA_DIR / "reports"
        self.output_dir.mkdir(exist_ok=True)
        logger.info(f"PDFReportService initialized. Output directory: {self.output_dir}")
    
    def generate_family_assessment_summary(self, families: List[Dict], 
                                          filename: Optional[str] = None) -> Optional[Path]:
        """
        Generate a PDF report summarizing family assessments.
        
        Args:
            families: List of family dictionaries
            filename: Optional output filename
            
        Returns:
            Path to generated PDF file
        """
        try:
            if not filename:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"family_assessment_{timestamp}.pdf"
            
            pdf_path = self.output_dir / filename
            
            doc = SimpleDocTemplate(
                str(pdf_path),
                pagesize=letter,
                rightMargin=0.75*inch,
                leftMargin=0.75*inch,
                topMargin=0.75*inch,
                bottomMargin=0.75*inch
            )
            
            story = []
            styles = getSampleStyleSheet()
            
            # Title
            title_style = ParagraphStyle(
                'CustomTitle',
                parent=styles['Heading1'],
                fontSize=16,
                textColor=rl_colors.HexColor(COLORS['primary']),
                alignment=TA_CENTER,
                spaceAfter=12
            )
            story.append(Paragraph("Family Assessment Summary Report", title_style))
            story.append(Spacer(1, 0.2*inch))
            
            # Report metadata
            meta_text = f"Generated: {datetime.now().strftime('%B %d, %Y at %H:%M')}<br/>Total Families: {len(families)}"
            meta_style = ParagraphStyle(
                'Metadata',
                parent=styles['Normal'],
                fontSize=9,
                textColor=rl_colors.grey,
                alignment=TA_CENTER
            )
            story.append(Paragraph(meta_text, meta_style))
            story.append(Spacer(1, 0.3*inch))
            
            # Table data
            if families:
                table_data = [
                    ['Family Code', 'Status', 'Children', 'Income', 'Expenses', 'Assessment Status']
                ]
                
                for family in families:
                    if isinstance(family, dict):
                        table_data.append([
                            family.get('family_code', 'N/A'),
                            family.get('status', 'Active'),
                            str(family.get('number_of_children', 0)),
                            family.get('monthly_income', 'N/A'),
                            family.get('monthly_expenses', 'N/A'),
                            family.get('assessment_status', 'Pending')
                        ])
                
                # Create table
                table = Table(table_data, colWidths=[1.2*inch, 1*inch, 1*inch, 1.2*inch, 1.2*inch, 1.3*inch])
                table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), rl_colors.HexColor(COLORS['primary'])),
                    ('TEXTCOLOR', (0, 0), (-1, 0), rl_colors.whitesmoke),
                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, 0), 10),
                    ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                    ('BACKGROUND', (0, 1), (-1, -1), rl_colors.beige),
                    ('GRID', (0, 0), (-1, -1), 1, rl_colors.black),
                    ('FONTSIZE', (0, 1), (-1, -1), 9),
                    ('ROWBACKGROUNDS', (0, 1), (-1, -1), [rl_colors.white, rl_colors.HexColor('#F5F5F5')])
                ]))
                
                story.append(table)
            else:
                story.append(Paragraph("No families found in database.", styles['Normal']))
            
            # Build PDF
            doc.build(story)
            logger.info(f"Generated Family Assessment Summary: {pdf_path}")
            return pdf_path
        except Exception as e:
            logger.error(f"Error generating family assessment summary: {e}")
            return None
    
    def generate_volunteer_activity_report(self, volunteers: List[Dict],
                                          filename: Optional[str] = None) -> Optional[Path]:
        """
        Generate a PDF report of volunteer activities.
        
        Args:
            volunteers: List of volunteer dictionaries
            filename: Optional output filename
            
        Returns:
            Path to generated PDF file
        """
        try:
            if not filename:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"volunteer_activity_{timestamp}.pdf"
            
            pdf_path = self.output_dir / filename
            
            doc = SimpleDocTemplate(
                str(pdf_path),
                pagesize=letter,
                rightMargin=0.75*inch,
                leftMargin=0.75*inch,
                topMargin=0.75*inch,
                bottomMargin=0.75*inch
            )
            
            story = []
            styles = getSampleStyleSheet()
            
            # Title
            title_style = ParagraphStyle(
                'CustomTitle',
                parent=styles['Heading1'],
                fontSize=16,
                textColor=rl_colors.HexColor(COLORS['primary']),
                alignment=TA_CENTER,
                spaceAfter=12
            )
            story.append(Paragraph("Volunteer Activity Report", title_style))
            story.append(Spacer(1, 0.2*inch))
            
            # Report metadata
            meta_text = f"Generated: {datetime.now().strftime('%B %d, %Y at %H:%M')}<br/>Total Volunteers: {len(volunteers)}"
            meta_style = ParagraphStyle(
                'Metadata',
                parent=styles['Normal'],
                fontSize=9,
                textColor=rl_colors.grey,
                alignment=TA_CENTER
            )
            story.append(Paragraph(meta_text, meta_style))
            story.append(Spacer(1, 0.3*inch))
            
            # Table data
            if volunteers:
                table_data = [
                    ['Volunteer Code', 'Name', 'Specialization', 'Assignments', 'Status']
                ]
                
                for vol in volunteers:
                    if isinstance(vol, dict):
                        table_data.append([
                            vol.get('volunteer_code', 'N/A'),
                            vol.get('name', 'N/A'),
                            vol.get('specialization', 'General'),
                            str(vol.get('assignment_count', 0)),
                            vol.get('status', 'Active')
                        ])
                
                table = Table(table_data, colWidths=[1.3*inch, 1.5*inch, 1.3*inch, 1.2*inch, 1.2*inch])
                table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), rl_colors.HexColor(COLORS['success'])),
                    ('TEXTCOLOR', (0, 0), (-1, 0), rl_colors.whitesmoke),
                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, 0), 10),
                    ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                    ('BACKGROUND', (0, 1), (-1, -1), rl_colors.lightgreen),
                    ('GRID', (0, 0), (-1, -1), 1, rl_colors.black),
                    ('FONTSIZE', (0, 1), (-1, -1), 9),
                    ('ROWBACKGROUNDS', (0, 1), (-1, -1), [rl_colors.white, rl_colors.HexColor('#F0F8F0')])
                ]))
                
                story.append(table)
            else:
                story.append(Paragraph("No volunteers found in database.", styles['Normal']))
            
            doc.build(story)
            logger.info(f"Generated Volunteer Activity Report: {pdf_path}")
            return pdf_path
        except Exception as e:
            logger.error(f"Error generating volunteer activity report: {e}")
            return None
    
    def generate_financial_overview(self, financial_data: Dict,
                                   filename: Optional[str] = None) -> Optional[Path]:
        """
        Generate a PDF report with financial overview.
        
        Args:
            financial_data: Dictionary with financial information
            filename: Optional output filename
            
        Returns:
            Path to generated PDF file
        """
        try:
            if not filename:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"financial_overview_{timestamp}.pdf"
            
            pdf_path = self.output_dir / filename
            
            doc = SimpleDocTemplate(
                str(pdf_path),
                pagesize=letter,
                rightMargin=0.75*inch,
                leftMargin=0.75*inch,
                topMargin=0.75*inch,
                bottomMargin=0.75*inch
            )
            
            story = []
            styles = getSampleStyleSheet()
            
            # Title
            title_style = ParagraphStyle(
                'CustomTitle',
                parent=styles['Heading1'],
                fontSize=16,
                textColor=rl_colors.HexColor(COLORS['primary']),
                alignment=TA_CENTER,
                spaceAfter=12
            )
            story.append(Paragraph("Financial Overview Report", title_style))
            story.append(Spacer(1, 0.2*inch))
            
            # Report metadata
            meta_text = f"Generated: {datetime.now().strftime('%B %d, %Y at %H:%M')}"
            meta_style = ParagraphStyle(
                'Metadata',
                parent=styles['Normal'],
                fontSize=9,
                textColor=rl_colors.grey,
                alignment=TA_CENTER
            )
            story.append(Paragraph(meta_text, meta_style))
            story.append(Spacer(1, 0.3*inch))
            
            # Financial summary table
            if financial_data:
                table_data = [['Metric', 'Amount']]
                
                for key, value in financial_data.items():
                    table_data.append([key.replace('_', ' ').title(), str(value)])
                
                table = Table(table_data, colWidths=[3*inch, 2*inch])
                table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), rl_colors.HexColor(COLORS['warning'])),
                    ('TEXTCOLOR', (0, 0), (-1, 0), rl_colors.whitesmoke),
                    ('ALIGN', (0, 0), (0, -1), 'LEFT'),
                    ('ALIGN', (1, 0), (-1, -1), 'RIGHT'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, 0), 11),
                    ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                    ('BACKGROUND', (0, 1), (-1, -1), rl_colors.lightyellow),
                    ('GRID', (0, 0), (-1, -1), 1, rl_colors.black),
                    ('FONTSIZE', (0, 1), (-1, -1), 10),
                    ('ROWBACKGROUNDS', (0, 1), (-1, -1), [rl_colors.white, rl_colors.HexColor('#FFFEF0')])
                ]))
                
                story.append(table)
            else:
                story.append(Paragraph("No financial data available.", styles['Normal']))
            
            doc.build(story)
            logger.info(f"Generated Financial Overview: {pdf_path}")
            return pdf_path
        except Exception as e:
            logger.error(f"Error generating financial overview: {e}")
            return None
    
    def list_reports(self) -> List[Path]:
        """
        List all generated PDF reports.
        
        Returns:
            List of PDF file paths
        """
        try:
            if not self.output_dir.exists():
                return []
            
            reports = sorted(
                list(self.output_dir.glob("*.pdf")),
                key=lambda x: x.stat().st_mtime,
                reverse=True
            )
            return reports
        except Exception as e:
            logger.error(f"Error listing reports: {e}")
            return []
    
    def delete_report(self, report_path: Path) -> bool:
        """
        Delete a generated report.
        
        Args:
            report_path: Path to the report
            
        Returns:
            True if deleted successfully
        """
        try:
            if Path(report_path).exists():
                Path(report_path).unlink()
                logger.info(f"Deleted report: {report_path}")
                return True
            return False
        except Exception as e:
            logger.error(f"Error deleting report: {e}")
            return False
