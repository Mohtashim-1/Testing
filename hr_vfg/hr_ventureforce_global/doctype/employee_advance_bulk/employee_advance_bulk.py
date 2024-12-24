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
        for r in self.employee_advance_bulk_ct:
            # Ensure the employee has valid data
            employee_data = frappe.db.get_value('Employee', r.employee_name, ['date_of_joining', 'relieving_date'], as_dict=True)

            if not employee_data:
                frappe.throw(f"Cannot create Additional Salary for {r.employee_name}. Employee data not found.")
            
            if not employee_data.get('date_of_joining'):
                frappe.throw(f"Cannot create Additional Salary for {r.employee_name}. Date of joining is missing.")
            
            doc = frappe.get_doc({
                'doctype': 'Additional Salary',
                'employee': r.employee_name,  # Use the employee's unique ID here
                'company': self.company,
                'payroll_date': self.posting_date,
                'currency':'PKR',
                'amount': r.amount,
                'salary_component': self.account,
                'ref_doctype': self.doctype,
                'ref_docname': self.name
            })
            doc.insert()
