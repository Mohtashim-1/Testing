# Copyright (c) 2025, VFG and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import getdate, today, nowdate, get_fullname


class ShowCauseNotice(Document):
	def validate(self):
		"""Validate the Show Cause Notice"""
		if self.date_of_incident and self.posting_date:
			if getdate(self.date_of_incident) > getdate(self.posting_date):
				frappe.throw("Date of Incident cannot be later than Posting Date")
		
		if self.response_due_date and self.posting_date:
			if getdate(self.response_due_date) < getdate(self.posting_date):
				frappe.throw("Response Due Date cannot be earlier than Posting Date")
		
		if self.response_date and self.posting_date:
			if getdate(self.response_date) < getdate(self.posting_date):
				frappe.throw("Response Date cannot be earlier than Posting Date")
		
		if self.decision_date and self.posting_date:
			if getdate(self.decision_date) < getdate(self.posting_date):
				frappe.throw("Decision Date cannot be earlier than Posting Date")
		
		# Auto-update status based on fields
		if not self.status or self.status == "Draft":
			if self.employee_response:
				self.status = "Responded"
			elif self.posting_date and getdate(self.posting_date) <= getdate(today()):
				self.status = "Issued"
	
	def before_save(self):
		"""Set default values before saving"""
		if not self.issued_by:
			self.issued_by = frappe.session.user
		
		if not self.posting_date:
			self.posting_date = today()
	
	def on_submit(self):
		"""Actions when document is submitted"""
		if self.status == "Draft":
			self.status = "Issued"
			self.save(ignore_permissions=True)
		
		# Send notification to employee if configured
		self.send_notification_to_employee()
	
	def on_cancel(self):
		"""Actions when document is cancelled"""
		if self.status not in ["Closed", "Withdrawn"]:
			frappe.throw("Only Closed or Withdrawn notices can be cancelled")
	
	def send_notification_to_employee(self):
		"""Send notification to employee about the show cause notice"""
		if self.employee:
			employee_doc = frappe.get_doc("Employee", self.employee)
			if employee_doc.user_id:
				try:
					frappe.sendmail(
						recipients=[employee_doc.user_id],
						subject=f"Show Cause Notice - {self.subject}",
						message=f"""
						Dear {employee_doc.employee_name},
						
						A Show Cause Notice has been issued to you.
						
						Subject: {self.subject}
						Date of Incident: {self.date_of_incident}
						Response Due Date: {self.response_due_date or 'Not specified'}
						
						Please review the notice and provide your response.
						
						Thank you.
						"""
					)
				except Exception as e:
					frappe.log_error(f"Error sending notification for Show Cause Notice {self.name}: {str(e)}")
	
	@frappe.whitelist()
	def update_status(self, status):
		"""Update the status of the show cause notice"""
		if status not in ["Draft", "Issued", "Responded", "Closed", "Withdrawn"]:
			frappe.throw("Invalid status")
		
		self.status = status
		self.save(ignore_permissions=True)
		return self.status
	
	@frappe.whitelist()
	def record_response(self, response, response_date=None):
		"""Record employee response"""
		if not response:
			frappe.throw("Response cannot be empty")
		
		self.employee_response = response
		self.response_date = response_date or today()
		self.status = "Responded"
		self.save(ignore_permissions=True)
		return self.name
