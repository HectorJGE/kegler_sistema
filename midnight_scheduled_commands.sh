#!/bin/sh

# Create doctor schedules
python /code/manage.py create_doctor_schedule

# Mark absent appointments as canceled
python /code/manage.py mark_absent_appointments

# Delete empty consultation entry sheets
python /code/manage.py delete_empty_consultation_entry_sheets