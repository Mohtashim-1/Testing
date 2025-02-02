from __future__ import unicode_literals
import frappe
from frappe import msgprint, _
from datetime import datetime, timedelta
import datetime as special
from frappe.utils import fmt_money

def execute(filters=None):
    columns, data = [], []
    columns = get_column()
    data = get_data(filters, columns)
    return columns, data

def get_column():
    column = [
        _("S No") + "::80",  # Add serial number column
        _("Emp Id") + "::80",
        _("Name") + "::120",
        _("Designation") + "::120",    
        _("Days Worked") + "::80",
        _("Gross Salary") + "::100",
        _("OT Hours") + "::100",
        _("OT Amount") + "::100", 
        _("Total Income") + "::100", 
        _("I Tax") + "::100", 
        _("Loan") + "::100",
        _("E.O.B.I Ded.") + "::100",
        _("Total Ded") + "::100",
        _("Net Payable") + "::100",
        _("Receiver Signature") + "::100"
    ]
    return column


def get_data(filters, columns):
    cond = {}
    if filters.month:
        cond["month"] = filters.month
    if filters.year:
        cond["year"] = filters.year
    if filters.employee:
        cond["employee"] = filters.employee
    if filters.department:
        cond["department"] = filters.department

    # Fetch salary slips based on filters
    salary_slips = frappe.get_all("Salary Slip", filters=cond, fields=["*"])

    # Create a dictionary to group data by department
    grouped_data = {}

    # Loop through the salary slips and group them by department
    serial_no = 1  # Start serial number
    for sp in salary_slips:
        doc = frappe.get_doc("Salary Slip", sp.name)

        # Grouping data by department
        if doc.department not in grouped_data:
            grouped_data[doc.department] = []

        # Initialize salary components to default values
        overtime = 0.0
        tax = 0.0
        loan = 0.0
        abse = 0.0
        early = 0.0
        late = 0.0

        # Iterate over earnings and calculate overtime
        for ern in doc.earnings:
            if "Overtime".lower() in ern.salary_component.lower():
                overtime += ern.amount

        # Iterate over deductions and calculate tax, loan, and others
        for ern in doc.deductions:
            if "Tax".lower() in ern.salary_component.lower():
                tax = ern.amount
            elif "Absent".lower() in ern.salary_component.lower():
                abse += ern.amount
            elif "Late".lower() in ern.salary_component.lower():
                late = ern.amount
            elif "Early".lower() in ern.salary_component.lower():
                early = ern.amount

        # Prepare row data for each salary slip
        row = [
            serial_no,  # Add serial number here
            doc.biometric_id or "",  # Default empty string if missing
            doc.employee_name or "",  # Default empty string if missing
            doc.designation or "",  # Default empty string if missing
            doc.present_days or 0,  # Default to 0 if missing
            int(doc.basic_salary) if doc.basic_salary else 0,  # Default to 0 if missing
            int(doc.custom_total_over_time_le),
            int(overtime),
            int(doc.gross_pay) if doc.gross_pay else 0,  # Default to 0 if missing
            int(tax),
            int(late),
            int(0),
            int(doc.total_deduction) if doc.total_deduction else 0,  # Default to 0 if missing
            int(doc.rounded_total) if doc.rounded_total else 0,  # Default to 0 if missing
            ""  # Empty field for the receiver signature
        ]

        # Debugging: Check if the row has the correct number of columns
        if len(row) == len(columns):
            grouped_data[doc.department].append(row)
        else:
            frappe.msgprint(_("Row length mismatch in department: {} for employee: {}").format(doc.department, doc.employee_name))
            # Print the row data for debugging
            print(f"Row data for employee {doc.employee_name}: {row}")
            # Padding the row if shorter or truncating if too long
            if len(row) < len(columns):
                row += [""] * (len(columns) - len(row))  # Pad with empty values
            elif len(row) > len(columns):
                row = row[:len(columns)]  # Truncate extra columns

            grouped_data[doc.department].append(row)

        serial_no += 1  # Increment serial number after processing each row

    # Convert the grouped data into a list of rows for each department
    data = []
    for department, rows in grouped_data.items():
        # Add a department header row, ensure that the department name spans across all columns
        department_row = [""] * len(columns)  # Create an empty row with the same length as columns
        department_row[1] = department  # Place the department name in the second column (skip serial number)
        
        # Add the department row as the first row
        data.append(department_row)

        # Initialize totals for the department
        total_gross_salary = 0
        total_ot_hours = 0
        total_ot_amount = 0
        total_income = 0
        total_tax = 0
        total_loan = 0
        total_eobi = 0
        total_ded = 0
        total_net_payable = 0

        # Add all rows under the department
        for row in rows:
            data.append(row)

            # Accumulate totals for each department
            total_gross_salary += row[5]  # Gross Salary
            total_ot_hours += row[6]  # OT Hours
            total_ot_amount += row[7]  # OT Amount
            total_income += row[8]  # Total Income
            total_tax += row[9]  # Tax
            total_loan += row[10]  # Loan
            total_eobi += row[11]  # E.O.B.I Ded.
            total_ded += row[12]  # Total Ded
            total_net_payable += row[13]  # Net Payable
            totals_row = [
				"<b>" + _("Total") + "</b>",  # Bold label for Total
				"",  # Leave Name blank
				"",  # Leave Name blank
				"",  # Leave Name blank
				"",  # Leave Designation blank
				"<b>" + str(total_gross_salary) + "</b>",  # Bold Total Gross Salary
				"<b>" + str(total_ot_hours) + "</b>",  # Bold Total OT Hours
				"<b>" + str(total_ot_amount) + "</b>",  # Bold Total OT Amount
				"<b>" + str(total_income) + "</b>",  # Bold Total Income
				"<b>" + str(total_tax) + "</b>",  # Bold Total Tax
				"<b>" + str(total_loan) + "</b>",  # Bold Total Loan
				"<b>" + str(total_eobi) + "</b>",  # Bold Total E.O.B.I Ded.
				"<b>" + str(total_ded) + "</b>",  # Bold Total Ded
				"<b>" + str(total_net_payable) + "</b>",  # Bold Total Net Payable
				""  # Receiver Signature field remains empty
			]


        # Add the totals row to the data
        data.append(totals_row)

    return data
