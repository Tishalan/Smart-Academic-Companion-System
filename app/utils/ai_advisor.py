import random

class AIAdvisor:
    """
    Internal ML-Driven AI Advisor that provides recommendations
    based on student performance and batch trends.
    """
    
    @staticmethod
    def get_student_recommendation(student):
        """
        Generates a personal recommendation for a student based on:
        - risk_score
        - graduation_probability
        - GPA
        - attendance
        """
        prob = student.graduation_probability or 0
        risk = student.risk_score or 0
        gpa = student.GPA or 0
        attendance = student.attendance_percentage or 0
        
        recommendations = []
        
        # Risk and Graduation Probability logic
        if prob < 0.5:
            recommendations.append("Priority: Your graduation is at high risk due to current academic trends.")
        elif prob < 0.75:
            recommendations.append("Focus: You are on track, but there is room for consistency in your performance.")
        else:
            recommendations.append("Excellent: You are highly likely to graduate on time!")

        # Performance-based logic
        if gpa < 2.0:
            recommendations.append("Academic Action: Your current GPA is below target. Suggested remedial sessions for core modules.")
        
        if attendance < 80:
            recommendations.append("Attendance Warning: Low attendance detected. Consistent participation is highly correlated with success.")
        
        # Specific study tips
        tips = [
            "Participate more in the LMS forums to clarify doubts with lecturers.",
            "Use the campus library resources for better assignment research.",
            "Focus on the 'Computing Project' or 'Final Project' as it has high credit weight.",
            "Collaborate with your batch mates on peer-to-peer programming."
        ]
        recommendations.append(f"Tip: {random.choice(tips)}")
        
        return recommendations

    @staticmethod
    def get_batch_insights(batch):
        """
        Generates high-level insights for a batch based on aggregated data.
        """
        students = batch.students.all()
        if not students:
            return "No data available for this batch."
            
        avg_prob = sum(s.graduation_probability for s in students) / len(students)
        avg_gpa = sum(s.GPA for s in students) / len(students)
        
        status = "On Track" if avg_prob > 0.7 else ("Slightly Delayed" if avg_prob > 0.5 else "High Risk")
        
        insight = f"Batch Status: {status} (Avg. Success Probability: {avg_prob*100:.1f}%).\n"
        
        if status == "High Risk":
            insight += "Recommendation: Immediate intervention required. Review lecturer feedback frequency and student engagement logs."
        elif status == "Slightly Delayed":
            insight += "Recommendation: Schedule a batch-wide feedback session to identify bottlenecks in recent modules."
        else:
            insight += "Recommendation: Maintain current teaching pace. Batch performance is excellent."
            
        return insight

    @staticmethod
    def get_lecturer_efficiency_report(lecturer):
        """
        Analyzes lecturer effectiveness based on the success of students in their modules.
        """
        # This can compare the success rates of students in their modules vs other lecturers
        # For now, it provides a simulated analysis based on existing stats
        stats = lecturer.get_workload_stats()
        pending = stats.get('pending_gradings', 0)
        
        if pending > 50:
            return "Efficiency Warning: High backlog of pending gradings. This delay may impact student graduation planning."
        return "Lecturer is performing well with current workload."
