frappe.query_reports["Attendance Register"] = {
    "filters": [
        {
            "fieldname": "month",
            "label": __("Month"),
            "fieldtype": "Select",
            "options": [
                { "value": "January", "label": __("January") },
                { "value": "February", "label": __("February") },
                { "value": "March", "label": __("March") },
                { "value": "April", "label": __("April") },
                { "value": "May", "label": __("May") },
                { "value": "June", "label": __("June") },
                { "value": "July", "label": __("July") },
                { "value": "August", "label": __("August") },
                { "value": "September", "label": __("September") },
                { "value": "October", "label": __("October") },
                { "value": "November", "label": __("November") },
                { "value": "December", "label": __("December") }
            ],
            "default": frappe.datetime.str_to_user(frappe.datetime.get_today()).split(' ')[0],  // default current month
            "reqd": 0
        },
        {
            "fieldname": "year",
            "label": __("Year"),
            "fieldtype": "Int",
            "default": frappe.datetime.str_to_user(frappe.datetime.get_today()).split(' ')[2],  // default current year
            "reqd": 0
        },
        {
            "fieldname": "employee",
            "label": __("Employee"),
            "fieldtype": "Link",
            "options": "Employee",
            "reqd": 0
        }
    ]
};
