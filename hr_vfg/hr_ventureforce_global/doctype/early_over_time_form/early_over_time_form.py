# Copyright (c) 2024, VFG and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import getdate
import calendar


class EarlyOverTimeForm(Document):
	def before_validate(self):
		"""Extract day, month name, and year from date field"""
		if self.date:
			date_obj = getdate(self.date)
			self.day = date_obj.day
			self.month = calendar.month_name[date_obj.month]  # Full month name like "November"
			self.year = date_obj.year
	@frappe.whitelist()
	def get_data(self):
		rec = frappe.db.sql("""
		SELECT p.employee,p.employee_name,c.shift_start,c.date, c.check_in_1, c.estimate_early, c.approved_eot, c.early_over_time, c.name as child_name, p.name as parent_name FROM `tabEmployee Attendance` p
		LEFT JOIN `tabEmployee Attendance Table` c ON c.parent=p.name
		where c.date=%s and c.estimate_early is not null and
		(c.approved_eot IS NULL OR c.approved_eot = '') 
		""",
		# where p.month=%s and p.year=%s and c.date=%s and c.early_ot is not null and c.early_over_time is not null and c.check_in_1 is not null and c.approved_eot is null and c.early_ot > %s """,
		(self.date),as_dict=1)

# for threshould of ot frequency had been added
#  if len(rec)>0:
			# self.early_over_time_form_ct = []

		if len(rec)>0:
			self.early_over_time_form_ct = []
		
		for r in rec:
			allow_ot = frappe.db.get_value("Employee",r.employee,"is_overtime_allowed")
			if allow_ot == 1:
				self.append("early_over_time_form_ct",{
					"employee":r.employee,
					"employee_name":r.employee_name,
					"check_in_1" : r.check_in_1,
					"date": r.date,
					"early_over_time":r.estimate_early,
					"approved_early_over_time":r.estimate_early,
					# "check":r.early_over_time,
					"att_ref":r.parent_name,
					"att_child_ref":r.child_name
				})
		self.save()

	def on_submit(self):
		for r in self.early_over_time_form_ct:
			# frappe.db.sql("""
			# update `tabEmployee Attendance Table` set approved_early_over_time=%s where name=%s
			# """,(r.approved_early_over_time,r.att_child_ref))

			frappe.db.sql("""
			update `tabEmployee Attendance Table` set approved_eot=%s where name=%s
			""",(r.approved_early_over_time,r.att_child_ref))
			frappe.db.commit()
			doc = frappe.get_doc("Employee Attendance",r.att_ref)
			doc.save()

	
	def on_cancel(self):
		for r in self.early_over_time_form_ct:
			frappe.db.sql("""
			update `tabEmployee Attendance Table` set approved_eot='' where name=%s
			""", (r.att_child_ref))
			frappe.db.commit()
			doc = frappe.get_doc("Employee Attendance", r.att_ref)
			doc.save()
