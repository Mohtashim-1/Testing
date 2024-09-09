# Copyright (c) 2024, VFG and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class LateOverTimeEmployeeWise(Document):
	@frappe.whitelist()
	def get_data(self):
		rec = frappe.db.sql("""
			select p.employee, p.employee_name, p.designation,c.date, c.late_sitting, c.approved_ot1, c.name as child_name, p.name as parent_name 
			from `tabEmployee Attendance` p
			LEFT JOIN `tabEmployee Attendance Table` c ON c.parent=p.name
			where p.month = %s and p.year = %s and p.employee=%s and c.late_sitting > %s and (c.approved_ot1 = '' or c.approved_ot1 is null) 
		""", (self.month, self.year, self.employee, self.ot_threshold), as_dict=1)  # Only pass self.date, not self.ot_frequency
		
		if rec:
			self.details = []
			for r in rec:
				allow_ot = frappe.db.get_value('Employee', r.employee, 'is_overtime_allowed')
				if allow_ot == 1 and r.late_sitting:
					# if r.approved_ot1 == "00:00:00":
						self.append("late_over_time_employee_wise_ct", {
							"employee": r.employee,
							"date": r.date,

							"actual_overtime": r.late_sitting,
							"approved_overtime": r.late_sitting,
							"employee_name": r.employee_name,
							# "designation": r.designation,
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

