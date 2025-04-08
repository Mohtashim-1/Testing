// Copyright (c) 2025, VFG and contributors
// For license information, please see license.txt

frappe.query_reports["Log Sheet"] = {
	"filters": [
		{
            "fieldname": "biometric_id",
            "label": __("Biometric ID"),
            "fieldtype": "Data",
            "reqd": 0
        },
        {
            "fieldname": "employee_name",
            "label": __("Employee Name"),
            "fieldtype": "Link",
            "options": "Employee",
            "reqd": 0
        },
        {
            "fieldname": "from_date",
            "label": __("From Date"),
            "fieldtype": "Date",
            "reqd": 0,
            "default": frappe.datetime.add_days(frappe.datetime.get_today(), -7) // Default to last 7 days
        },
        {
            "fieldname": "to_date",
            "label": __("To Date"),
            "fieldtype": "Date",
            "reqd": 0,
            "default": frappe.datetime.get_today() // Default to today
        }
	]
};
