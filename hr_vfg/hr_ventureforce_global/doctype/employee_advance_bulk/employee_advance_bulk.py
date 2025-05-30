import frappe
from frappe.model.document import Document
from datetime import datetime, timedelta

class EmployeeAdvanceBulk(Document):
    def validate(self):
        self.month_and_year()
        self.calculate_total_advance()

    def month_and_year(self):
        date_str = str(self.posting_date)
        date_obj = datetime.strptime(date_str, "%Y-%m-%d")  
        self.day = date_obj.strftime('%A')
        self.month = date_obj.strftime("%B") 
        self.year = date_obj.year

    def calculate_total_advance(self):
        amount = 0
        for i in self.employee_advance_bulk_ct:
            amount += i.amount or 0
        self.total_advance = amount

    @frappe.whitelist()
    def get_data(self):
        # Fetching employee data from `Employee` doctype
        rec = frappe.db.sql("""
            SELECT name, employee_name, department, designation, date_of_joining FROM `tabEmployee`
            WHERE status = 'Active'
        """, as_dict=1)

        # Clear the child table before appending new data
        self.employee_advance_bulk_ct = []

        # Loop through each employee record and append to the child table
        for r in rec:
            self.append('employee_advance_bulk_ct', {
                "employee_name": r['name'], 
                "designation": r.designation,
                "department": r['department'],  # Employee's department
                "date_of_joining": r['date_of_joining']  # Employee's date of joining
            })

        # Save the changes to the document after appending the child table data
        self.save()

    def on_submit(self):
        company = frappe.get_doc("Company", self.company)
        cash_acct = company.default_cash_account
        adv_acct  = company.default_employee_advance_account
        curr      = company.default_currency

        for row in self.employee_advance_bulk_ct:
            # — create & submit the Employee Advance —
            adv = (
                frappe.get_doc({
                    "doctype":                "Employee Advance",
                    "employee":               row.employee_name,
                    "company":                self.company,
                    "posting_date":           self.posting_date,
                    "currency":               curr,
                    "purpose":                self.remarks or "",
                    "exchange_rate":          1,
                    "advance_amount":         row.amount,
                    "mode_of_payment":        "Cash",
                    "advance_account":        adv_acct,
                    "repay_unclaimed_amount_from_salary": 1,
                    "custom_reference_document": self.doctype,
                    "custom_reference_voucher":  self.name
                })
                .insert()
                .submit()
            )

            # — create the Payment Entry as an advance —
            pe = frappe.new_doc("Payment Entry")
            pe.payment_type               = "Pay"
            pe.party_type                 = "Employee"
            pe.party                      = row.employee_name
            pe.party_name                 = frappe.get_value("Employee",
                                                           row.employee_name,
                                                           "employee_name")
            pe.company                    = self.company
            pe.posting_date               = self.posting_date

            pe.paid_from                  = cash_acct
            pe.paid_from_account_currency = curr
            pe.paid_to                    = adv_acct
            pe.paid_to_account_currency   = curr

            pe.paid_amount      = row.amount
            pe.received_amount  = row.amount

            pe.exchange_rate        = 1
            pe.source_exchange_rate = 1
            pe.target_exchange_rate = 1

            pe.mode_of_payment = "Cash"

            # **this flag** tells ERPNext these References are Advances
            pe.is_advance = 1

            # **append into the _References_ table**, not "advances"
            pe.append("references", {
                "reference_doctype":  "Employee Advance",
                "reference_name":     adv.name,
                "total_amount":       adv.advance_amount,
                "outstanding_amount": adv.advance_amount,
                "allocated_amount":   row.amount
            })

            pe.insert()
            pe.submit()

            # tell the Advance to recalc its paid_amount & status
            adv.reload()
            adv.set_total_advance_paid()

            # save the links back on your bulk row
            frappe.db.set_value(row.doctype, row.name, {
                "employee_advance": adv.name,
                "payment_entry":    pe.name
            }, update_modified=False)

        frappe.db.commit()