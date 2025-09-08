# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and Contributors
# License: GNU General Public License v3. See license.txt


import datetime
import math
from operator import index

import frappe
from frappe import _, msgprint
from frappe.model.naming import make_autoname
from frappe.utils import (
	add_days,
	cint,
	cstr,
	date_diff,
	flt,
	formatdate,
	get_first_day,
	get_last_day,
	getdate,
	money_in_words,
	rounded,
)
import calendar
from frappe.utils.background_jobs import enqueue
from six import iteritems

from erpnext.setup.doctype.employee.employee import get_holiday_list_for_employee
from erpnext.setup.doctype.employee.employee import (
    InactiveEmployeeStatusError
)

# from hrms.hr.doctype.employee.employee import (
# 	InactiveEmployeeStatusError,
# 	get_holiday_list_for_employee,
# )

import erpnext
from erpnext.accounts.utils import get_fiscal_year
from hrms.hr.utils import get_holiday_dates_for_employee, validate_active_employee
# from erpnext.loan_management.doctype.loan_repayment.loan_repayment import (
# 	calculate_amounts,
# 	create_repayment_entry,
# )
from hrms.payroll.doctype.additional_salary.additional_salary import get_additional_salaries
from hrms.payroll.doctype.employee_benefit_application.employee_benefit_application import (
	get_benefit_component_amount,
)
from hrms.payroll.doctype.employee_benefit_claim.employee_benefit_claim import (
	get_benefit_claim_amount,
	get_last_payroll_period_benefits,
)
from hrms.payroll.doctype.payroll_entry.payroll_entry import get_start_end_dates
from hrms.payroll.doctype.payroll_period.payroll_period import (
	get_payroll_period,
	get_period_factor,
)
from erpnext.utilities.transaction_base import TransactionBase
from hrms.payroll.doctype.salary_slip.salary_slip import SalarySlip


class CustomSalarySlip(SalarySlip):
    def get_advance_deduction_component(self):
        # Get the latest salary structure assignment for the employee as of the end date
        assignment = frappe.get_all(
            "Salary Structure Assignment",
            filters={
                "employee": self.employee,
                "from_date": ["<=", self.end_date],
                "docstatus": 1,
            },
            fields=["salary_structure"],
            order_by="from_date desc",
            limit=1,
        )
        if not assignment:
            return None

        salary_structure = assignment[0].salary_structure
        structure_doc = frappe.get_doc("Salary Structure", salary_structure)
        # Find deduction component with 'advance' in the name
        for row in structure_doc.deductions:
            if "advance" in row.salary_component.lower():
                return row.salary_component
        return None

    def add_employee_advance_deductions(self):
        advances = frappe.get_all(
            "Employee Advance",
            filters={
                "employee": self.employee,
                "repay_unclaimed_amount_from_salary": 1,
                "docstatus": 1,
                "status": ["in", ["Paid", "Unpaid"]],
                # Only include advances that were posted within the salary slip period
                "posting_date": ["between", [self.start_date, self.end_date]]
            },
            fields=["name", "paid_amount", "claimed_amount", "return_amount", "advance_account", "posting_date"],
        )
        # Dynamically get the deduction component
        deduction_component = self.get_advance_deduction_component()
        if not deduction_component:
            frappe.throw(_("No 'Advance' deduction component found in the assigned Salary Structure for this employee."))

        for adv in advances:
            unclaimed = (adv.paid_amount or 0) - (adv.claimed_amount or 0) - (adv.return_amount or 0)
            if unclaimed > 0:
                # Check if there's already an Additional Salary for this advance in this payroll period
                additional_salary_exists = frappe.get_all(
                    "Additional Salary",
                    filters={
                        "employee": self.employee,
                        "ref_doctype": "Employee Advance",
                        "ref_docname": adv.name,
                        "docstatus": 1,
                        "payroll_date": ["between", [self.start_date, self.end_date]]
                    },
                    limit=1
                )
                
                # Only add direct deduction if no Additional Salary exists for this advance
                if not additional_salary_exists:
                    # Check if this advance is already in deductions by checking ref_docname
                    already_exists = False
                    for d in self.get("deductions", []):
                        if hasattr(d, 'ref_docname') and d.ref_docname == adv.name:
                            already_exists = True
                            break
                    
                    if not already_exists:
                        self.append("deductions", {
                            "salary_component": deduction_component,
                            "amount": unclaimed,
                            "account": adv.advance_account,
                            "ref_doctype": "Employee Advance",
                            "ref_docname": adv.name,
                        })

    def validate(self):
        super().validate()
        self.add_employee_advance_deductions()
	
	# def get_taxable_earnings_for_prev_period(self, payroll_period,start_date, end_date, allow_tax_exemption=False):
	# 	payroll_period = get_payroll_period(self.start_date, self.end_date, self.company)
	# 	prev = frappe.db.sql("""select previous_salary_earned from `tabPrevious Salary Detail` where employee=%s and payroll_period=%s""",
	# 		(self.employee,payroll_period.name))
		
	# 	prev_earned = flt(prev[0][0]) if prev else 0	
	# 	taxable_earnings = frappe.db.sql("""
	# 		select sum(sd.amount)
	# 		from
	# 			`tabSalary Detail` sd join `tabSalary Slip` ss on sd.parent=ss.name
	# 		where
	# 			sd.parentfield='earnings'
	# 			and sd.is_tax_applicable=1
	# 			and is_flexible_benefit=0
	# 			and ss.docstatus=1
	# 			and ss.employee=%(employee)s
	# 			and ss.start_date between %(from_date)s and %(to_date)s
	# 			and ss.end_date between %(from_date)s and %(to_date)s
	# 		""", {
	# 			"employee": self.employee,
	# 			"from_date": start_date,
	# 			"to_date": end_date
	# 		})
	# 	taxable_earnings = flt(taxable_earnings[0][0]) if taxable_earnings else 0

	# 	exempted_amount = 0
	# 	if allow_tax_exemption:
	# 		exempted_amount = frappe.db.sql("""
	# 			select sum(sd.amount)
	# 			from
	# 				`tabSalary Detail` sd join `tabSalary Slip` ss on sd.parent=ss.name
	# 			where
	# 				sd.parentfield='deductions'
	# 				and sd.exempted_from_income_tax=1
	# 				and is_flexible_benefit=0
	# 				and ss.docstatus=1
	# 				and ss.employee=%(employee)s
	# 				and ss.start_date between %(from_date)s and %(to_date)s
	# 				and ss.end_date between %(from_date)s and %(to_date)s
	# 			""", {
	# 				"employee": self.employee,
	# 				"from_date": start_date,
	# 				"to_date": end_date
	# 			})
	# 		exempted_amount = flt(exempted_amount[0][0]) if exempted_amount else 0

		
	# 	frappe.msgprint(str(prev_earned))
	# 	return (taxable_earnings + prev_earned) - exempted_amount
	
	# def get_tax_paid_in_period(self, start_date, end_date, tax_component):
	# 			payroll_period = get_payroll_period(self.start_date, self.end_date, self.company)
	# 			prev = frappe.db.sql("""select previous_tax_paid from `tabPrevious Salary Detail` where employee=%s and payroll_period=%s""",
	# 				(self.employee,payroll_period.name))
	# 			prev_paid = flt(prev[0][0]) if prev else 0
	# 			# find total_tax_paid, tax paid for benefit, additional_salary
	# 			total_tax_paid = flt(frappe.db.sql("""
	# 				select
	# 					sum(sd.amount)
	# 				from
	# 					`tabSalary Detail` sd join `tabSalary Slip` ss on sd.parent=ss.name
	# 				where
	# 					sd.parentfield='deductions'
	# 					and sd.salary_component=%(salary_component)s
	# 					and sd.variable_based_on_taxable_salary=1
	# 					and ss.docstatus=1
	# 					and ss.employee=%(employee)s
	# 					and ss.start_date between %(from_date)s and %(to_date)s
	# 					and ss.end_date between %(from_date)s and %(to_date)s
	# 			""", {
	# 				"salary_component": tax_component,
	# 				"employee": self.employee,
	# 				"from_date": start_date,
	# 				"to_date": end_date
	# 			})[0][0])

	# 			return total_tax_paid + prev_paid

