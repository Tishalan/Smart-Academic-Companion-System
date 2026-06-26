import os
from fpdf import FPDF
from datetime import datetime

class AcademicReport(FPDF):
    def header(self):
        # Logo
        # self.image('app/static/img/logo.png', 10, 8, 33)
        self.set_font('helvetica', 'B', 15)
        self.cell(80)
        self.cell(30, 10, 'Smart Academic Companion System', 0, 0, 'C')
        self.ln(20)

    def footer(self):
        self.set_y(-15)
        self.set_font('helvetica', 'I', 8)
        self.cell(0, 10, f'Page {self.page_no()} | Generated on {datetime.now().strftime("%Y-%m-%d %H:%M")}', 0, 0, 'C')

def generate_risk_report(students, output_path):
    pdf = AcademicReport()
    pdf.add_page()
    pdf.set_font('helvetica', 'B', 16)
    pdf.cell(0, 10, 'Student Risk Assessment Report', 0, 1, 'L')
    pdf.ln(10)
    
    pdf.set_font('helvetica', 'B', 12)
    pdf.cell(40, 10, 'Student ID', 1)
    pdf.cell(60, 10, 'Name', 1)
    pdf.cell(40, 10, 'GPA', 1)
    pdf.cell(40, 10, 'Risk Score', 1)
    pdf.ln()
    
    pdf.set_font('helvetica', '', 12)
    for student in students:
        pdf.cell(40, 10, student.student_id, 1)
        pdf.cell(60, 10, student.user.full_name, 1)
        pdf.cell(40, 10, str(round(student.GPA, 2)), 1)
        pdf.cell(40, 10, f"{round(student.risk_score * 100)}%", 1)
        pdf.ln()
    
    pdf.output(output_path)
    return output_path
