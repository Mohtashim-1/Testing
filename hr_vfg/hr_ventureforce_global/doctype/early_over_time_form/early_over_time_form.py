# Copyright (c) 2024, VFG and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class EarlyOverTimeForm(Document):
	@frappe.whitelist()
	def get_data(self):
		rec = frappe.db.sql("""
		SELECT p.employee,p.employee_name,c.shift_start,c.date,c.early_approved_ot, c.check_in_1, c.early_over_time, c.name as child_name, p.name as parent_name FROM `tabEmployee Attendance` p
		LEFT JOIN `tabEmployee Attendance Table` c ON c.parent=p.name
		where p.month=%s and p.year=%s and c.date=%s and c.early_over_time is not null""",
		(self.month,self.year,self.date),as_dict=1)

		if len(rec)>0:
			self.early_over_time_form_ct = []
		
		for r in rec:
			allow_ot = frappe.db.get_value("Employee",r.employee,"is_overtime_allowed")
			if allow_ot == 1:
				self.append("early_over_time_form_ct",{
					"employee":r.employee,
					"employee_name":r.employee_name,
					"check_in_1" : r.check_in_1,
					"early_over_time":r.early_over_time,
					"approved_early_over_time":r.early_over_time,
					# "check":r.early_over_time,
					"att_ref":r.parent_name,
					"att_child_ref":r.child_name
				})
		self.save()

	def on_submit(self):
		for r in self.early_over_time_form_ct:
			frappe.db.sql("""
			update `tabEmployee Attendance Table` set approved_early_over_time=%s where name=%s
			""",(r.approved_early_over_time,r.att_child_ref))
			frappe.db.commit()
			doc = frappe.get_doc("Employee Attendance",r.att_ref)
			doc.save()