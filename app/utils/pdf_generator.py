import os
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle

def generate_student_report(student, output_path):
    """Generate a PDF report for a student's academic performance and risk assessment"""
    doc = SimpleDocTemplate(output_path, pagesize=letter)
    styles = getSampleStyleSheet()
    elements = []

    # Title
    elements.append(Paragraph(f"Academic Performance Report: {student.user.full_name}", styles['Title']))
    elements.append(Spacer(1, 12))

    # Student Info
    data = [
        ["Student ID:", student.student_id],
        ["Department:", student.department],
        ["Current GPA:", f"{student.GPA:.2f}"],
        ["Attendance:", f"{student.attendance_percentage}%"]
    ]
    t = Table(data, colWidths=[100, 300])
    t.setStyle(TableStyle([
        ('ALIGN', (0,0), (-1,-1), 'LEFT'),
        ('FONTNAME', (0,0), (0,-1), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0,0), (-1,-1), 10),
    ]))
    elements.append(t)
    elements.append(Spacer(1, 24))

    # AI Risk Assessment
    elements.append(Paragraph("AI-Driven Risk Assessment", styles['Heading2']))
    elements.append(Spacer(1, 12))
    
    risk_level = "High" if student.risk_score > 0.7 else ("Medium" if student.risk_score > 0.3 else "Low")
    risk_color = colors.red if student.risk_score > 0.7 else (colors.orange if student.risk_score > 0.3 else colors.green)

    risk_data = [
        ["Dropout Risk Score:", f"{student.risk_score * 100:.1f}%"],
        ["Risk Level:", risk_level],
        ["Graduation Probability:", f"{student.graduation_probability * 100:.1f}%"]
    ]
    rt = Table(risk_data, colWidths=[150, 250])
    rt.setStyle(TableStyle([
        ('TEXTCOLOR', (1,1), (1,1), risk_color),
        ('FONTNAME', (0,0), (0,-1), 'Helvetica-Bold'),
    ]))
    elements.append(rt)
    elements.append(Spacer(1, 24))

    # Recommendations
    elements.append(Paragraph("Recommendations", styles['Heading2']))
    if student.risk_score > 0.5:
        rec = "Student is flagged for immediate intervention. Suggest meeting with academic advisor and increasing study hours."
    else:
        rec = "Student is performing well. Maintain current attendance and engagement levels."
    
    elements.append(Paragraph(rec, styles['Normal']))

    # Build PDF
    doc.build(elements)
    return output_path