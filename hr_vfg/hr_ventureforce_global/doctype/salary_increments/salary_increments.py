# Copyright (c) 2023, VFG and contributors
# For license information, please see license.txt

# import frappe
from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from datetime import datetime, date

class SalaryIncrements(Document):
	pass
	def validate(self):
		for i in self.salary_increment_table:
			prev_salary = float(i.previous_salary or 0)
			inc_amount = float(i.increment_amount or 0)
			inc_per = float(i.increment_per or 0)

			# Debugging: Print values to check if they are being fetched correctly
			# frappe.msgprint(f"Employee: {i.employee}, Previous Salary: {prev_salary}, Increment %: {inc_per}, Increment Amount: {inc_amount}")

			# Calculate increment amount if percentage is provided but amount is missing
			if inc_per > 0 and inc_amount == 0:
				i.increment_amount = (prev_salary * inc_per) / 100
				# frappe.msgprint(f"Calculated Increment Amount: {i.increment_amount}")  # Debugging

			# Calculate increment percentage if amount is provided but percentage is missing
			elif inc_amount > 0 and inc_per == 0:
				i.increment_per = (inc_amount / prev_salary) * 100
				# frappe.msgprint(f"Calculated Increment Percentage: {i.increment_per}")  # Debugging

			# Compute after increment salary
			i.after_increment_salary = prev_salary + i.increment_amount
			# frappe.msgprint(f"Updated After Increment Salary: {i.after_increment_salary}")  # Debugging

			# Ensure the values persist in the database
			i.db_set("increment_amount", i.increment_amount)
			i.db_set("increment_per", i.increment_per)
			i.db_set("after_increment_salary", i.after_increment_salary)


      		# if i.salary_date <= i.previous_salary_date:
		# if len(self.salary_increment_table) == 0:
		# 	incs = frappe.get_all("Salary Increment",filters={"employee":self.employee,"name":["!=",self.name]},fields=["*"])
		# 	for doc in incs:
		# 		self.append("salary_increment_table",{
		# 			"increment_date":doc.increment_date,
		# 			"increment_type":doc.increment_type,
		# 			"previous_salary":doc.salary,
		# 			"increment_per":doc.increment_percentage,
		# 			"increment_amount":doc.increment_amount,
		# 			"after_increment_salary":doc.after_increment_salary
		# 		})
		for d in self.salary_increment_table:
			for inn_d in self.salary_increment_table:
				if d.employee == inn_d.employee and d.name != inn_d.name:
					frappe.throw("Employee {0} selected multiple times".format(d.employee))
	@frappe.whitelist()
	def get_employee(self,employee=None,department=None,designation=None,branch=None):
		increment_amount = 0
		total_after_increment = 0
		self.salary_increment_table = []
		filters = {"status":"Active"}
		if employee:
			filters["name"] = employee
		else:
			if department:
				filters["department"] = department
			if designation:
				filters["designation"] = designation
			if branch:
				filters["branch"] = branch
		employees = frappe.db.get_all("Employee",filters=filters,fields=["name"])
		for row in employees:
			prev = frappe.db.get_value("Salary Structure Assignment",{"docstatus":1,"employee":row.name},"base") or 0
			if prev == 0:
				frappe.msgprint(f"Skipping employee {row.employee} as they have no previous salary.", alert=True)
				continue
			if self.increment_percentage > 0 and self.increment_amount == 0:
				self.append("salary_increment_table",{
					    "employee":row.name,
						"increment_date":self.increment_date,
						"increment_type":self.increment_type,
						"previous_salary":prev,
						"increment_per":self.increment_percentage,
						"increment_amount":prev*(self.increment_percentage/100),
						"after_increment_salary":prev + (prev*(self.increment_percentage/100))
					})
			if self.increment_amount > 0 and self.increment_percentage == 0:
				if prev == 0:
					frappe.msgprint(f"Warning: Employee {row.name} has no previous salary. Increment percentage will be set to 0.")
				self.append("salary_increment_table", {
					"employee": row.name,
					"increment_date": self.increment_date,
					"increment_type": self.increment_type,
					"previous_salary": prev,
					"increment_per": (self.increment_amount / prev) * 100 if prev > 0 else 0,
					"increment_amount": self.increment_amount,
					"after_increment_salary": prev + self.increment_amount
				})


			else:
				frappe.msgprint("Please select only one, either Increment Percentage or Increment Amount")
		for row in self.salary_increment_table:
			increment_amount += row.increment_amount
			total_after_increment += row.after_increment_salary
		self.total_increment = increment_amount
		self.total_salary_after_increment = total_after_increment	
		self.save()
  
	def on_submit(self):
		for d in self.salary_increment_table:
			emp_doc = frappe.get_doc("Employee",d.employee)
			emp_doc.update({
				"salary":d.after_increment_salary
			})
			emp_doc.save()
			ssa_value = frappe.db.get_value("Salary Structure Assignment",{"employee":d.employee,"docstatus":1},"name")
			if ssa_value:
				ssa_doc = frappe.get_doc("Salary Structure Assignment",ssa_value)
				new_doc = frappe.copy_doc(ssa_doc)
				new_doc.update({
					"from_date":self.increment_date,
					"base":d.after_increment_salary
				})
				new_doc.save()
				new_doc.submit()