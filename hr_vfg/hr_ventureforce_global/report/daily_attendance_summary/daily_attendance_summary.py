# Copyright (c) 2013, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.utils import flt, getdate, add_months, get_last_day, fmt_money, nowdate,cstr, cint

from frappe import msgprint, _
from calendar import monthrange

day_abbr = [
		"Mon",
		"Tue",
		"Wed",
		"Thu",
		"Fri",
		"Sat",
		"Sun"
	]
month_list = ['January','February','March','April','May','June','July','August','September',
		'October','November','December']


def execute(filters=None):
	columns, data = [], []
	columns = get_columns(filters)
	data  = get_data(filters)
	return columns, data


def get_columns(filters):
    columns =  [
        {
            "fieldtype":"Link",
            "fieldname":"department",
            "options":"Department",
            "label":"Department",
            "width":200,
        },
        # {
        #     "fieldtype":"Data",
        #     "fieldname":"sub_department",
        #     "label":"Sub Department",
        #     "width":200,
        # },
        {
            "fieldtype":"Int",
            "fieldname":"total_employee",
            "label":"Total Employee",
            "width":200,
        },
        {
            "fieldtype":"Int",
            "fieldname":"on_time",
            "label":"On Time",
            "width":200,
        },
        {
            "fieldtype":"Int",
            "fieldname":"late_present",
            "label":"Late Present",
            "width":200,
        },
        {
            "fieldtype":"Int",
            "fieldname":"total_present",
            "label":"Total Present",
            "width":200,
        },
        {
            "fieldtype":"Int",
            "fieldname":"total_absent",
            "label":"Total Absent",
            "width":200,
        },
    ]

    return columns

def get_data(filters):
    data = []
    rec = frappe.db.sql("""
               SELECT p.department, c.late, c.early, c.weekly_off AS sunday, c.public_holiday AS holiday, c.absent, c.half_day
               FROM `tabEmployee Attendance` p
               LEFT JOIN 
               `tabEmployee` AS emp
               ON emp.name=p.employee
               LEFT JOIN
               `tabEmployee Attendance Table` c
               ON c.parent = p.name
               WHERE c.date = %s 
     """, (filters.to_date), as_dict=1)

    for r in rec:
        exists = False
        for d in data:
            if r.get("department") == d.get("department"):
                d["total_employee"] += 1
                if r.get("absent"):
                    d["total_absent"] += 1
                elif r.get("sunday") or r.get("holiday"):
                    pass
                elif r.get("late"):
                    d["late_present"] += 1
                    d["total_present"] += 1
                else:
                    d["on_time"] += 1
                    d["total_present"] += 1
                exists = True
                break
        if not exists:
            data.append({
                "department": r.get("department"),
                "total_employee": 1,
                "total_absent": 1 if r.get("absent") else 0,
                "late_present": 1 if r.get("late") else 0,
                "on_time": 1 if not (r.get("sunday") or r.get("holiday") or r.get("late")) else 0,
                "total_present": 1 if not (r.get("absent") or r.get("sunday") or r.get("holiday")) else 0
            })

    return data
