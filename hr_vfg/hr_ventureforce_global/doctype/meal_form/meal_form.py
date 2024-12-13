# Copyright (c) 2024, VFG and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from datetime import datetime


class MealForm(Document):
	def validate(self):
		# self.calculate_total_contractor()
		# self.calculate_total_employee()
		# self.calculate_total_sum()
		# self.rate_of_meal()
		# self.sum_total_amount()
		self.contract_rate_base_on_category()
		self.employee_rate_base_on_category()
		self.total_qty_and_total_amount()

	
	def contract_rate_base_on_category(self):
		meal_provider = frappe.get_doc("Meal Provider", self.meal_provider)
		meal_data = meal_provider.meal_provider_ct

		date = datetime.strptime(self.date, "%Y-%m-%d").date() if isinstance(self.date, str) else self.date

		for m in meal_data:
			for j in self.detail:
				from_date = datetime.strptime(m.from_date, "%Y-%m-%d").date() if isinstance(m.from_date, str) else m.from_date
				to_date = datetime.strptime(m.to_date, "%Y-%m-%d").date() if isinstance(m.to_date, str) else m.to_date

				if from_date <= date <= to_date:
					if m.category == j.meal_category:
						if m.meal_type == self.meal_type:
							j.rate = m.rate
							j.amount = j.rate * j.quantity
				else:
					j.rate = 0
					j.amount = 0

	def employee_rate_base_on_category(self):
		meal_provider = frappe.get_doc("Meal Provider", self.meal_provider)
		meal_data = meal_provider.meal_provider_ct

		date = datetime.strptime(self.date, "%Y-%m-%d").date() if isinstance(self.date, str) else self.date

		for m in meal_data:
			for j in self.detail_meal:
				from_date = datetime.strptime(m.from_date, "%Y-%m-%d").date() if isinstance(m.from_date, str) else m.from_date
				to_date = datetime.strptime(m.to_date, "%Y-%m-%d").date() if isinstance(m.to_date, str) else m.to_date

				if from_date <= date <= to_date:
					if m.category == j.meal_category:
						if m.meal_type == self.meal_type:
							j.rate = m.rate
							j.amount = j.rate * j.qty
				else:
					j.rate = 0
					j.amount = 0
	
	def total_qty_and_total_amount(self):
		total_qty = 0
		total_amount = 0
		total_qty1 = 0
		total_amount1 = 0
		for j in self.detail:
			total_qty += j.quantity
			total_amount += j.amount
		for i in self.detail_meal:
			total_qty1 += i.qty
			total_amount1 += i.amount
		# self.total_contractor = total_qty
		# self.total_contract_amount = total_amount
		# self.total_employees = total_qty1
		# self.total_employee_amount = total_amount1
		# self.total_qty = self.total_contractor + self.total_employees 
		# self.total_amount = self.total_contract_amount + self.total_employee_amount
		self.db_set('total_contractor', total_qty)
		self.db_set('total_contract_amount', total_amount)
		self.db_set('total_employees', total_qty1)
		self.db_set('total_employee_amount', total_amount1)
		self.db_set('total_qty', total_qty + total_qty1)
		self.db_set('total_amount', total_amount + total_amount1)
				



		
