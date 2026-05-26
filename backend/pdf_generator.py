"""
PDF Report Generation Service
Generates professional PDF reports from lab results
"""
import logging
from datetime import datetime
from typing import List, Dict, Optional
from io import BytesIO
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak
from reportlab.platypus import Image as RLImage
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY
from parser_service import ParsedLabResult

logger = logging.getLogger(__name__)

class PDFReportGenerator:
    """Generate PDF reports from lab results"""
    
    def __init__(self):
        self.styles = getSampleStyleSheet()
        self._setup_custom_styles()
    
    def _setup_custom_styles(self):
        """Setup custom paragraph styles"""
        # Only add styles if they don't already exist
        if 'CustomTitle' not in self.styles:
            self.styles.add(ParagraphStyle(
                name='CustomTitle',
                parent=self.styles['Heading1'],
                fontSize=24,
                textColor=colors.HexColor('#1a237e'),
                spaceAfter=30,
                alignment=TA_CENTER
            ))
        
        if 'SectionHeader' not in self.styles:
            self.styles.add(ParagraphStyle(
                name='SectionHeader',
                parent=self.styles['Heading2'],
                fontSize=16,
                textColor=colors.HexColor('#283593'),
                spaceAfter=12,
                spaceBefore=12
            ))
        
        if 'CustomBodyText' not in self.styles:
            self.styles.add(ParagraphStyle(
                name='CustomBodyText',
                parent=self.styles['BodyText'],
                fontSize=11,
                leading=14,
                alignment=TA_JUSTIFY
            ))
        
        if 'Disclaimer' not in self.styles:
            self.styles.add(ParagraphStyle(
                name='Disclaimer',
                parent=self.styles['BodyText'],
                fontSize=9,
                textColor=colors.HexColor('#666666'),
                leading=11,
                leftIndent=20,
                rightIndent=20,
                borderColor=colors.HexColor('#ff9800'),
                borderWidth=1,
                borderPadding=10
            ))
    
    def generate_report(
        self,
        results: List[ParsedLabResult],
        explanation: Dict[str, str],
        report_id: str,
        report_type: str,
        patient_name: Optional[str] = None,
        report_date: Optional[datetime] = None
    ) -> BytesIO:
        """
        Generate a PDF report
        
        Args:
            results: List of lab results
            explanation: Dict with summary, tips, disclaimer
            report_id: Report UUID
            report_type: Type of report
            patient_name: Optional patient name
            report_date: Report date
            
        Returns:
            BytesIO buffer containing PDF
        """
        buffer = BytesIO()
        
        # Create PDF document
        doc = SimpleDocTemplate(
            buffer,
            pagesize=letter,
            rightMargin=72,
            leftMargin=72,
            topMargin=72,
            bottomMargin=72
        )
        
        # Build content
        story = []
        
        # Header
        story.append(Paragraph("Medical Lab Report", self.styles['CustomTitle']))
        story.append(Spacer(1, 0.2*inch))
        
        # Report info
        report_date_str = report_date.strftime("%B %d, %Y") if report_date else datetime.now().strftime("%B %d, %Y")
        info_data = [
            ["Report ID:", report_id[:13] + "..."],
            ["Report Type:", report_type or "General"],
            ["Date:", report_date_str],
        ]
        if patient_name:
            info_data.insert(0, ["Patient:", patient_name])
        
        info_table = Table(info_data, colWidths=[2*inch, 3.5*inch])
        info_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 11),
            ('TEXTCOLOR', (0, 0), (0, -1), colors.HexColor('#1a237e')),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ]))
        story.append(info_table)
        story.append(Spacer(1, 0.3*inch))
        
        # Lab Results Table
        story.append(Paragraph("Lab Results", self.styles['SectionHeader']))
        story.append(Spacer(1, 0.1*inch))
        
        # Table header
        table_data = [
            ["Test Name", "Value", "Unit", "Reference Range", "Status"]
        ]
        
        # Add results
        for result in results:
            value = str(result.value_numeric if result.value_numeric else result.value_text)
            ref_range = result.ref_text if result.ref_text else \
                       f"{result.ref_low}-{result.ref_high}" if result.ref_low and result.ref_high else "N/A"
            
            status = result.status.upper()
            status_color = colors.green if status == "NORMAL" else \
                          colors.red if status in ["HIGH", "LOW"] else colors.gray
            
            table_data.append([
                result.canonical_name,
                value,
                result.unit or "",
                ref_range,
                status
            ])
        
        results_table = Table(table_data, colWidths=[2*inch, 1*inch, 0.7*inch, 1.5*inch, 0.8*inch])
        results_table.setStyle(TableStyle([
            # Header style
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1a237e')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 11),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            
            # Data style
            ('BACKGROUND', (0, 1), (-1, -1), colors.white),
            ('GRID', (0, 0), (-1, -1), 1, colors.grey),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 10),
            ('ALIGN', (1, 1), (-1, -1), 'CENTER'),
            ('ALIGN', (0, 1), (0, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('TOPPADDING', (0, 1), (-1, -1), 6),
            ('BOTTOMPADDING', (0, 1), (-1, -1), 6),
            
            # Alternating row colors
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f5f5f5')]),
        ]))
        
        # Color code status column
        for i in range(1, len(table_data)):
            status = table_data[i][4]
            if status == "HIGH" or status == "LOW":
                results_table.setStyle(TableStyle([
                    ('TEXTCOLOR', (4, i), (4, i), colors.red),
                    ('FONTNAME', (4, i), (4, i), 'Helvetica-Bold'),
                ]))
            elif status == "NORMAL":
                results_table.setStyle(TableStyle([
                    ('TEXTCOLOR', (4, i), (4, i), colors.green),
                ]))
        
        story.append(results_table)
        story.append(Spacer(1, 0.3*inch))
        
        # Summary
        if explanation.get('summary'):
            story.append(Paragraph("Summary & Explanation", self.styles['SectionHeader']))
            story.append(Spacer(1, 0.1*inch))
            
            # Clean and format summary text
            summary_text = explanation['summary'].replace('\n', '<br/>')
            story.append(Paragraph(summary_text, self.styles['CustomBodyText']))
            story.append(Spacer(1, 0.2*inch))
        
        # Health Tips
        if explanation.get('tips'):
            story.append(Paragraph("Health & Wellness Tips", self.styles['SectionHeader']))
            story.append(Spacer(1, 0.1*inch))
            
            tips_text = explanation['tips'].replace('\n', '<br/>')
            story.append(Paragraph(tips_text, self.styles['CustomBodyText']))
            story.append(Spacer(1, 0.3*inch))
        
        # Disclaimer (only if not empty)
        disclaimer_text = explanation.get('disclaimer', '').strip()
        if disclaimer_text:
            story.append(Spacer(1, 0.2*inch))
            story.append(Paragraph("MEDICAL DISCLAIMER", self.styles['SectionHeader']))
            disclaimer_text = disclaimer_text.replace('\n', '<br/>')
            story.append(Paragraph(disclaimer_text, self.styles['Disclaimer']))
        
        # Build PDF
        doc.build(story)
        
        # Return buffer
        buffer.seek(0)
        return buffer
    
    def generate_simple_report(
        self,
        results: List[ParsedLabResult],
        report_id: str
    ) -> BytesIO:
        """Generate a simple PDF report without detailed explanation"""
        explanation = {
            'summary': 'Lab results extracted and analyzed.',
            'tips': 'Consult your healthcare provider for detailed interpretation.',
            'disclaimer': '⚠️ This is an automated report. Always consult your doctor for medical advice.'
        }
        
        return self.generate_report(
            results=results,
            explanation=explanation,
            report_id=report_id,
            report_type="General"
        )


# Singleton instance
_pdf_generator = None

def get_pdf_generator() -> PDFReportGenerator:
    """Get or create PDF generator singleton"""
    global _pdf_generator
    if _pdf_generator is None:
        _pdf_generator = PDFReportGenerator()
    return _pdf_generator
