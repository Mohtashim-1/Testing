# Copyright (c) 2025, VFG and contributors
# For license information, please see license.txt

import frappe
from frappe import _

def execute(filters=None):
    filters = filters or {}
    columns = get_columns()
    data = get_data(filters)
    return columns, data

def get_columns():
    return [
        {"fieldname": "employee_id", "label": _("Employee ID"), "fieldtype": "Data", "width": 120},
        {"fieldname": "employee_name", "label": _("Employee Name"), "fieldtype": "Data", "width": 150},
        {"fieldname": "date_of_joining", "label": _("Date of Joining"), "fieldtype": "Date", "width": 120},
        {"fieldname": "joining_month", "label": _("Joining Month"), "fieldtype": "Data", "width": 100},
        {"fieldname": "joining_year", "label": _("Joining Year"), "fieldtype": "Data", "width": 100},
        {"fieldname": "attendance_month", "label": _("Attendance Month"), "fieldtype": "Data", "width": 120},
        {"fieldname": "attendance_year", "label": _("Attendance Year"), "fieldtype": "Data", "width": 120},
        {"fieldname": "attendance_date", "label": _("Attendance Date"), "fieldtype": "Date", "width": 120},
    ]

def get_data(filters):
    month = filters.get("month")
    year = filters.get("year")

    query = """
        SELECT 
            e.name AS employee_id, 
            e.employee_name, 
            e.date_of_joining,
            MONTH(e.date_of_joining) AS joining_month,
            YEAR(e.date_of_joining) AS joining_year,
            ea.month AS attendance_month,
            ea.year AS attendance_year,
            eat.date AS attendance_date
        FROM `tabEmployee` e
        LEFT JOIN `tabEmployee Attendance` ea
            ON ea.employee = e.name
        LEFT JOIN `tabEmployee Attendance Table` eat
            ON eat.parent = ea.name
        WHERE 
            MONTH(e.date_of_joining) = %(month)s
            AND YEAR(e.date_of_joining) = %(year)s
            AND (eat.date IS NULL OR MONTH(eat.date) != MONTH(e.date_of_joining))
    """
    return frappe.db.sql(query, {"month": month, "year": year}, as_dict=True)
