import frappe
from frappe.model.document import Document
from datetime import datetime, time as datetime_time, timedelta


class OverTimeSlab(Document):
    def validate(self):
        self.calculate_total_hours()

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



