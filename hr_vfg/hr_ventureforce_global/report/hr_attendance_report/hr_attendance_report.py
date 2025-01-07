# Copyright (c) 2013, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from frappe.model.naming import make_autoname
from frappe import msgprint, _
from datetime import datetime
from datetime import timedelta
from datetime import date as dt
import datetime as special
import time
# from erpnext.hr.utils import get_holidays_for_employee
from frappe.utils import date_diff, add_months, today, getdate, add_days, flt, get_last_day
import calendar

def execute(filters=None):
    columns, data = [], []
    return get_columns(), get_data(filters)

# Modify the work_hours calculation logic
def get_data(filters):
    emp = ""
    if filters.employee:
        emp = "employee='" + filters.employee + "' and "
    
    query = """ select name from `tabEmployee Attendance` where {0} month=%s""".format(emp)
    result = frappe.db.sql(query, (filters.month))

    data = []
    if result:
        for res in result:
            try:
                doc = frappe.get_doc("Employee Attendance", res[0])
                for item in doc.table1:
                    if frappe.utils.getdate(filters.from_date) <= frappe.utils.getdate(item.date) and frappe.utils.getdate(filters.to_date) >= frappe.utils.getdate(item.date):
                        pass
                    else:
                        continue
                    
                    shift_req = frappe.get_all("Shift Request", filters={'employee': doc.employee,
                                                                         'from_date': ["<=", item.date], 'to_date': [">=", item.date]}, fields=["*"])
                    shift = None
                    if len(shift_req) > 0:
                        shift = shift_req[0].shift_type
                    
                    if shift:
                        shift_doc = frappe.get_doc("Shift Type", shift)
                    else:
                        shift_doc = None

                    day_name = datetime.strptime(str(item.date), '%Y-%m-%d').strftime('%A')
                    day_data = None

                    if shift_doc:
                        for day in shift_doc.days:
                            if day_name == day.day:
                                day_data = day
                                break
                    
                    if not day_data:
                        if item.check_in_1 and item.check_out_1:
                            schedule_time_in = "00:00:00"
                            schedule_time_out = "00:00:00"
                        else:
                            continue
                    else:
                        schedule_time_in = day_data.start_time
                        schedule_time_out = day_data.end_time
                    
                    # Check attendance status
                    att_status = "In Time"
                    if item.late:
                        att_status = "Late Entry"
                    elif item.absent:
                        att_status = "Absent"
                    elif item.half_day:
                        att_status = "Half Day"
                    if item.sunday or item.holiday:
                        att_status = "Off"
                    if att_status == "Absent":
                        leaves = frappe.get_all("Leave Application", filters={'employee': doc.employee,
                                                                             'from_date': ["<=", item.date], 'to_date': [">=", item.date], "status": "Approved"}, fields=["*"])
                        if len(leaves) > 0:
                            att_status = leaves[0].leave_type
                    
                    # Work hours handling (convert timedelta to formatted string)
                    if isinstance(item.per_day_hour, timedelta):
                        # Convert timedelta to total seconds
                        total_seconds = int(item.per_day_hour.total_seconds())
                        hours = total_seconds // 3600
                        minutes = (total_seconds % 3600) // 60
                        seconds = total_seconds % 60
                        work_hours = f"{hours:02}:{minutes:02}:{seconds:02}"
                    else:
                        work_hours = "00:00:00"  # Default to 00:00:00 if not timedelta
                    
                    # Handling for late_coming_hours and early_going_hours
                    def convert_to_time_string(time_val):
                        if isinstance(time_val, timedelta):
                            total_seconds = int(time_val.total_seconds())
                            hours = total_seconds // 3600
                            minutes = (total_seconds % 3600) // 60
                            seconds = total_seconds % 60
                            return f"{hours:02}:{minutes:02}:{seconds:02}"
                        elif isinstance(time_val, str):
                            # If it's already a string (e.g., 'HH:MM:SS'), return it directly
                            return time_val
                        return "00:00:00"  # Default if the value is neither timedelta nor string
                    
                    late_coming_hours = convert_to_time_string(item.late_coming_hours)
                    early_going_hours = convert_to_time_string(item.early_going_hours)

                    row = {
                        "emp_id": doc.employee,
                        "biometric_id": doc.biometric_id,
                        "name": doc.employee_name,
                        "department": doc.department,
                        "date": getdate(item.date),
                        "day": day_name[:3],
                        "schedule_time_in": item.shift_in,
                        "actual_in_time": item.check_in_1,
                        "schedule_time_out": item.shift_out,
                        "actual_out_time": item.check_out_1,
                        "late_arrival": late_coming_hours if item.late else "00:00:00",
                        "early_going": early_going_hours if item.early else "00:00:00",
                        "work_hours": work_hours,  # Display work_hours in hh:mm:ss format
                        "total_hours": item.difference,
                        "overtime": item.estimated_late,
                        "day_status": "Holiday" if item.sunday or item.holiday else "Working Day",
                        "att_status": att_status
                    }
                    data.append(row)

            except Exception as e:
                frappe.msgprint(f"Error processing attendance for {doc.employee}: {str(e)}")

        return data
    else:
        frappe.msgprint("No results found for the given filters.")
        return []



def get_columns():
    columns = [
        {
            "label": _("EMP #"),
            "fieldname": "emp_id",
            "fieldtype": "Link",
            "options": "Employee",
            "width": 120
        },
        {
            "label": _("Biometric ID"),
            "fieldname": "biometric_id",
            "fieldtype": "Data",
            "width": 120
        },
        {
            "label": _("Name"),
            "fieldname": "name",
            "fieldtype": "Data",
            "width": 220
        },
        {
            "label": _("Department"),
            "fieldname": "department",
            "fieldtype": "Data",
            "width": 200
        },
        {
            "label": _("Date"),
            "fieldname": "date",
            "fieldtype": "Date",
            "width": 120
        },
        {
            "label": _("Day"),
            "fieldname": "day",
            "fieldtype": "Data",
            "width": 120
        },
        {
            "label": _("Sch In Time"),
            "fieldname": "schedule_time_in",
            "fieldtype": "Data",
            "width": 120
        },
        {
            "label": _("Act In Time"),
            "fieldname": "actual_in_time",
            "fieldtype": "Data",
            "width": 120
        },
        {
            "label": _("Sch Out Time"),
            "fieldname": "schedule_time_out",
            "fieldtype": "Data",
            "width": 120
        },
        {
            "label": _("Act Out Time"),
            "fieldname": "actual_out_time",
            "fieldtype": "Data",
            "width": 120
        },
        {
            "label": _("Late Arrival"),
            "fieldname": "late_arrival",
            "fieldtype": "Data",
            "width": 120
        },
        {
            "label": _("Day Status"),
            "fieldname": "day_status",
            "fieldtype": "Data",
            "width": 120
        },
        {
            "label": _("Att Status"),
            "fieldname": "att_status",
            "fieldtype": "Data",
            "width": 120
        },
        {
            "label": _("Work Hours"),
            "fieldname": "work_hours",
            "fieldtype": "Data",
            "width": 120
        },
        {
            "label": _("Total Hours"),
            "fieldname": "total_hours",
            "fieldtype": "Data",
            "width": 120
        },
        {
            "label": _("Overtime"),
            "fieldname": "overtime",
            "fieldtype": "Data",
            "width": 120
        },
        {
            "label": _("Leave Early"),
            "fieldname": "early_going",
            "fieldtype": "Data",
            "width": 120
        },
    ]
    return columns
