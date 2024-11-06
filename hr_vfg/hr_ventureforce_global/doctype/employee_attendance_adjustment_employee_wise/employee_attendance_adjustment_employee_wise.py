# Copyright (c) 2024, VFG and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class EmployeeAttendanceAdjustmentEmployeeWise(Document):
	@frappe.whitelist()
	def get_data(self):
		# Correct the SQL query to only include the required argument (self.date)
		rec = frappe.db.sql("""
    SELECT p.employee, p.employee_name, p.month, p.year, p.designation, c.date, c.check_in_1, c.check_out_1, 
           p.name AS parent_name, c.name AS child_name
    FROM `tabEmployee Attendance` p
    LEFT JOIN `tabEmployee Attendance Table` c ON c.parent = p.name
    WHERE p.month = %s 
      AND p.year = %s 
      AND p.employee = %s
      AND (
          (c.check_in_1 IS NULL AND c.check_out_1 IS NOT NULL) 
          OR 
          (c.check_in_1 IS NOT NULL AND c.check_out_1 IS NULL)
      )
""", (self.month, self.year, self.employee), as_dict=1)
		
		if rec:
			self.employee_attendance_adjustment_employee_wise_ct = []
			for r in rec:
				# allow_ot = frappe.db.get_value('Employee', r.employee, 'is_overtime_allowed')
				# if allow_ot == 1 and r.estimated_late:
					# if r.approved_ot1 == "00:00:00":
						self.append("employee_attendance_adjustment_employee_wise_ct", {
							# "employee": r.employee,
							"date" : r.date,
							"check_in":r.check_in_1,
							"actual_check_in":r.check_in_1,
							"check_out" :r.check_out_1,
							"actual_check_out":r.check_out_1,
							"update_check_in":1,
							"update_check_in":1,
							"att_ref": r.parent_name,
							"att_child_ref": r.child_name
						})
			self.save()

	def on_submit(self):
		for r in self.employee_attendance_adjustment_employee_wise_ct:
			# Update the `approved_ot1` field in `Employee Attendance Table`
			frappe.db.sql("update `tabEmployee Attendance Table` set check_in_1=%s , check_out_1=%s where name=%s", 
						  (r.check_in, r.check_out, r.att_child_ref))
			frappe.db.commit()

			# Reload and update the parent document
			doc = frappe.get_doc("Employee Attendance", r.att_ref)
			child_row = doc.getone({"name": r.att_child_ref})
			child_row.check_in_1 = r.check_in
			child_row.check_out_1 = r.check_out
			if r.update_check_in == 1 :
				child_row.check_in_updated = 1
			if r.update_check_out == 1:	
				child_row.check_out_updated = 1
			doc.save()

			# Reload to verify update
			doc.reload()
			# frappe.log_error(f"Updated approved_ot1: {child_row.approved_ot1}")
	
	def on_cancel(self):
		for r in self.employee_attendance_adjustment_employee_wise_ct:
			
			frappe.db.sql("update `tabEmployee Attendance Table` set check_in_1='', check_out_1='' where name=%s", 
						  (r.att_child_ref,))
			frappe.db.commit()

			doc = frappe.get_doc("Employee Attendance", r.att_ref)
			child_row = doc.getone({"name": r.att_child_ref})
			child_row.check_in_1 = ''
			child_row.check_out_1 = ''
			doc.save()


			doc.reload()
			# frappe.log_error(f"Updated approved_ot1: {child_row.approved_ot1}")
			# frappe.log_error(f"Updated approved_ot1: {child_row.approved_ot1}")


