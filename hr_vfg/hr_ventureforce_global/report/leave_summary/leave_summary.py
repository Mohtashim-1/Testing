# Copyright (c) 2013, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt


from itertools import groupby
from typing import Dict, List, Optional, Tuple

import frappe
from frappe import _
from frappe.utils import add_days, getdate

from hrms.hr.doctype.leave_allocation.leave_allocation import get_previous_allocation
from hrms.hr.doctype.leave_application.leave_application import (
	get_leave_balance_on,
	get_leaves_for_period,
)

Filters = frappe._dict


def execute(filters: Optional[Filters] = None) -> Tuple:
	if filters.to_date <= filters.from_date:
		frappe.throw(_('"From Date" can not be greater than or equal to "To Date"'))

	columns = get_columns()
	data = get_data(filters)
	return columns, data


def get_columns() -> List[Dict]:
	return [
		
		{
			"label": _("Employee"),
			"fieldtype": "Link",
			"fieldname": "employee",
			"width": 100,
			"options": "Employee",
		},
		{
			"label": _("Employee Name"),
			"fieldtype": "Dynamic Link",
			"fieldname": "employee_name",
			"width": 100,
			"options": "employee",
		},
		{
			"label": _("Joining Date"),
			"fieldtype": "Date",
			"fieldname": "date_of_joining",
			"width": 100,
		},
		{
			"label": _("Department"),
			"fieldtype": "Data",
			"fieldname": "department",
			"width": 100,
		},
		{
			"label": _("Designation"),
			"fieldtype": "Data",
			"fieldname": "designation",
			"width": 100,
		},
		
		{
			"label": _("Initial A/L"),
			"fieldtype": "float",
			"fieldname": "opening_balance_annual",
			"width": 100,
		},
		
		{
			"label": _("Initial C/L"),
			"fieldtype": "float",
			"fieldname": "opening_balance_casual",
			"width": 100,
		},
		
		{
			"label": _("Initial M/L"),
			"fieldtype": "float",
			"fieldname": "opening_balance_medical",
			"width": 100,
		},

		# {
		# 	"label": _("Alloc A/L"),
		# 	"fieldtype": "float",
		# 	"fieldname": "allocated_annual",
		# 	"width": 100,
		# },
		
		# {
		# 	"label": _("Alloc C/L"),
		# 	"fieldtype": "float",
		# 	"fieldname": "allocated_casual",
		# 	"width": 100,
		# },
		
		# {
		# 	"label": _("Alloc M/L"),
		# 	"fieldtype": "float",
		# 	"fieldname": "allocated_medical",
		# 	"width": 100,
		# },
		
		{
			"label": _("Taken A/L"),
			"fieldtype": "float",
			"fieldname": "leaves_taken_annual",
			"width": 100,
		},
		{
			"label": _("Taken C/L"),
			"fieldtype": "float",
			"fieldname": "leaves_taken_casual",
			"width": 100,
		},
		{
			"label": _("Taken M/L"),
			"fieldtype": "float",
			"fieldname": "leaves_taken_medical",
			"width": 100,
		},
		
		{
			"label": _("Balance A/L"),
			"fieldtype": "float",
			"fieldname": "closing_balance_annual",
			"width": 100,
		},
		{
			"label": _("Balance C/L"),
			"fieldtype": "float",
			"fieldname": "closing_balance_casual",
			"width": 100,
		},
		{
			"label": _("Balance M/L"),
			"fieldtype": "float",
			"fieldname": "closing_balance_medical",
			"width": 100,
		},
	]


def get_data(filters: Filters) -> List:
	leave_types = ["Annual Leave","Casual Leave","Medical Leave"]
	conditions = get_conditions(filters)

	user = frappe.session.user
	department_approver_map = get_department_leave_approver_map(filters.get("department"))

	active_employees = frappe.get_list(
		"Employee",
		filters=conditions,
		fields=["name", "employee_name", "designation","department", "user_id", "leave_approver"],
	)

	data = []

	

	for employee in active_employees:
			row = frappe._dict({})
			row.employee = employee.name
			row.department = employee.department
			row.designation = employee.designation
			row.employee_name = employee.employee_name

			for leave_type in leave_types:
				
				leave_approvers = department_approver_map.get(employee.department_name, []).append(
					employee.leave_approver
				)

				if (
					(leave_approvers and len(leave_approvers) and user in leave_approvers)
					or (user in ["Administrator", employee.user_id])
					or ("HR Manager" in frappe.get_roles(user))
				):
					
					leaves_taken = (
						get_leaves_for_period(employee.name, leave_type, filters.from_date, filters.to_date) * -1
					)

					new_allocation, expired_leaves, carry_forwarded_leaves = get_allocated_and_expired_leaves(
						filters.from_date, filters.to_date, employee.name, leave_type
					)
					opening = get_opening_balance(employee.name, leave_type, filters, carry_forwarded_leaves)

					if leave_type == "Annual Leave":
						row.opening_balance_annual = opening + new_allocation 
						#row.allocated_annual = new_allocation
						row.leaves_taken_annual = leaves_taken 
						row.closing_balance_annual = new_allocation + opening - (expired_leaves + leaves_taken)
					elif leave_type == "Casual Leave":
						row.opening_balance_casual = opening + new_allocation 
						#row.allocated_casual = new_allocation
						row.leaves_taken_casual = leaves_taken
						row.closing_balance_casual = new_allocation + opening - (expired_leaves + leaves_taken)
					else:
						row.opening_balance_medical = opening + new_allocation 
						#row.allocated_medical = new_allocation
						row.leaves_taken_medical = leaves_taken
						row.closing_balance_medical = new_allocation + opening - (expired_leaves + leaves_taken)
					
				
			data.append(row)

	return data


