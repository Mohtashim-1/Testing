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
            "fieldname": "employee",
            "label": __("Employee Name"),
            "fieldtype": "Link",
            "options": "Employee",
            "reqd": 0
        },
        {
            "fieldname": "attendance_date",
            "label": __("Date"),
            "fieldtype": "Date",
            "reqd": 0
        }
	]
};
