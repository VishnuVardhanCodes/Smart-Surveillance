import os
import pandas as pd
import matplotlib.pyplot as plt
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Image, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from datetime import datetime, timedelta
import schedule
import time
import threading

class ReportGenerator:
    def __init__(self, db_manager, report_dir=None):
        self.db = db_manager
        if report_dir is None:
            # Default to 'reports/daily_reports' relative to this file (backend/)
            base_dir = os.path.dirname(os.path.abspath(__file__))
            self.report_dir = os.path.join(base_dir, 'reports', 'daily_reports')
        else:
            self.report_dir = report_dir
            
        if not os.path.exists(self.report_dir):
            os.makedirs(self.report_dir)

    def generate_daily_report(self, date_str=None):
        """Generate a PDF report for a specific date."""
        if date_str is None:
            date_str = (datetime.now() - timedelta(days=0)).strftime("%Y-%m-%d")
        
        stats = self.db.get_stats_for_report(date_str)
        filename = f"daily_report_{date_str}.pdf"
        filepath = os.path.join(self.report_dir, filename)
        
        # 1. Create Charts
        self._create_charts(stats, date_str)
        
        # 2. Create PDF
        doc = SimpleDocTemplate(filepath, pagesize=letter)
        styles = getSampleStyleSheet()
        elements = []
        
        # Title
        title_style = ParagraphStyle(
            'TitleStyle',
            parent=styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor("#2563EB"),
            alignment=1,
            spaceAfter=20
        )
        elements.append(Paragraph(f"ITC PSPD BCM: SmartEye AI Sentinel - Daily Report", title_style))
        elements.append(Paragraph(f"Date: {date_str}", styles['Normal']))
        elements.append(Spacer(1, 12))
        
        # Summary Table
        data = [
            ['Metric', 'Count'],
            ['Total Entries', stats['entries']],
            ['Total Exits', stats['exits']],
            ['Vehicles Detected', stats['vehicles']],
            ['Unique Number Plates', stats['unique_plates']],
            ['Night Alerts Triggered', stats['night_alerts']]
        ]
        
        t = Table(data, colWidths=[200, 100])
        t.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#2563EB")),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        elements.append(t)
        elements.append(Spacer(1, 24))
        
        # Add Charts
        chart_path = os.path.join(self.report_dir, f"chart_{date_str}.png")
        if os.path.exists(chart_path):
            img = Image(chart_path, width=400, height=250)
            elements.append(img)
            
        doc.build(elements)
        return filepath

    def _create_charts(self, stats, date_str):
        """Create visualization charts for the report."""
        plt.figure(figsize=(10, 6))
        
        # Hourly Activity Bar Chart
        hours = sorted(stats['hourly_data'].keys())
        counts = [stats['hourly_data'][h] for h in hours]
        
        plt.bar(hours, counts, color='#2563EB')
        plt.title(f'Hourly Activity - {date_str}')
        plt.xlabel('Hour of Day')
        plt.ylabel('Number of Detections')
        plt.grid(axis='y', linestyle='--', alpha=0.7)
        
        chart_path = os.path.join(self.report_dir, f"chart_{date_str}.png")
        plt.savefig(chart_path)
        plt.close()

    def run_scheduler(self):
        """Run the automated report generation at 23:59 daily."""
        schedule.every().day.at("23:59").do(self.generate_daily_report)
        
        def run_loop():
            while True:
                schedule.run_pending()
                time.sleep(60)
        
        thread = threading.Thread(target=run_loop, daemon=True)
        thread.start()
        print("Report Scheduler Started - Running daily at 23:59")
