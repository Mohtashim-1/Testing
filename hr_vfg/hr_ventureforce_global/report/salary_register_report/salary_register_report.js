// Copyright (c) 2025, VFG and contributors
// For license information, please see license.txt

frappe.query_reports["Salary Register Report"] = {
	"filters": [

		{
            "fieldname": "month",
            "label": __("Month"),
            "fieldtype": "Select",
            "options": "\nJanuary\nFebruary\nMarch\nApril\nMay\nJune\nJuly\nAugust\nSeptember\nOctober\nNovember\nDecember",
            "default": [
                "January", "February", "March", "April", "May", "June",
                "July", "August", "September", "October", "November", "December"
            ][frappe.datetime.str_to_obj(frappe.datetime.get_today()).getMonth()],
        },
        {
            "fieldname": "year",
            "label": __("Year"),
            "fieldtype": "Link",
            "options": "Year",
        },
        {
            "fieldname": "employee",
            "label": __("Employee"),
            "fieldtype": "Link",
            "options": "Employee"
        },
        {
            "fieldname": "department",
            "label": __("Department"),
            "fieldtype": "Link",
            "options": "Department"
        }
	],
	// "onload": function () {
    //     frappe.call({
    //         method: "hrms.hr.report.monthly_attendance_sheet.monthly_attendance_sheet.get_attendance_years",
    //         callback: function (r) {
    //             if (r.message) {
    //                 let year_filter = frappe.query_report.get_filter('year');
                    
    //                 // Update options for the year filter
    //                 year_filter.df.options = r.message + "\n2020";
                    
    //                 // Refresh the filter UI to apply changes
    //                 year_filter.refresh();

    //                 // Set the default value
    //                 const default_year = r.message.split("\n")[0];
    //                 year_filter.set_input(default_year);
    //             }
    //         }
    //     });
    // }
};
