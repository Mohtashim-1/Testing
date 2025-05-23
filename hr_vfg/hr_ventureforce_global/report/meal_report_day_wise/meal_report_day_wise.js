frappe.query_reports["Meal Report Day Wise"] = {
    "filters": [
        {
            "fieldname": "from_date",
            "label": __("From Date"),
            "fieldtype": "Date",
            "default": frappe.datetime.add_months(frappe.datetime.get_today(), -1),
            "reqd": 1
        },
        {
            "fieldname": "to_date",
            "label": __("To Date"),
            "fieldtype": "Date",
            "default": frappe.datetime.get_today(),
            "reqd": 1  
		},
        {
            "fieldname": "meal_supplier",
            "label": __("Meal Supplier"),
            "fieldtype": "Link",
            "options": "Meal Provider"
        },
        {
            "fieldname": "meal_type",
            "label": __("Meal Type"),
            "fieldtype": "Link",
            "options": "Meal Type"
        },
    ]
}