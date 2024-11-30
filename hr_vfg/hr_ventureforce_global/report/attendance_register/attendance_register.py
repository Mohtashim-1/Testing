import frappe
from frappe import _

def execute(filters=None):
    if filters is None:
        filters = {}

    # Fetch columns and data based on the provided filters
    columns, data = get_columns(filters=filters), get_datas(filters=filters)

    # Generate chart data
    chart = get_chart_data(data)

    return columns, data, None, chart

def get_chart_data(data):
    # Initialize counters for late, absent, and leave per employee
    employee_stats = {}
    for row in data:
        employee = row['employee']
        if employee not in employee_stats:
            employee_stats[employee] = {
                'Late': 0,
                'Absent': 0,
                'Leave': 0
            }

        # Iterate through each day's status
        for day in range(1, 31):
            status = row.get(f'status_{day}')
            if status == 'Late':
                employee_stats[employee]['Late'] += 1
            elif status == 'Absent':
                employee_stats[employee]['Absent'] += 1
            elif status == 'Leave':
                employee_stats[employee]['Leave'] += 1

    # Prepare data for chart
    labels = list(employee_stats.keys())  # Employee names
    late_values = [employee_stats[emp]['Late'] for emp in labels]
    absent_values = [employee_stats[emp]['Absent'] for emp in labels]
    leave_values = [employee_stats[emp]['Leave'] for emp in labels]

    # Create chart object
    chart = {
        "data": {
            "labels": labels,
            "datasets": [
                {
                    "name": "Late",
                    "values": late_values
                },
                {
                    "name": "Absent",
                    "values": absent_values
                },
                {
                    "name": "Leave",
                    "values": leave_values
                }
            ]
        },
        "type": "bar",  # or "line"
        "colors": ["#ff6384", "#36a2eb", "#cc65fe"]  # Colors for the bars
    }

    return chart


def get_columns(filters=None):
    columns = [
        {
            "label": _("Employee"),
            "fieldname": "employee",
            "fieldtype": "Link",
            "options": "Employee",
            "width": 100
        },
        {
            "label": _("Employee Name"),
            "fieldname": "employee_name",
            "fieldtype": "Data",
            "width": 100
        }
    ]

    # Add columns for each day of the month
    for day in range(1, 31):
        columns.append({
            "label": _(f"Date {day}"),
            "fieldname": f"date_{day}",
            "fieldtype": "Date",
            "width": 100
        })
        columns.append({
            "label": _(f"Check In {day}"),
            "fieldname": f"check_in_{day}",
            "fieldtype": "Data",
            "width": 100
        })
        columns.append({
            "label": _(f"Check Out {day}"),
            "fieldname": f"check_out_{day}",
            "fieldtype": "Data",
            "width": 100
        })
        columns.append({
            "label": _(f"Status {day}"),
            "fieldname": f"status_{day}",
            "fieldtype": "Data",
            "width": 100
        })

    return columns

def get_datas(filters=None):
    if filters is None:
        filters = {}

    # Prepare filter conditions for parent doctype
    conditions = {}
    if filters.get("employee"):
        conditions["employee"] = filters["employee"]
    if filters.get("month"):
        conditions["month"] = filters["month"]
    if filters.get("year"):
        conditions["year"] = filters["year"]

    # Fetch filtered attendance records
    attendance_records = frappe.get_all(
        'Employee Attendance',
        filters=conditions,
        fields=['name', 'employee', 'employee_name']
    )

    data = []

    # Process each attendance record
    for record in attendance_records:
        # Fetch the full document (including child table)
        attendance_doc = frappe.get_doc('Employee Attendance', record['name'])
        
        # Initialize check-in/out data for this employee
        check_in_out_data = {
            'employee': record['employee'],
            'employee_name': record['employee_name']
        }

        # Initialize fields for each day of the month
        for day in range(1, 31):
            check_in_out_data[f'date_{day}'] = None
            check_in_out_data[f'check_in_{day}'] = None
            check_in_out_data[f'check_out_{day}'] = None
            check_in_out_data[f'status_{day}'] = None

        # Process child table (table1) for daily attendance
        for child in attendance_doc.table1:
            day = child.date.day
            if 1 <= day <= 30:  # Ensure the day falls within the range
                check_in_out_data[f'date_{day}'] = child.date
                check_in_out_data[f'check_in_{day}'] = child.check_in_1
                check_in_out_data[f'check_out_{day}'] = child.check_out_1

                # Determine status based on child table fields
                if child.late:
                    status = "Late"
                elif child.absent:
                    status = "Absent"
                elif child.mark_leave:
                    status = "Leave"
                elif child.check_in_1 or child.check_out_1:
                    status = "Present"
                else:
                    status = "Absent"  # Default status if no check-in/out info

                check_in_out_data[f'status_{day}'] = status

        # Append processed data for this employee
        data.append(check_in_out_data)

    return data
