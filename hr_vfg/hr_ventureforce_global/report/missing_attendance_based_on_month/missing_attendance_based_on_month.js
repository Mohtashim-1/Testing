// Copyright (c) 2025, VFG and contributors
// For license information, please see license.txt

frappe.query_reports["Missing Attendance Based on Month"] = {
	filters: [
        {
            fieldname: "month",
            label: __("Month"),
            fieldtype: "Select",
            options: [
                { "value": "1", "label": __("January") },
                { "value": "2", "label": __("February") },
                { "value": "3", "label": __("March") },
                { "value": "4", "label": __("April") },
                { "value": "5", "label": __("May") },
                { "value": "6", "label": __("June") },
                { "value": "7", "label": __("July") },
                { "value": "8", "label": __("August") },
                { "value": "9", "label": __("September") },
                { "value": "10", "label": __("October") },
                { "value": "11", "label": __("November") },
                { "value": "12", "label": __("December") }
            ],
            reqd: 1,
        },
        {
            fieldname: "year",
            label: __("Year"),
            fieldtype: "Int",
            reqd: 1,
            default: new Date().getFullYear(),
        },
    ]
};
