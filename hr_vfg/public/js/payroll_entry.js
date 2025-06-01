// File: hr_vfg/hr_ventureforce_global/doctype/payroll_entry/payroll_entry.js

frappe.ui.form.on("Payroll Entry", {
    refresh: function(frm) {
        // Add a “Check Attendance” button under the Actions menu
        if (!frm.custom_buttons['Check Attendance']) {
            frm.add_custom_button(__('Check Attendance'), function() {
                frappe.call({
                    method: "hr_vfg.hr_ventureforce_global.custom_events.get_employee_attendance_status",
                    args: {
                        payroll_entry_name: frm.doc.name
                    },
                    freeze: true,
                    freeze_message: __("Checking attendance..."),
                    callback: function(r) {
                        if (r.message && r.message.status === "ok") {
                            frm.reload_doc();
                        } else {
                            frappe.msgprint(__("Could not fetch attendance data."));
                        }
                    }
                });
            }, __("Actions"));
        }
    }
});
