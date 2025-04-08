# Copyright (c) 2025, VFG and contributors
# For license information, please see license.txt

import frappe

def execute(filters=None):
    columns = [
        {"label": "Employee", "fieldname": "employee", "fieldtype": "Data", "width": 250},
        {"label": "Designation", "fieldname": "designation", "fieldtype": "Data", "width": 100},
        {"label": "Department", "fieldname": "department", "fieldtype": "Data", "width": 100},
        {"label": "Month", "fieldname": "month", "fieldtype": "Data", "width": 100},
        {"label": "Year", "fieldname": "year", "fieldtype": "Data", "width": 100},
        {"label": "Absent", "fieldname": "total_absents", "fieldtype": "Data", "width": 100},
    ]

    conditions = "WHERE ea.total_absents != 0 AND ea.employee != 'MOHTASHIM MUHAMMAD SHOAIB'"

    if filters:
        if filters.get("employee"):
            conditions += f" AND ea.employee = {frappe.db.escape(filters['employee'])}"
        if filters.get("year"):
            conditions += f" AND ea.year = {frappe.db.escape(filters['year'])}"
        if filters.get("month"):
            conditions += f" AND ea.month = {frappe.db.escape(filters['month'])}"
        if filters.get("department"):
            conditions += f" AND ea.department = {frappe.db.escape(filters['department'])}"
        if filters.get("designation"):
            conditions += f" AND ea.designation = {frappe.db.escape(filters['designation'])}"

    query = f"""
        SELECT 
            ea.employee,
            ea.designation,
            ea.department,
            ea.month,
            ea.year,
            ea.total_absents
        FROM `tabEmployee Attendance` AS ea
        {conditions}
        ORDER BY 
            ea.year,
            FIELD(ea.month, 'January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December')
    """

    data = frappe.db.sql(query, as_dict=True)
    return columns, data
