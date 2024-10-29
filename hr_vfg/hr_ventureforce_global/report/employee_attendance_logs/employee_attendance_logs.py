# Copyright (c) 2023, VFG and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
from multiprocessing import Condition

from frappe import msgprint, _
import frappe
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
	condition = {
		"status":"Active"
	}
	if filters.get("depart", None):
		condition["department"]=filters.depart
	if filters.get("employee", None):
		condition["employee"]=filters.employee
	employees = frappe.db.get_all("Employee",filters=condition,fields=["name","biometric_id"])
	id_list = []
	
	for emp in employees:
		if emp.biometric_id: id_list.append(emp.biometric_id)
	
	filters_data = [
		
		["attendance_date", ">=", filters.get("from")],
		["attendance_date", "<=", filters.get("to")],
		
	]
	if len(id_list) > 0:
		filters_data = [
		["biometric_id","in", tuple(id_list)],
		["attendance_date", ">=", filters.get("from")],
		["attendance_date", "<=", filters.get("to")],
		
	]
		
	records = frappe.db.get_all("Attendance Logs",
							  filters=filters_data,
							  fields=["*"],order_by="biometric_id, attendance_date ASC")
	prev_id = None
	prev_date =None
	in_log = []
	out_log = []
	data = []
	for r in records:
		if prev_id is None:
			prev_id  = r.biometric_id
			prev_date = getdate(r.attendance_date)
			if r.type == "Check In":
				in_log.append(r.attendance_time)
			if r.type == "Check Out":
				out_log.append(r.attendance_time)
		elif prev_id != r.biometric_id:
			sorted_in = sorted(in_log)
			sorted_out = sorted(out_log)
			day_name = datetime.strptime(
					str(r.attendance_date), '%Y-%m-%d').strftime('%A')
			
			
			row = {
                 "emp_id":frappe.db.get_value("Employee",{"biometric_id":r.biometric_id},"name"),
				  "att_id":r.biometric_id,
				"name":frappe.db.get_value("Employee",{"biometric_id":r.biometric_id},"employee_name"),
				"department":frappe.db.get_value("Employee",{"biometric_id":r.biometric_id},"department"),
				"designation":frappe.db.get_value("Employee",{"biometric_id":r.biometric_id},"designation"),
				"date":getdate(r.attendance_date),
				"day":day_name[:3],
				"att_status":get_att_status(r)
			}
			count = 0
			for in_l in sorted_in:
				if count==0:
					row["time_in_1"] = in_l
				elif count==1:
					row["time_in_2"] = in_l
				else:
					row["time_in_3"] = in_l
				count+=1
			count = 0
			for out_l in sorted_out:
				if count==0:
					row["time_out_1"] = out_l
				elif count==1:
					row["time_out_2"] = out_l
				else:
					row["time_out_3"] = out_l
				count+=1

			compute_times(row)
			data.append(row)


			prev_id = r.biometric_id
			prev_date = getdate(r.attendance_date)
			in_log = []
			out_log = []
			if r.type == "Check In":
				in_log.append(r.attendance_time)
			if r.type == "Check Out":
				out_log.append(r.attendance_time)
		elif prev_date != getdate(r.attendance_date):
			sorted_in = sorted(in_log)
			sorted_out = sorted(out_log)
			day_name = datetime.strptime(
					str(r.attendance_date), '%Y-%m-%d').strftime('%A')
			row = {
                 "emp_id":frappe.db.get_value("Employee",{"biometric_id":r.biometric_id},"name"),
				 "att_id":r.biometric_id,
				"name":frappe.db.get_value("Employee",{"biometric_id":r.biometric_id},"employee_name"),
				"department":frappe.db.get_value("Employee",{"biometric_id":r.biometric_id},"department"),
				"designation":frappe.db.get_value("Employee",{"biometric_id":r.biometric_id},"designation"),
				"date":getdate(r.attendance_date),
				"day":day_name[:3],
				"att_status":get_att_status(r)
			}
			count = 0
			for in_l in sorted_in:
				if count==0:
					row["time_in_1"] = in_l
				elif count==1:
					row["time_in_2"] = in_l
				else:
					row["time_in_3"] = in_l
				count+=1
			count = 0
			for out_l in sorted_out:
				if count==0:
					row["time_out_1"] = out_l
				elif count==1:
					row["time_out_2"] = out_l
				else:
					row["time_out_3"] = out_l
				count+=1

			compute_times(row)
			data.append(row)

			prev_date = getdate(r.attendance_date)
			in_log = []
			out_log = []
			if r.type == "Check In":
				in_log.append(r.attendance_time)
			if r.type == "Check Out":
				out_log.append(r.attendance_time)
		else:
			if r.type == "Check In":
				in_log.append(r.attendance_time)
			if r.type == "Check Out":
				out_log.append(r.attendance_time)
	return data

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
			"label": _("Att #"),
			"fieldname": "att_id",
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
			"label": _("Designation"),
			"fieldname": "designation",
			"fieldtype": "Data",
			"width": 200
		},
		
		{
			"label": _("Date"),
			"fieldname": "date",
			"fieldtype": "Data",
			"width": 120
		},
		{
			"label": _("Day"),
			"fieldname": "day",
			"fieldtype": "Data",
			"width": 120
		},
		{
			"label": _("In Time"),
			"fieldname": "time_in_1",
			"fieldtype": "Data",
			"width": 120
		},
		{
			"label": _("Out Time"),
			"fieldname": "time_out_1",
			"fieldtype": "Data",
			"width": 120
		},

		{
			"label": _("In Time"),
			"fieldname": "time_in_2",
			"fieldtype": "Data",
			"width": 120
		},
		{
			"label": _("Out Time"),
			"fieldname": "time_out_2",
			"fieldtype": "Data",
			"width": 120
		},
		{
			"label": _("In Time"),
			"fieldname": "time_in_3",
			"fieldtype": "Data",
			"width": 120
		},
		{
			"label": _("Out Time"),
			"fieldname": "time_out_3",
			"fieldtype": "Data",
			"width": 120
		},
		{
			"label": _("Stay Hours"),
			"fieldname": "stay_hours",
			"fieldtype": "Data",
			"width": 120
		},
		{
			"label": _("Break Hours"),
			"fieldname": "break_hours",
			"fieldtype": "Data",
			"width": 120
		},
		{
			"label": _("Att Status"),
			"fieldname": "att_status",
			"fieldtype": "Data",
			"width": 120
		},

	]
	return columns

