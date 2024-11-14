# Copyright (c) 2024, VFG and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class AttendanceAdjustments(Document):
    @frappe.whitelist()
    def get_data(self):
        # Check if adjustment_date is set before running the query
        if not self.adjustment_date:
            frappe.throw("Please set the Adjustment Date before fetching data.")

        # Correct the SQL query to only include the required argument (self.adjustment_date)
        rec = frappe.db.sql("""
            SELECT p.employee, p.employee_name, p.month, p.year, p.designation, c.date, c.check_in_1, c.check_out_1, 
                p.name AS parent_name, c.name AS child_name
            FROM `tabEmployee Attendance` p
            LEFT JOIN `tabEmployee Attendance Table` c ON c.parent = p.name
            WHERE c.date = %s
            AND (
			(c.check_in_1 IS NULL AND c.check_out_1 IS NOT NULL) 
			OR 
			(c.check_in_1 IS NOT NULL AND c.check_out_1 IS NULL)
      )
        """,(self.adjustment_date,), as_dict=1)
        
        if rec:
            self.attendance_adjustments_ct = []  # Ensure the list is cleared before appending
            for r in rec:
                # Optionally, uncomment this if needed for overtime check
                # allow_ot = frappe.db.get_value('Employee', r.employee, 'is_overtime_allowed')
                # if allow_ot == 1:
                self.append("attendance_adjustments_ct", {
                    "employee": r.employee,
                    # Uncomment the date field if needed
                    # "date": r.date,
                    "check_in": r.check_in_1,
                    "actual_check_in": r.check_in_1,
                    "check_out": r.check_out_1,
                    "actual_check_out": r.check_out_1,
                    "att_ref": r.parent_name,
                    "att_child_ref": r.child_name
                })
            self.save()
            
    def on_submit(self):
        for r in self.attendance_adjustments_ct:
            frappe.db.sql("update `tabEmployee Attendance Table` set check_in_1=%s , check_out_1=%s where name=%s", 
			(r.check_in, r.check_out, r.att_child_ref))
            frappe.db.commit()
            doc = frappe.get_doc("Employee Attendance", r.att_ref)
            child_row = doc.getone({"name": r.att_child_ref})
            child_row.check_in_1 = r.check_in
            child_row.check_out_1 = r.check_out
            # if r.update_check_in == 1 :
            #         child_row.check_in_updated = 1
            # if r.update_check_out == 1:	
            #     child_row.check_out_updated = 1
            doc.save()
            doc.reload()