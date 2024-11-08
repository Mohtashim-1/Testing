import frappe
from frappe.utils import today

def execute(filters=None):
    columns = [
        {"label": "Employee", "fieldname": "employee", "fieldtype": "Data", "width": 120},
        {"label": "Date", "fieldname": "date", "fieldtype": "Date", "width": 100},
        {"label": "Designation", "fieldname": "designation", "fieldtype": "Data", "width": 120},
        {"label": "Department", "fieldname": "department", "fieldtype": "Data", "width": 120},
        {"label": "Check In", "fieldname": "check_in_1", "fieldtype": "Time", "width": 100},
        {"label": "Check Out", "fieldname": "check_out_1", "fieldtype": "Time", "width": 100}
    ]

    from_date = filters.get("from_date") if filters and filters.get("from_date") else today()
    to_date = filters.get("to_date") if filters and filters.get("to_date") else today()

    data = frappe.db.sql("""
        SELECT 
            ea.employee, 
            eat.date, 
            ea.designation, 
            ea.department, 
            eat.check_in_1, 
            eat.check_out_1
        FROM `tabEmployee Attendance` AS ea
        LEFT JOIN `tabEmployee Attendance Table` AS eat
            ON eat.parent = ea.name
        WHERE (
            (eat.check_in_1 IS NULL AND eat.check_out_1 IS NOT NULL) 
            OR (eat.check_in_1 IS NOT NULL AND eat.check_out_1 IS NULL)
        )
        AND eat.date BETWEEN %(from_date)s AND %(to_date)s
    """, {"from_date": from_date, "to_date": to_date}, as_dict=True)

    return columns, data
