import frappe
from frappe.utils import add_months, getdate, get_first_day, get_last_day, flt

def execute(filters=None):
    columns = get_columns(filters)
    data = get_data(filters)
    return columns, data

def get_columns(filters):
    columns = [
        {
            "fieldname": "employee",
            "label": "Emp ID",
            "fieldtype": "Data",
            "width": 150,
        },
        {
            "fieldname": "employee_name",
            "label": "Emp Name",
            "fieldtype": "Data",
            "width": 150,
        },
        {
            "fieldname": "department",
            "label": "Department",
            "fieldtype": "Data",
            "width": 150,
        },
        {
            "fieldname": "designation",
            "label": "Designation",
            "fieldtype": "Data",
            "width": 150,
        }
    ]
    # Add month-wise qty and price columns dynamically
    start_date = getdate(filters.get("from_date"))
    end_date = getdate(filters.get("to_date"))
    cur_date = start_date
    while cur_date <= end_date:
        month_str = cur_date.strftime('%b %Y')  # Format month as 'Jan 2024'
        columns.append({
            "fieldname": f"total_absents_{month_str}",
            "label": f"Absents ({month_str})",
            "fieldtype": "Int",
            "width": 180,
        })
        columns.append({
            "fieldname": f"present_days_{month_str}",
            "label": f"Present Days ({month_str})",
            "fieldtype": "Int",
            "width": 180,
        })
        columns.append({
            "fieldname": f"total_lates_{month_str}",
            "label": f"Total Lates ({month_str})",
            "fieldtype": "Int",
            "width": 180,
        })
        cur_date = add_months(cur_date, 1)
    return columns

def get_data(filters):
    data = []
    condition = """
        eat.date between %(from_date)s and %(to_date)s
    """
    if filters.get("department"):
        condition += " and ea.department = %(department)s"

    query = frappe.db.sql("""
        SELECT ea.employee, eat.date, ea.employee_name, ea.department, ea.designation, ea.total_absents, ea.present_days,ea.total_lates
        FROM `tabEmployee Attendance` AS ea
        LEFT JOIN `tabEmployee Attendance Table` AS eat ON ea.name = eat.parent
        WHERE {condition}
        Group by ea.employee
    """.format(condition=condition), filters, as_dict=1)

    for record in query:
        row = {"employee": record.get("employee"), "employee_name": record.get("employee_name"), "department": record.get("department"), "designation": record.get("designation")}  # Initialize row without total quantity

        # Calculate monthly total_absents_ and present_days_ by iterating through transactions
        for month in get_month_ranges(filters["from_date"], filters["to_date"]):
            if record.get("date") and record.get("date") >= month[0] and record.get("date") <= month[1]:
                month_str = month[1].strftime('%b %Y')
                row[f"total_absents_{month_str}"] = record.get("total_absents") or 0
                row[f"present_days_{month_str}"] = flt(record.get("present_days") or 0)
                row[f"total_lates_{month_str}"] = flt(record.get("total_lates") or 0)
                break  # Only count the first occurrence per month

        data.append(row)
    return data

def get_month_ranges(start_date, end_date):
    cur_date = start_date
    ranges = []
    while cur_date <= end_date:
        ranges.append((get_first_day(cur_date), get_last_day(cur_date)))
        cur_date = add_months(cur_date, 1)
    return ranges
