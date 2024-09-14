import frappe
from frappe.model.document import Document
from datetime import datetime, time as datetime_time, timedelta


class OverTimeSlab(Document):
    def validate(self):
        self.calculate_total_hours()
        self.per_hours_calculation()

    def calculate_total_hours(self):
        FMT = '%H:%M:%S'
        
        for item in self.over_time_slab_ct:
            s1 = item.from_time
            s2 = item.to_time
            
            from_time = datetime.strptime(s1, FMT)
            to_time = datetime.strptime(s2, FMT)
            
            if from_time > to_time:
                to_time += timedelta(days=1)
            
            item.total_hours = to_time - from_time
    
    def per_hours_calculation(self):
        for rate in self.over_time_slab_ct:
            if rate.formula:
                if rate.formula == "Employee's Overtime Rate":
                    rate.per_hour_calculation = 1.0
                if rate.formula == "Employee's Overtime Rate x 1.5":
                    rate.per_hour_calculation = 1.5
                if rate.formula == "Employee's Overtime Rate x 2":
                    rate.per_hour_calculation = 2.0
                if rate.formula == "Employee Full Day":
                    rate.per_hour_calculation = self.standard_workinghours
                if rate.formula == "Employee Full Day x 2":
                    rate.per_hour_calculation = float(self.standard_workinghours) * 2
                # frappe.msgprint('123')


