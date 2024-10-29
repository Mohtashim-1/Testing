// Copyright (c) 2024, VFG and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Monthly Attendance Summary"] = {
	"filters": [
		{
			"fieldname":"employee",
			"label": __("Employee"),
			"fieldtype": "Link",
			"options": "Employee",
			
		},
		{
			"fieldname":"month",
			"label": __("Month"),
			"fieldtype": "Select",
			"options":"\nJanuary\nFebruary\nMarch\nApril\nMay\nJune\nJuly\nAugust\nSeptember\nOctober\nNovember\nDecember",
			"reqd": 1
		},
		{
			"fieldname":"year",
			"label": __("Year"),
			"fieldtype": "Select",
			"options":"\n2022\n2023\n2024\n2025\n2026\n2027\n2028\n2029\n2030\n2031\n2032\n2033",
			"reqd": 1
		},
		// {
		// 	"fieldname":"from_date",
		// 	"label": __("From Date"),
		// 	"fieldtype": "Date",
		// 	"default": frappe.datetime.add_months(frappe.datetime.get_today(), -0.5),
		// 	"reqd": 1,
		// 	"width": "60px"
		// },
		// {
		// 	"fieldname":"to_date",
		// 	"label": __("To Date"),
		// 	"fieldtype": "Date",
		// 	"default": frappe.datetime.get_today(),
		// 	"reqd": 1,
		// 	"width": "60px"
		// },
	]
};
