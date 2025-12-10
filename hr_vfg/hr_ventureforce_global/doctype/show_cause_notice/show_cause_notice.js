// Copyright (c) 2025, VFG and contributors
// For license information, please see license.txt

frappe.ui.form.on("Show Cause Notice", {
	refresh(frm) {
		// Add custom buttons based on status
		if (frm.doc.status === "Issued" && !frm.doc.employee_response) {
			frm.add_custom_button(__("Record Response"), function() {
				show_response_dialog(frm);
			}, __("Actions"));
		}
		
		if (frm.doc.status === "Responded" && !frm.doc.management_decision) {
			frm.add_custom_button(__("Record Decision"), function() {
				show_decision_dialog(frm);
			}, __("Actions"));
		}
		
		if (frm.doc.status !== "Closed" && frm.doc.status !== "Withdrawn") {
			frm.add_custom_button(__("Close Notice"), function() {
				close_notice(frm);
			}, __("Actions"));
		}
		
		// Set read-only fields based on status
		if (frm.doc.status === "Closed" || frm.doc.status === "Withdrawn") {
			frm.set_read_only();
		}
	},
	
	employee(frm) {
		// Fetch employee details when employee is selected
		if (frm.doc.employee) {
			frappe.db.get_value("Employee", frm.doc.employee, ["employee_name", "designation", "department"], (r) => {
				if (r) {
					frm.set_value("employee_name", r.employee_name);
					frm.set_value("designation", r.designation);
					frm.set_value("department", r.department);
				}
			});
		}
	},
	
	posting_date(frm) {
		// Set default response due date (7 days from posting date)
		if (frm.doc.posting_date && !frm.doc.response_due_date) {
			let due_date = frappe.datetime.add_days(frm.doc.posting_date, 7);
			frm.set_value("response_due_date", due_date);
		}
	},
	
	employee_response(frm) {
		// Auto-update response date when response is entered
		if (frm.doc.employee_response && !frm.doc.response_date) {
			frm.set_value("response_date", frappe.datetime.get_today());
		}
		
		// Auto-update status to "Responded"
		if (frm.doc.employee_response && frm.doc.status !== "Responded") {
			frm.set_value("status", "Responded");
		}
	},
	
	management_decision(frm) {
		// Auto-update decision date when decision is made
		if (frm.doc.management_decision && !frm.doc.decision_date) {
			frm.set_value("decision_date", frappe.datetime.get_today());
		}
		
		// Auto-update decision by
		if (frm.doc.management_decision && !frm.doc.decision_by) {
			frm.set_value("decision_by", frappe.session.user);
		}
		
		// Auto-close if decision is made
		if (frm.doc.management_decision && frm.doc.status !== "Closed") {
			frm.set_value("status", "Closed");
		}
	}
});

function show_response_dialog(frm) {
	let d = new frappe.ui.Dialog({
		title: __("Record Employee Response"),
		fields: [
			{
				fieldtype: "Text Editor",
				fieldname: "response",
				label: __("Response"),
				reqd: 1
			},
			{
				fieldtype: "Date",
				fieldname: "response_date",
				label: __("Response Date"),
				default: frappe.datetime.get_today()
			}
		],
		primary_action_label: __("Submit"),
		primary_action(values) {
			frm.call({
				method: "record_response",
				args: {
					response: values.response,
					response_date: values.response_date
				},
				callback: function(r) {
					if (!r.exc) {
						frm.reload_doc();
						d.hide();
					}
				}
			});
		}
	});
	d.show();
}

function show_decision_dialog(frm) {
	let d = new frappe.ui.Dialog({
		title: __("Record Management Decision"),
		fields: [
			{
				fieldtype: "Select",
				fieldname: "decision",
				label: __("Decision"),
				options: "\nWarning\nSuspension\nTermination\nNo Action\nUnder Review",
				reqd: 1
			},
			{
				fieldtype: "Date",
				fieldname: "decision_date",
				label: __("Decision Date"),
				default: frappe.datetime.get_today()
			},
			{
				fieldtype: "Link",
				fieldname: "decision_by",
				label: __("Decision By"),
				options: "User",
				default: frappe.session.user
			}
		],
		primary_action_label: __("Submit"),
		primary_action(values) {
			frm.set_value("management_decision", values.decision);
			frm.set_value("decision_date", values.decision_date);
			frm.set_value("decision_by", values.decision_by);
			frm.set_value("status", "Closed");
			frm.save().then(() => {
				d.hide();
			});
		}
	});
	d.show();
}

function close_notice(frm) {
	frappe.confirm(
		__("Are you sure you want to close this Show Cause Notice?"),
		function() {
			frm.set_value("status", "Closed");
			frm.save();
		}
	);
}
