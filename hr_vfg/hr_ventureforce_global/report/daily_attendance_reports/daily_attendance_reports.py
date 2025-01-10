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
        "Late:HTML:100",  # Changed to HTML to support highlighting
        "Early Out:HTML:100",  # Changed to HTML to support highlighting
        "OT Hours:HTML:100",
        "Total Hours:HTML:100",
        "Remarks:HTML:100",
    ]

def get_data(filters):
    cond = ""
    if filters.get("depart"):
        cond = "and emp.department='{0}' ".format(filters.get("depart"))

    if filters.get("employee"):
        cond += "and emp.employee='{0}' ".format(filters.get("employee"))

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
            emptab.total_time
        FROM `tabEmployee Attendance` AS emp
        JOIN `tabEmployee Attendance Table` AS emptab ON emptab.parent = emp.name
        JOIN `tabEmployee` emply ON emp.employee = emply.name
        WHERE emptab.date = %s {0} AND emply.status = "Active"
        ORDER BY emptab.date, emp.department
    """.format(cond), (filters.get('to'),))

    # Add remarks dynamically based on conditions
    data = []
    for record in records:
        remarks = generate_remarks(record)
        data.append(record + (remarks,))
    return data


def generate_remarks(record):
    """
    Generate remarks dynamically based on the record fields.
    """
    late_minutes = record[9]  # Late Minutes
    early_out = record[10]  # Early Out
    total_hours = record[12]  # Total Hours

    remarks = []
    # if late_minutes and int(late_minutes.split(":")[0]) > 1:  # Assuming 'Late Minutes' is in 'hh:mm:ss' format
    #     remarks.append("Late arrival")

    # if early_out and int(early_out.split(":")[0]) > 1:  # Assuming 'Early Out' is in 'hh:mm:ss' format
    #     remarks.append("Early leave")

    if total_hours and int(total_hours.split(":")[0]) > 8:
        remarks.append("Overtime")

    return ", ".join(remarks) if remarks else "No issues"