def add_leaves(doc, method):
			
			rec = frappe.db.sql("""select name from `tabLeave Application` where status="Approved" and  from_date>=%s and to_date<=%s 
				                             and employee=%s and custom_late_absent_adjusted_as_a_leave=1 and docstatus=1 """,
				                      (getdate(doc.get("start_date")),getdate(doc.get("end_date")),doc.employee), as_dict=True)
			
			adj_list = []
			for r in rec:
				adj_list.append(r.name)

			doc.late_adjustments = len(adj_list)
			doc.absents_adjustments = len(frappe.db.get_all("Attendance", 
						{"attendance_date":["between",[doc.start_date,doc.end_date]],"status":"On Leave","docstatus":1,
							"employee":doc.employee,"leave_application":["not in",adj_list]}))
			doc.half_days_adjustments =  len(frappe.db.get_all("Attendance", 
						{"attendance_date":["between",[doc.start_date,doc.end_date]],"status":"Half Day","docstatus":1,
							"employee":doc.employee,"leave_application":["not in",adj_list]}))
			doc.annual_leave_ =  len(frappe.db.get_all("Attendance", 
						{"attendance_date":["between",[doc.start_date,doc.end_date]],"status":"On Leave","docstatus":1,
							"employee":doc.employee,"leave_type":"Annual Leave"})) + (len(frappe.db.get_all("Attendance", 
						{"attendance_date":["between",[doc.start_date,doc.end_date]],"status":"Half Day","docstatus":1,
							"employee":doc.employee,"leave_type":"Annual Leave"}))/2)
			doc.sick_leave = len(frappe.db.get_all("Attendance", 
						{"attendance_date":["between",[doc.start_date,doc.end_date]],"status":"On Leave","docstatus":1,
							"employee":doc.employee,"leave_type":"Sick Leave"})) + (len(frappe.db.get_all("Attendance", 
						{"attendance_date":["between",[doc.start_date,doc.end_date]],"status":"Half Day","docstatus":1,
							"employee":doc.employee,"leave_type":"Sick Leave"}))/2)
			doc.emergency_leave = len(frappe.db.get_all("Attendance", 
						{"attendance_date":["between",[doc.start_date,doc.end_date]],"status":"On Leave","docstatus":1,
							"employee":doc.employee,"leave_type":"Emergency Leave"})) + (len(frappe.db.get_all("Attendance", 
						{"attendance_date":["between",[doc.start_date,doc.end_date]],"status":"Half Day","docstatus":1,
							"employee":doc.employee,"leave_type":"Emergency Leave"}))/2)
			doc.casual_leave = len(frappe.db.get_all("Attendance", 
						{"attendance_date":["between",[doc.start_date,doc.end_date]],"status":"On Leave","docstatus":1,
							"employee":doc.employee,"leave_type":"Casual Leave"})) + (len(frappe.db.get_all("Attendance", 
						{"attendance_date":["between",[doc.start_date,doc.end_date]],"status":"Half Day","docstatus":1,
							"employee":doc.employee,"leave_type":"Casual Leave"}))/2)
			
		