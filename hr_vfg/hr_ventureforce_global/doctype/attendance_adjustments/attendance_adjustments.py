# Copyright (c) 2024, VFG and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

class AttendanceAdjustments(Document):
    @frappe.whitelist()
    def get_data(self):
        # ensure adjustment_date and adjustment_type are set
        if not self.adjustment_date:
            frappe.throw(_("Please set the Adjustment Date before fetching data."))
        if not self.adjustment_type:
            frappe.throw(_("Please select an Adjustment Type."))

        # build base query
        base_sql = """
            SELECT
                p.employee,
                p.employee_name,
                p.month,
                p.year,
                p.designation,
                c.date,
                c.check_in_1,
                c.check_out_1,
                p.name   AS parent_name,
                c.name   AS child_name
            FROM `tabEmployee Attendance` p
            LEFT JOIN `tabEmployee Attendance Table` c
              ON c.parent = p.name
            WHERE c.date = %s
        """

        # add filter for missing check-ins/outs only if that adjustment_type is selected
        if self.adjustment_type == "Missing Check In/ Check Out":
            base_sql += """
              AND (
                (c.check_in_1 IS NULL AND c.check_out_1 IS NOT NULL)
                OR
                (c.check_in_1 IS NOT NULL AND c.check_out_1 IS NULL)
              )
            """
        # if you instead want only fully existing records for validation,
        # uncomment the following:
        # elif self.adjustment_type == "Validate Check In/ Check Out":
        #     base_sql += " AND c.check_in_1 IS NOT NULL AND c.check_out_1 IS NOT NULL"

        # run query
        recs = frappe.db.sql(base_sql, (self.adjustment_date,), as_dict=1)

        # clear and repopulate child table
        self.set("attendance_adjustments_ct", [])
        for r in recs:
            self.append("attendance_adjustments_ct", {
                "employee":          r.employee,
                "actual_check_in":   r.check_in_1,
                "check_in":          r.check_in_1,
                "actual_check_out":  r.check_out_1,
                "check_out":         r.check_out_1,
                "att_ref":           r.parent_name,
                "att_child_ref":     r.child_name
            })

        # save draft with populated rows
        self.save()

    def on_submit(self):
        for row in self.attendance_adjustments_ct:
            # update via SQL (for speed)...
            frappe.db.sql(
                """
                UPDATE `tabEmployee Attendance Table`
                SET check_in_1=%s, check_out_1=%s
                WHERE name=%s
                """,
                (row.check_in, row.check_out, row.att_child_ref)
            )

            # ...and also update via Document API (to fire all hooks)
            doc = frappe.get_doc("Employee Attendance", row.att_ref)
            child = doc.getone({"name": row.att_child_ref})
            child.check_in_1  = row.check_in
            child.check_out_1 = row.check_out
            doc.save()

        frappe.db.commit()
