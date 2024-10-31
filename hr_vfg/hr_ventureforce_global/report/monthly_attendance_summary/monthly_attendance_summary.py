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

from frappe.utils import date_diff, add_months, today, getdate, add_days, flt, get_last_day
import calendar

def execute(filters=None):
	columns, data = [], []
	return get_columns(), get_data(filters)

def get_data(filters):
		emp = ""
		if filters.employee:
			emp = "employee='"+filters.employee + "' and "
		result = frappe.db.sql(""" select name from `tabEmployee Attendance` where {0} month=%s and year=%s""".format(emp),
							(filters.month,filters.year))
		data =[]
		if result:
			for res in result:
				#try:
					doc = frappe.get_doc("Employee Attendance", res[0])
					
					shift_ass = frappe.get_all("Shift Assignment", filters={'employee': doc.employee,
                                                                            'start_date': ["<=", getdate(doc.table1[0].date)]}, fields=["*"])
					shift_hours = "08:00:00"
					if len(shift_ass) > 0:
						shift = shift_ass[0].shift_type
						shift_doc = frappe.get_doc("Shift Type", shift)
						shift_hours = shift_doc.end_time - shift_doc.start_time
					

					start_date = getdate(doc.table1[0].date)
					end_date = getdate(doc.table1[-1].date)
					annual_l =  len(frappe.db.get_all("Attendance", 
						{"attendance_date":["between",[start_date,end_date]],"status":"On Leave","docstatus":1,
							"employee":doc.employee,"leave_type":"Annual Leave"})) + (len(frappe.db.get_all("Attendance", 
						{"attendance_date":["between",[start_date,end_date]],"status":"Half Day","docstatus":1,
							"employee":doc.employee,"leave_type":"Annual Leave"}))/2)
					medical_l = len(frappe.db.get_all("Attendance", 
								{"attendance_date":["between",[start_date,end_date]],"status":"On Leave","docstatus":1,
									"employee":doc.employee,"leave_type":"Sick Leave"})) + (len(frappe.db.get_all("Attendance", 
								{"attendance_date":["between",[start_date,end_date]],"status":"Half Day","docstatus":1,
									"employee":doc.employee,"leave_type":"Sick Leave"}))/2)
					
					casual_l = len(frappe.db.get_all("Attendance", 
								{"attendance_date":["between",[start_date,end_date]],"status":"On Leave","docstatus":1,
									"employee":doc.employee,"leave_type":"Casual Leave"})) + (len(frappe.db.get_all("Attendance", 
								{"attendance_date":["between",[start_date,end_date]],"status":"Half Day","docstatus":1,
									"employee":doc.employee,"leave_type":"Casual Leave"}))/2)
					
					deduction_days  =(float(doc.total_absents or 0) + float(doc.total_half_days or 0) \
					                  + float(doc.lates_for_absent or 0)) - (annual_l + casual_l + medical_l)
					row={
							"emp_id":doc.employee,
							"biometric_id":doc.biometric_id,
							"name":doc.employee_name,
							"department":doc.department,
							"date_of_joining":frappe.db.get_value("Employee",{"name":doc.employee},"date_of_joining"),
							"present_days":doc.present_days,
							"half_days":doc.total_half_days,
							"work_hours":doc.hours_worked,
							"total_days":doc.total_working_days,
							"shift_hours":shift_hours,
							"total_hours":doc.total_working_hours,
							"absents":doc.total_absents,
							"annual_l":annual_l,
							"casual_l":casual_l,
							"medical_l":medical_l,
							"month_days":doc.month_days,
							"payable_days":float(doc.month_days) - deduction_days,
							"late_counts":doc.lates_for_absent,
							"deduction_days":deduction_days,


						}
					data.append(row)
				# except:
				# 		pass

			#frappe.msgprint(str(data))
			return data

		else:
			return []

def get_columns():
	columns=[
		{
			"label": _("EMP #"),
			"fieldname": "emp_id",
			"fieldtype": "Link",
			"options": "Employee",
			"width": 120
		},
		{
			"label": _("ID No."),
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
			"label": _("department"),
			"fieldname": "department",
			"fieldtype": "Data",
			"width": 200
		},
		{
			"label": _("D.O.J"),
			"fieldname": "date_of_joining",
			"fieldtype": "Date",
			"width": 120
		},
		
		
		{
			"label": _("Present Days"),
			"fieldname": "present_days",
			"fieldtype": "float",
			"width": 120
		},
		{
			"label": _("Half Days"),
			"fieldname": "half_days",
			"fieldtype": "float",
			"width": 120
		},
		{
			"label": _("Worked Hours"),
			"fieldname": "work_hours",
			"fieldtype": "float",
			"width": 120
		},


		{
			"label": _("Total Working Days"),
			"fieldname": "total_days",
			"fieldtype": "float",
			"width": 120
		},
		{
			"label": _("Official Shift Hours"),
			"fieldname": "shift_hours",
			"fieldtype": "Data",
			"width": 120
		},
		{
			"label": _("Hours"),
			"fieldname": "total_hours",
			"fieldtype": "float",
			"width": 120
		},

		{
			"label": _("Absents"),
			"fieldname": "absents",
			"fieldtype": "float",
			"width": 120
		},
		{
			"label": _("A/L"),
			"fieldname": "annual_l",
			"fieldtype": "float",
			"width": 120
		},
		{
			"label": _("C/L"),
			"fieldname": "casual_l",
			"fieldtype": "float",
			"width": 120
		},
		{
			"label": _("M/L"),
			"fieldname": "medical_l",
			"fieldtype": "float",
			"width": 120
		},

		{
			"label": _("Month Days"),
			"fieldname": "month_days",
			"fieldtype": "float",
			"width": 120
		},
		{
			"label": _("Payable Days"),
			"fieldname": "payable_days",
			"fieldtype": "float",
			"width": 120
		},
		{
			"label": _("Late Counts"),
			"fieldname": "late_counts",
			"fieldtype": "float",
			"width": 120
		},
		{
			"label": _("Deduction Days"),
			"fieldname": "deduction_days",
			"fieldtype": "float",
			"width": 120
		}

	]
	return columns