# Copyright (c) 2024, VFG and contributors
# For license information, please see license.txt
import frappe
from frappe.model.document import Document
from datetime import datetime, timedelta

class LateOverTime(Document):
	def validate(self):
		self.month_and_year()
		self.total_ot()

	def month_and_year(self):
		date_str = str(self.date)
		date_obj = datetime.strptime(date_str, "%Y-%m-%d")  
		self.day = date_obj.strftime('%A')
		self.months = date_obj.strftime("%B") 
		self.year1 = date_obj.year
	
	def total_ot(self):
		total_seconds = 0
		total_approved_seconds = 0

		for row in self.details:
			actual_overtime = row.actual_overtime
			approved_overtime = row.approved_overtime

			# Process actual overtime
			if actual_overtime:
				if isinstance(actual_overtime, str):
					time_parts = list(map(int, actual_overtime.split(":")))
					actual_time = timedelta(hours=time_parts[0], minutes=time_parts[1], seconds=time_parts[2])
				elif isinstance(actual_overtime, timedelta):
					actual_time = actual_overtime
				else:
					raise ValueError("Invalid format for actual_overtime")
				total_seconds += actual_time.total_seconds()

			# Process approved overtime
			if approved_overtime:
				if isinstance(approved_overtime, str):
					time_parts1 = list(map(int, approved_overtime.split(":")))
					approved_time = timedelta(hours=time_parts1[0], minutes=time_parts1[1], seconds=time_parts1[2])
				elif isinstance(approved_overtime, timedelta):
					approved_time = approved_overtime
				else:
					raise ValueError("Invalid format for approved_overtime")
				total_approved_seconds += approved_time.total_seconds()

		# Convert total seconds back to timedelta and store as string
		total_overtime = str(timedelta(seconds=total_seconds))
		total_approved_overtime = str(timedelta(seconds=total_approved_seconds))
		self.total_over_time = total_overtime
		self.approved_over_time = total_approved_overtime

	@frappe.whitelist()
	def get_data(self):
		# Correct the SQL query to only include the required argument (self.date)
		rec = frappe.db.sql("""
			select p.employee, p.employee_name, p.designation, c.estimated_late, c.approved_ot1, c.name as child_name, p.name as parent_name 
			from `tabEmployee Attendance` p
			LEFT JOIN `tabEmployee Attendance Table` c ON c.parent=p.name
			where c.date=%s and estimated_late is not null and (c.approved_ot1 = '' or c.approved_ot1 is null or c.approved_ot1 = '00:00:00') 
		""", (self.date, ), as_dict=1)  # Only pass self.date, not self.ot_frequency
		
		if rec:
			self.details = []
			for r in rec:
				allow_ot = frappe.db.get_value('Employee', r.employee, 'is_overtime_allowed')
				if allow_ot == 1 and r.estimated_late:
					# if r.approved_ot1 == "00:00:00":
						self.append("details", {
							"employee": r.employee,
							"actual_overtime": r.estimated_late,
							"approved_overtime": r.estimated_late,
							"employee_name": r.employee_name,
							"designation": r.designation,
							"att_ref": r.parent_name,
							"att_child_ref": r.child_name
						})
			self.save()

	def on_submit(self):
		for r in self.details:
			# Update the `approved_ot1` field in `Employee Attendance Table`
			frappe.db.sql("update `tabEmployee Attendance Table` set approved_ot1=%s where name=%s", 
						  (r.approved_overtime, r.att_child_ref))
			frappe.db.commit()

			# Reload and update the parent document
			doc = frappe.get_doc("Employee Attendance", r.att_ref)
			child_row = doc.getone({"name": r.att_child_ref})
			child_row.approved_ot1 = r.approved_overtime
			doc.save()

			# Reload to verify update
			doc.reload()
			frappe.log_error(f"Updated approved_ot1: {child_row.approved_ot1}")
	
	def on_cancel(self):
		for r in self.details:
			
			frappe.db.sql("update `tabEmployee Attendance Table` set approved_ot1='' where name=%s", 
						  (r.att_child_ref,))
			frappe.db.commit()

			doc = frappe.get_doc("Employee Attendance", r.att_ref)
			child_row = doc.getone({"name": r.att_child_ref})
			child_row.approved_ot1 = ''
			doc.save()


			doc.reload()
			frappe.log_error(f"Updated approved_ot1: {child_row.approved_ot1}")
			frappe.log_error(f"Updated approved_ot1: {child_row.approved_ot1}")


