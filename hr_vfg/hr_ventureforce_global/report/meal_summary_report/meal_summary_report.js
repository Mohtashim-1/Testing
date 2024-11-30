frappe.query_reports["Meal Summary Report"] = {
    "filters": [
        {
            "fieldname": "from_date",
            "label": __("From Date"),
            "fieldtype": "Date",
            "reqd": 1
        },
        {
            "fieldname": "to_date",
            "label": __("To Date"),
            "fieldtype": "Date",
            "reqd": 1
        },
        {
            "fieldname": "meal_supplier",
            "label": __("Meal Supplier"),
            "fieldtype": "Link",
            "options": "Meal Provider"
        },
    ]
};
