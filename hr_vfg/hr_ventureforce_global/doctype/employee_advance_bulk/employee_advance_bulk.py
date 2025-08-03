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
        adv_acct  = company.default_employee_advance_account
        curr      = company.default_currency

        for row in self.employee_advance_bulk_ct:
            # — create & submit the Employee Advance only —
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
                    "custom_reference_voucher": self.name
                })
                .insert()
                .submit()
            )

            # save the employee advance link back on your bulk row
            frappe.db.set_value(row.doctype, row.name, {
                "employee_advance": adv.name
            }, update_modified=False)

        frappe.db.commit()
        frappe.msgprint("Employee Advances created successfully. Use 'Create Disbursed Payment' button to create payment entries.")

    @frappe.whitelist()
    def create_disbursed_payment(self):
        """Create Payment Entry for disbursement after document is submitted"""
        # Get the document if called from JavaScript
        if not hasattr(self, 'name') or not self.name:
            self = frappe.get_doc("Employee Advance Bulk", frappe.form_dict.docname)
        
        if self.docstatus != 1:
            frappe.throw("Document must be submitted before creating payment entries.")
        
        company = frappe.get_doc("Company", self.company)
        
        # Get cash account - try multiple sources
        cash_acct = self.account  # Use the account field from the document
        if not cash_acct:
            # Try to get from company settings
            cash_acct = company.default_cash_account
        if not cash_acct:
            # Try to get from company settings directly
            cash_acct = frappe.db.get_value("Company", self.company, "default_cash_account")
        if not cash_acct:
            frappe.throw("Cash account not found. Please set the account field in the document or default cash account in Company settings.")
        
        # Verify the cash account exists
        if not frappe.db.exists("Account", cash_acct):
            frappe.throw(f"Cash account '{cash_acct}' does not exist in the database.")
        
        # Get employee advance account
        adv_acct = company.default_employee_advance_account
        if not adv_acct:
            frappe.throw("Employee advance account not found. Please set default employee advance account in Company settings.")
        
        # Verify the employee advance account exists
        if not frappe.db.exists("Account", adv_acct):
            frappe.throw(f"Employee advance account '{adv_acct}' does not exist in the database.")
        
        curr = company.default_currency

        # Debug information
        print(f"DEBUG: Company: {self.company}")
        print(f"DEBUG: Document Account Field: {self.account}")
        print(f"DEBUG: Company Default Cash Account: {company.default_cash_account}")
        print(f"DEBUG: Final Cash Account: {cash_acct}")
        print(f"DEBUG: Employee Advance Account: {adv_acct}")
        print(f"DEBUG: Currency: {curr}")

        payment_entries_created = 0

        for row in self.employee_advance_bulk_ct:
            if row.employee_advance and not row.payment_entry:
                # Verify employee exists
                if not frappe.db.exists("Employee", row.employee_name):
                    frappe.throw(f"Employee '{row.employee_name}' does not exist in the database.")
                
                # Verify employee advance exists
                if not frappe.db.exists("Employee Advance", row.employee_advance):
                    frappe.throw(f"Employee Advance '{row.employee_advance}' does not exist in the database.")
                
                # Get the employee advance document
                adv = frappe.get_doc("Employee Advance", row.employee_advance)
                
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

                # Validate required fields before saving
                if not pe.paid_from:
                    frappe.throw(f"Paid From account is missing for employee {row.employee_name}")
                if not pe.paid_to:
                    frappe.throw(f"Paid To account is missing for employee {row.employee_name}")
                if not pe.party:
                    frappe.throw(f"Party is missing for employee {row.employee_name}")

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

                # save the payment entry link back on your bulk row
                frappe.db.set_value(row.doctype, row.name, {
                    "payment_entry": pe.name
                }, update_modified=False)

                payment_entries_created += 1

        frappe.db.commit()
        
        if payment_entries_created > 0:
            frappe.msgprint(f"Successfully created {payment_entries_created} payment entries for disbursement.")
        else:
            frappe.msgprint("No payment entries were created. All advances may already have payment entries.")
        
        return {
            "payment_entries_created": payment_entries_created,
            "message": f"Successfully created {payment_entries_created} payment entries for disbursement."
        }

@frappe.whitelist()
def create_disbursed_payment(docname):
    """Standalone function to create disbursed payment entries"""
    doc = frappe.get_doc("Employee Advance Bulk", docname)
    return doc.create_disbursed_payment()

@frappe.whitelist()
def get_dashboard_data():
    """Get dashboard statistics for Employee Advance Bulk"""
    try:
        # Count all Employee Advances
        employee_advances_count = frappe.db.count("Employee Advance", {
            "docstatus": 1
        })
        
        # Count all Payment Entries that are advances
        payment_entries_count = frappe.db.count("Payment Entry", {
            "is_advance": 1,
            "docstatus": 1
        })
        
        # Count submitted Employee Advance Bulk documents
        bulk_documents_count = frappe.db.count("Employee Advance Bulk", {
            "docstatus": 1
        })
        
        return {
            "employee_advances": employee_advances_count,
            "payment_entries": payment_entries_count,
            "bulk_documents": bulk_documents_count
        }
    except Exception as e:
        frappe.log_error(f"Error getting dashboard data: {str(e)}", "Employee Advance Bulk Dashboard Error")
        return {
            "employee_advances": 0,
            "payment_entries": 0,
            "bulk_documents": 0
        }