def get_opening_balance(
	employee: str, leave_type: str, filters: Filters, carry_forwarded_leaves: float
) -> float:
	# allocation boundary condition
	# opening balance is the closing leave balance 1 day before the filter start date
	opening_balance_date = add_days(filters.from_date, -1)
	allocation = get_previous_allocation(filters.from_date, leave_type, employee)

	if (
		allocation
		and allocation.get("to_date")
		and opening_balance_date
		and getdate(allocation.get("to_date")) == getdate(opening_balance_date)
	):
		# if opening balance date is same as the previous allocation's expiry
		# then opening balance should only consider carry forwarded leaves
		opening_balance = carry_forwarded_leaves
	else:
		# else directly get leave balance on the previous day
		opening_balance = get_leave_balance_on(employee, leave_type, opening_balance_date)

	return opening_balance


def get_conditions(filters: Filters) -> Dict:
	conditions = {}

	if filters.get("employee"):
		conditions["name"] = filters.get("employee")

	if filters.get("company"):
		conditions["company"] = filters.get("company")

	if filters.get("department"):
		conditions["department"] = filters.get("department")

	if filters.get("employee_status"):
		conditions["status"] = filters.get("employee_status")

	return conditions


def get_department_leave_approver_map(department: Optional[str] = None):
	# get current department and all its child
	department_list = frappe.get_list(
		"Department",
		filters={"disabled": 0},
		or_filters={"name": department, "parent_department": department},
		pluck="name",
	)
	# retrieve approvers list from current department and from its subsequent child departments
	approver_list = frappe.get_all(
		"Department Approver",
		filters={"parentfield": "leave_approvers", "parent": ("in", department_list)},
		fields=["parent", "approver"],
		as_list=True,
	)

	approvers = {}

	for k, v in approver_list:
		approvers.setdefault(k, []).append(v)

	return approvers


def get_allocated_and_expired_leaves(
	from_date: str, to_date: str, employee: str, leave_type: str
) -> Tuple[float, float, float]:
	new_allocation = 0
	expired_leaves = 0
	carry_forwarded_leaves = 0

	records = get_leave_ledger_entries(from_date, to_date, employee, leave_type)

	for record in records:
		# new allocation records with `is_expired=1` are created when leave expires
		# these new records should not be considered, else it leads to negative leave balance
		if record.is_expired:
			continue

		if record.to_date < getdate(to_date):
			# leave allocations ending before to_date, reduce leaves taken within that period
			# since they are already used, they won't expire
			expired_leaves += record.leaves
			expired_leaves += get_leaves_for_period(employee, leave_type, record.from_date, record.to_date)

		if record.from_date >= getdate(from_date):
			if record.is_carry_forward:
				carry_forwarded_leaves += record.leaves
			else:
				new_allocation += record.leaves

	return new_allocation, expired_leaves, carry_forwarded_leaves


def get_leave_ledger_entries(
	from_date: str, to_date: str, employee: str, leave_type: str
) -> List[Dict]:
	ledger = frappe.qb.DocType("Leave Ledger Entry")
	records = (
		frappe.qb.from_(ledger)
		.select(
			ledger.employee,
			ledger.leave_type,
			ledger.from_date,
			ledger.to_date,
			ledger.leaves,
			ledger.transaction_name,
			ledger.transaction_type,
			ledger.is_carry_forward,
			ledger.is_expired,
		)
		.where(
			(ledger.docstatus == 1)
			& (ledger.transaction_type == "Leave Allocation")
			& (ledger.employee == employee)
			& (ledger.leave_type == leave_type)
			& (
				(ledger.from_date[from_date:to_date])
				| (ledger.to_date[from_date:to_date])
				| ((ledger.from_date < from_date) & (ledger.to_date > to_date))
			)
		)
	).run(as_dict=True)

	return records

