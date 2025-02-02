# Copyright (c) 2025, VFG and contributors
# For license information, please see license.txt


from __future__ import unicode_literals
import frappe
from frappe import msgprint, _
from datetime import datetime, timedelta
import datetime as special
from frappe.utils import fmt_money

# import frappe

def execute(filters=None):
	columns, data = [], []
	columns = get_column()
	data = get_data(filters)
	return columns, data

def get_column():
	column =[
    _("Emp. Id") + "::80",
	_("Name") + "::120",
	_("Designation") + "::120",	
	# _("Present Days Holiday") + "::80",
	_("Department") + "::80",
	_("Days Worked") + "::80",
	# _("Month Days") + "::80",	
	_("Gross Salary")+ "::100",
	_("O.T Hours")+ "::100",
	_("O.T Amount")+ "::100", 
	_("Total Income")+ "::100", 
	_("I. Tax")+ "::100", 
	_("Loan")+ "::100",
	_("E.O.B.I Ded.")+ "::100",
	_("Total Ded")+ "::100",
	_("Net Payable")+ "::100",
	_("Receiver Signature")+ "::100"
	]

	return column
def get_data(filters):
	cond ={}
	if filters.month:
		cond["month"] = filters.month
	if filters.year:
		cond["year"] = filters.year
	if filters.employee:
		cond["employee"] = filters.employee
	if filters.department:
		cond["department"] = filters.department
	#try:
	salary_slips = frappe.get_all("Salary Slip",filters=cond,fields=["*"])
	#
	data=[]
	
	for sp in salary_slips:
		row = []
		doc  = frappe.get_doc("Salary Slip",sp.name)
		leaves = 0.0
		for lev in doc.leave_details:
			leaves +=lev.taken
		basic = 0.0
		overtime = 0.0
		att_allow = 0.0
		conv_allow = 0.0
		leave_allow =0.0
		perf_allow =0.0
		other_allow = 0.0
		arrears = 0.0
		trip=0.0
		fuel = 0.0
		for ern in doc.earnings:
			if "Basic".lower() in ern.salary_component.lower():
				basic += ern.amount
			elif "Conveyance".lower() in ern.salary_component.lower():
				conv_allow = ern.amount
			elif "Overtime".lower() in ern.salary_component.lower():
				overtime += ern.amount
			elif "Fuel".lower() in ern.salary_component.lower():
				fuel += ern.amount
			elif "Attendance".lower() in ern.salary_component.lower():
				att_allow = ern.amount

		late = 0.0
		loan = 0.0
		short = 0.0
		adv = 0.0
		ad = 0.0
		abse = 0.0
		early = 0.0
		ladv = 0.0
		l_miss = 0.0
		tax = 0.0



		#for ll in doc.loans:
		#	if "Loan".lower() in ll.loan_type.lower():
		#		loan+=ll.principal_amount
		#	elif "Advance".lower() in ll.loan_type.lower():
		#		ladv += ll.principal_amount

		for ern in doc.deductions:
			if "Absent".lower() in ern.salary_component.lower():
				abse += ern.amount
			elif "employee advance".lower() in ern.salary_component.lower():
				ladv = ern.amount
			elif "Punch Missing".lower() in ern.salary_component.lower():
				l_miss = ern.amount
			elif "Late".lower() in ern.salary_component.lower():
				late = ern.amount
			elif "Early".lower() in ern.salary_component.lower():
				early = ern.amount
			elif "Short".lower() in ern.salary_component.lower():
				short = ern.amount
			elif "Tax".lower() in ern.salary_component.lower():
				tax = ern.amount	
		ladd = int(late+abse)
		lsld = int(early+short)
		tax = int(tax)

		#bb = basic/doc.total_working_days*float(doc.present_days)
		#gross = int(bb+overtime+att_allow+conv_allow+leave_allow+perf_allow+other_allow+arrears)
		#total_ded = int(abse+adv+late+early+loan_o_adv+short)
		#net_pay = gross-total_ded
		row =[
				doc.biometric_id,
				doc.employee_name,
				doc.designation,
				doc.department,
				# doc.total_present_days,
				doc.present_days,
				# doc.total_absents,
				# doc.total_month_days,
				# int(basic),
				# int(fuel),
				int(doc.basic_salary),
				int(doc.custom_total_over_time_le),
				int(overtime),
				int(doc.gross_pay),
				# int(att_allow),
				int(tax),
				int(l_miss),
				int(ladv),
				int(doc.total_deduction),
				# int(ladd),
				# int(lsld),
				int(doc.rounded_total),
				""
			]
		data.append(row)
			



	return data


@frappe.whitelist()
def get_day_name(date):
		day = special.datetime.strptime(str(date).replace("-", " "), '%Y %m %d').weekday()
		switcher = {
			0:"Monday",
			1:"Tuesday",
			2:"Wednesday",
			3:"Thursday",
			4:"Friday",
			5:"Saturday",
			6:"Sunday"
		}
		return switcher.get(day,"Not Found")
