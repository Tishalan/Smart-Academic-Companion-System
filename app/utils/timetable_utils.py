from datetime import datetime, time

SLOTS = [
    {"id": 1, "start": "09:00", "end": "10:30", "label": "09:00 - 10:30"},
    {"id": 2, "start": "10:30", "end": "12:00", "label": "10:30 - 12:00"},
    {"id": 3, "start": "12:00", "end": "13:30", "label": "12:00 - 13:30"},
    {"id": 4, "start": "13:30", "end": "14:00", "label": "13:30 - 14:00 (Lunch)", "is_lunch": True},
    {"id": 5, "start": "14:00", "end": "15:30", "label": "14:00 - 15:30"},
    {"id": 6, "start": "15:30", "end": "17:00", "label": "15:30 - 17:00"},
]

DAYS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]

def get_current_slot():
    now = datetime.now().time()
    for slot in SLOTS:
        start_time = datetime.strptime(slot["start"], "%H:%M").time()
        end_time = datetime.strptime(slot["end"], "%H:%M").time()
        if start_time <= now <= end_time:
            return slot
    return None

def get_next_slot():
    now = datetime.now().time()
    for slot in SLOTS:
        start_time = datetime.strptime(slot["start"], "%H:%M").time()
        if start_time > now:
            return slot
    return None

def get_day_name(date_obj=None):
    if date_obj is None:
        date_obj = datetime.now()
    return date_obj.strftime("%A")
