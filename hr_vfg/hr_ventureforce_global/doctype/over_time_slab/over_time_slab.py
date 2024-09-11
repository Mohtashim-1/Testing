import frappe
from frappe.model.document import Document
from datetime import datetime, timedelta


class OverTimeSlab(Document):
    def validate(self):
        self.calculate_total_hours()

    def calculate_total_hours(self):
        FMT = '%H:%M:%S'
        for item in self.over_time_slab_ct:
            from_time_str = item.from_time
            to_time_str = item.to_time

            try:
                # Parse the time strings into datetime objects
                from_time = datetime.strptime(from_time_str, FMT)
                to_time = datetime.strptime(to_time_str, FMT)

                # Handle the case where to_time is less than from_time (overnight shifts)
                if to_time < from_time:
                    to_time += timedelta(days=1)

                # Calculate the time difference
                time_difference = to_time - from_time

                # Convert time difference to HH:MM:SS format
                total_seconds = int(time_difference.total_seconds())
                hours, remainder = divmod(total_seconds, 3600)
                minutes, seconds = divmod(remainder, 60)
                item.total_hours = f"{hours:02}:{minutes:02}:{seconds:02}"

                # Debug print
                print(f"Item {item.idx} - from_time: {from_time_str}, to_time: {to_time_str}, total_hours: {item.total_hours}")

            except Exception as e:
                frappe.throw(f"Error calculating total hours for item {item.idx}: {str(e)}")



