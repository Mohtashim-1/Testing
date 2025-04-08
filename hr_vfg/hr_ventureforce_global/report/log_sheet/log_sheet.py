# Copyright (c) 2025, VFG and contributors
# For license information, please see license.txt
import frappe

def execute(filters=None):
    columns = [
        {"fieldname": "biometric_id", "label": "Biometric ID", "fieldtype": "Data", "width": 120},
        {"fieldname": "employee_name", "label": "Employee Name", "fieldtype": "Data", "width": 200},
        {"fieldname": "attendance_date", "label": "Date", "fieldtype": "Date", "width": 120},
        {"fieldname": "check_in", "label": "Check In", "fieldtype": "Time", "width": 120},
        {"fieldname": "check_out", "label": "Check Out", "fieldtype": "Time", "width": 120},
    ]

    conditions = []
    values = {}

    # Apply filters
    if filters.get("biometric_id"):
        conditions.append("al.biometric_id = %(biometric_id)s")
        values["biometric_id"] = filters.get("biometric_id")

    if filters.get("employee_name"):
        conditions.append("e.employee_name = %(employee_name)s")
        values["employee_name"] = filters.get("employee_name")

    if filters.get("from_date"):
        conditions.append("al.attendance_date >= %(from_date)s")
        values["from_date"] = filters.get("from_date")

    if filters.get("to_date"):
        conditions.append("al.attendance_date <= %(to_date)s")
        values["to_date"] = filters.get("to_date")

    condition_query = " AND ".join(conditions)
    if condition_query:
        condition_query = "WHERE " + condition_query

    # Fetch attendance logs with correct employee_name
    attendance_logs = frappe.db.sql(f"""
        SELECT 
            al.biometric_id, 
            e.employee_name, 
            al.attendance_date,
            (SELECT MIN(attendance_time) FROM `tabAttendance Logs` 
                WHERE biometric_id = al.biometric_id 
                AND attendance_date = al.attendance_date AND type = 'Check In') AS check_in,
            (SELECT MAX(attendance_time) FROM `tabAttendance Logs` 
                WHERE biometric_id = al.biometric_id 
                AND attendance_date = al.attendance_date AND type = 'Check Out') AS check_out
        FROM `tabAttendance Logs` al
        LEFT JOIN `tabEmployee` e ON al.biometric_id = e.biometric_id
        {condition_query}
        GROUP BY al.biometric_id, e.employee_name, al.attendance_date
        ORDER BY al.attendance_date ASC
    """, values, as_dict=True)

    return columns, attendance_logs
