import frappe
from frappe import _
from frappe.desk.reportview import get_filters_cond, get_match_cond
from frappe.model.document import Document
from frappe.utils import (
	DATE_FORMAT,
	add_days,
	add_to_date,
	cint,
	comma_and,
	date_diff,
	flt,
	getdate,
)
from hrms.payroll.doctype.payroll_entry.payroll_entry import get_existing_salary_slips



@frappe.whitelist()
def get_employee_attendance_status(payroll_entry_name):
    """
    For each row in the 'employees' child table of this Payroll Entry,
    attempt to find an Employee Attendance for that employee for the
    payroll’s month/year. If found AND present_days > 1, mark:
        - child_row.custom_attendance = True
        - child_row.employee_attendance_name = attendance_doc.name
    Otherwise, clear those fields.
    """
    # 1. Load the parent document
    pe = frappe.get_doc("Payroll Entry", payroll_entry_name)

    # 2. Determine month and year from the Payroll Entry’s end_date
    try:
        end_date = getdate(pe.end_date)
    except Exception:
        frappe.throw(_("Cannot parse end_date on Payroll Entry {0}").format(pe.name))

    month_index = end_date.month  # 1–12
    year = end_date.year
    # Convert numeric month to full month name:
    months = ["January","February","March","April","May","June","July","August","September","October","November","December"]
    month_str = months[month_index - 1]
    

    # 3. Loop through each child row in pe.employees
    for row in pe.employees:
        emp = row.employee
        found = False
        

        # 3a. Try to fetch exactly one Employee Attendance record for this employee/month/year
        attendance_list = frappe.get_all(
            "Employee Attendance",
            filters={
                "employee": emp,
                "month": month_str,
                "year": year,
            },
            fields=["name", "present_days"],
            limit=1
        )
        

        if attendance_list:
            att = attendance_list[0]
            # 3b. If present_days > 1, set the flags
            # if att.get("present_days") and flt(att.get("present_days")) > 1:
            if flt(att.get("present_days")) > 1:
                row.custom_attendance = 1
                row.custom_employee_attendance = att.get("name")
                # frappe.log_error= att.get('name')
                found = True
            else:
                row.custom_attendance = 0
                row.custom_employee_attendance = ""

        # 3c. If not found or present_days ≤ 1 → clear those fields
        if not found:
            row.custom_attendance = 0
            row.custom_employee_attendance = ""

    # 4. Save the parent doc (this will persist child‐row changes)
    pe.flags.ignore_mandatory = True   # if any other mandatory child fields exist
    pe.save(ignore_permissions=True)

    return {"status": "ok"}

@frappe.whitelist()
def create_salary_slips(self):
		"""
		Creates salary slip for selected employees if already not created
		"""
		self.check_permission("write")
		employees = [emp.employee for emp in self.employees]
		if employees:
			args = frappe._dict(
				{
					"salary_slip_based_on_timesheet": self.salary_slip_based_on_timesheet,
					"payroll_frequency": self.payroll_frequency,
					"start_date": self.start_date,
					"end_date": self.end_date,
					"company": self.company,
					"posting_date": self.posting_date,
					"deduct_tax_for_unclaimed_employee_benefits": self.deduct_tax_for_unclaimed_employee_benefits,
					"deduct_tax_for_unsubmitted_tax_exemption_proof": self.deduct_tax_for_unsubmitted_tax_exemption_proof,
					"payroll_entry": self.name,
					"exchange_rate": self.exchange_rate,
					"currency": self.currency,
				}
			)
			if len(employees) > 30:
				frappe.enqueue(create_salary_slips_for_employees, timeout=600, employees=employees, args=args)
			else:
				create_salary_slips_for_employees(employees, args, publish_progress=False)
				# since this method is called via frm.call this doc needs to be updated manually
				self.reload()
				
def create_salary_slips_for_employees(employees, args, publish_progress=True):
        salary_slips_exists_for = get_existing_salary_slips(employees, args)
        count = 0
        salary_slips_not_created = []
        for emp in employees:
            if emp not in salary_slips_exists_for:
                e_month  = getdate(args.get("end_date")).month
                year = getdate(args.get("end_date")).year
                month_str  = ["January", "February", "March", "April","May","June","July","August","September","October","November","December"][e_month-1]
                try:
                    employee_att = frappe.get_all("Employee Attendance",
                    filters={"month":month_str,"employee": emp,"year":year},fields=["*"])[0]
                    
                    args.update({
                    "select_month": month_str,
                    "employee_attendance": employee_att.name,
                    # "lates": employee_att.total_lates,
                    # "early_goings": employee_att.early_goings,
                    # "late_sitting_hours": employee_att.late_sitting_hours,
                    # "present_day": employee_att.present_days,
                    # "over_times": employee_att.over_time,
                    # "short_hours": employee_att.short_hours,
                    # "absents": employee_att.total_absents,
                    # "half_days": employee_att.total_half_days,
                    # "late_adjusted_absents":int(employee_att.total_lates)/3,
                    
                    })

                except:
                    frappe.error_log(frappe.get_traceback(),"PAYROLL")
                args.update({"doctype": "Salary Slip", "employee": emp})
                ss = frappe.get_doc(args)
                add_leaves(ss)
                ss.insert()
                count += 1
                if publish_progress:
                    frappe.publish_progress(
                        count * 100 / len(set(employees) - set(salary_slips_exists_for)),
                        title=_("Creating Salary Slips..."),
                    )

            else:
                salary_slips_not_created.append(emp)

        payroll_entry = frappe.get_doc("Payroll Entry", args.payroll_entry)
        payroll_entry.db_set("salary_slips_created", 1)
        payroll_entry.notify_update()

        if salary_slips_not_created:
            frappe.msgprint(
                _(
                    "Salary Slips already exists for employees {}, and will not be processed by this payroll."
                ).format(frappe.bold(", ".join([emp for emp in salary_slips_not_created]))),
                title=_("Message"),
                indicator="orange",
            )



def add_leaves(doc):
			
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