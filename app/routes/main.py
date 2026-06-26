from flask import Blueprint, render_template

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    return render_template('index.html')

@main_bp.route('/attendance-kiosk')
def attendance_kiosk():
    return render_template('attendance_kiosk.html')