def compute_times(row):
	total_stay_hours = 0
	total_not_stay_hours = 0

	in_time = None

	# Iterate through the dictionary
	for key, value in row.items():
		if key.startswith("time_in") and value:
			in_time = datetime.strptime(value, "%H:%M:%S")
		elif key.startswith("time_out") and value:
			out_time = datetime.strptime(value, "%H:%M:%S")
			if in_time:
				stay_duration = out_time - in_time
				total_stay_hours += stay_duration.total_seconds() / 3600  # Convert to hours
				in_time = None
	out_time = None

	# Iterate through the dictionary
	for key, value in row.items():
		if key.startswith("time_out") and value:
			out_time = datetime.strptime(value, "%H:%M:%S")
		elif key.startswith("time_in") and value:
			in_time = datetime.strptime(value, "%H:%M:%S")
			if out_time:
				out_duration = in_time - out_time 
				total_not_stay_hours += out_duration.total_seconds() / 3600  # Convert to hours
				out_time = None
			
	row["stay_hours"] = round(abs(total_stay_hours),2)
	row["break_hours"] = round(abs(total_not_stay_hours),2)


def get_att_status(r):
	employee_att = frappe.db.get_all(
					"Employee Attendance",
					fields=[
						"`tabEmployee Attendance`.`employee`",
						"`tabEmployee Attendance Table`.`date`",
						"`tabEmployee Attendance Table`.`absent`", 
			         "`tabEmployee Attendance Table`.`half_day`",
					 "`tabEmployee Attendance Table`.`weekly_off`",
					 "`tabEmployee Attendance Table`.`public_holiday`"],
					filters=[
						["Employee Attendance", "biometric_id", "=", r.biometric_id],
						["Employee Attendance Table", "date", "=", r.attendance_date],
						
					],
				)
	for item in employee_att:
		att_status = "In Time"
		if item.late:
			att_status = "Late Entry"
		elif item.absent:
			att_status = "Absent"
		elif item.half_day:
			att_status = "Half Day"
		if item.weekly_off or item.public_holiday:
			att_status = "Off"
		if item.type:
			att_status = item.type
		if att_status == "Absent":
						leaves  = frappe.get_all("Leave Application", filters={'employee': item.employee,
																				'from_date': ["<=", item.date], 'to_date': [">=", item.date],"status":"Approved"}, fields=["*"])
						if len(leaves) > 0:
							att_status = leaves[0].leave_type
		break
	return att_status