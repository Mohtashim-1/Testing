# Copyright (c) 2024, mohtashim and contributors
# For license information, please see license.txt

import frappe

def execute(filters=None):
    columns, data = get_columns(filters), get_data(filters)
    return columns, data

def get_columns(filters):
    return [
        "Date:Data:100",
		"Emp ID:Data:100",
		"Emp Name:Data:100",
		"Department:Link/Department:120",
        "Designation:Link/Designation:120",
        "Shift End:Data:100",
		"Shift Start:Data:100",
		"Time In:Data:100",
        "Time Out:Data:100",
        "Late Minutes:HTML:100",  # Changed to HTML to support highlighting
        "Early Out:HTML:100",  # Changed to HTML to support highlighting
        "O.T Hours:HTML:100",
        "Total Hours:HTML:100",
		"Remarks:HTML:100",

    ]


def get_data(filters):
    cond = ""
    if filters.get("depart"):
        cond = "and emp.department='{0}' ".format(filters.get("depart"))

    if filters.get("employee"):
        cond = "and emp.employee='{0}' ".format(filters.get("employee"))

    # Fetching records with the necessary fields
    records = frappe.db.sql(""" 
        SELECT 
			emptab.date,
			emp.biometric_id,
            emp.employee,
			emp.department,
			emp.designation,
            emptab.shift_in,
			emptab.shift_out,
            emptab.check_in_1,
            emptab.check_out_1,
            emptab.late_coming_hours,
            emptab.early_going_hours,
            emptab.estimated_late,
            emptab.late,
            emptab.absent
        FROM `tabEmployee Attendance` AS emp
        JOIN `tabEmployee Attendance Table` AS emptab ON emptab.parent = emp.name
        JOIN `tabEmployee` emply ON emp.employee = emply.name
        WHERE emptab.date = %s {0} AND emply.status = "Active"
        ORDER BY emptab.date, emp.department
    """.format(cond), (filters.get('to'),))

    # Assign the query result to 'data' before returning
    data = records
    return data
