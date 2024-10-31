# Copyright (c) 2024, VFG and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class MealForm(Document):
	def validate(self):
		self.calculate_total_contractor()
		self.calculate_total_employee()
		self.calculate_total_sum()
		self.rate_of_meal()
		self.sum_total_amount()

	def calculate_total_contractor(self):
		total = 0
		for i in self.detail:
			total += i.quantity
		self.total_contractor = total

	
	def calculate_total_employee(self):
		total1 = 0
		for j in self.detail_meal:
			total1 += j.qty
		self.total_employees = total1
	
	def calculate_total_sum(self):
		total_qty = self.total_contractor + self.total_employees
		self.total_qty = total_qty

	def rate_of_meal(self):
		meal_provider = frappe.get_doc("Meal Provider",self.meal_provider)
		meal_data = meal_provider.meal_provider_ct
		for m in meal_data:
			if self.meal_type == m.meal_type:
				self.per_meal_rate = m.rate

	def sum_total_amount(self):
		total_amount = self.per_meal_rate * self.total_qty
		self.total_amount = total_amount


		
