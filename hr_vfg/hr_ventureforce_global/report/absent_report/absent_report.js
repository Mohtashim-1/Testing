// Copyright (c) 2025, VFG and contributors
// For license information, please see license.txt

frappe.query_reports["Absent Report"] = {
	"filters": [
		{
            fieldname: "employee",
            label: "Employee",
            fieldtype: "Link",
			options:"Employee"
        },
		{
            fieldname: "year",
            label: "Year",
            fieldtype: "Link",
			options:"Year"
        },
        {
            fieldname: "month",
            label: "Month",
            fieldtype: "Select",
            options: "\nJanuary\nFebruary\nMarch\nApril\nMay\nJune\nJuly\nAugust\nSeptember\nOctober\nNovember\nDecember"
        },
        {
            fieldname: "department",
            label: "Department",
            fieldtype: "Link",
            options: "Department"
        },
		{
            fieldname: "designation",
            label: "Designation",
            fieldtype: "Link",
            options: "Designation"
        }

	]
};
