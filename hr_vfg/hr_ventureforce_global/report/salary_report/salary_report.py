from __future__ import unicode_literals
import frappe
from frappe import msgprint, _
from datetime import datetime, timedelta
import datetime as special
from frappe.utils import fmt_money

def execute(filters=None):
    columns, data = [], []
    columns = get_column()
    data = get_data(filters)
    return columns, data

def get_column():
    column = [
        _("Code") + "::80",
        _("Name") + "::120",
        _("Designation") + "::120",
        _("Monthly Salary") + "::100",
        _("OT Amount") + "::100",
        _("Days Ded") + "::100",
        _("Late Short Ded") + "::100",
        _("Fuel") + "::100",
        _("Net Salary") + "::100",
        _("Advance") + "::100",
        _("Loan") + "::100",
        _("Net Payable") + "::100"
    ]
    return column

def get_data(filters):
    cond = {}
    if filters.month:
        cond["month"] = filters.month
    if filters.employee:
        cond["employee"] = filters.employee
    if filters.department:
        cond["department"] = filters.department

    salary_slips = frappe.get_all("Salary Slip", filters=cond, fields=["*"])
    data = []
    
    for sp in salary_slips:
        doc = frappe.get_doc("Salary Slip", sp.name)

        # Initialize variables
        basic = 0.0
        overtime = 0.0
        late = 0.0
        short = 0.0
        advance = 0.0
        loan = 0.0
        net_salary = 0.0

        # Process earnings
        for ern in doc.earnings:
            if "Basic".lower() in ern.salary_component.lower():
                basic += ern.amount
            elif "Overtime".lower() in ern.salary_component.lower():
                overtime += ern.amount
            elif "Fuel".lower() in ern.salary_component.lower():
                fuel += ern.amount
            

        # Process deductions
        for ded in doc.deductions:
            if "Late".lower() in ded.salary_component.lower():
                late += ded.amount
            elif "Short".lower() in ded.salary_component.lower():
                short += ded.amount
            elif "Advance".lower() in ded.salary_component.lower():
                advance += ded.amount
            elif "Loan".lower() in ded.salary_component.lower():
                loan += ded.amount
            

        # Calculate late + short deduction
        late_short_ded = int(late + short)

        # Calculate net salary
        net_salary = int(doc.gross_pay - (late + short + advance + loan))

        # Append row
        row = [
            doc.biometric_id,
            doc.employee_name,
            doc.designation,
            int(basic),
            int(overtime),
            int(doc.days_deducted if hasattr(doc, 'days_deducted') else 0),

            late_short_ded,
            int(doc.fuel_allowance if hasattr(doc, 'fuel_allowance') else 0),
            net_salary,
            int(advance),
            int(loan),
            int(doc.rounded_total)
        ]
        data.append(row)
    
    return data

@frappe.whitelist()
def get_day_name(date):
    day = special.datetime.strptime(str(date).replace("-", " "), '%Y %m %d').weekday()
    switcher = {
        0: "Monday",
        1: "Tuesday",
        2: "Wednesday",
        3: "Thursday",
        4: "Friday",
        5: "Saturday",
        6: "Sunday"
    }
    return switcher.get(day, "Not Found")
