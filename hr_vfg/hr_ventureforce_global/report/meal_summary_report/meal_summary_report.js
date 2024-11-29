// Copyright (c) 2024, VFG and contributors
// For license information, please see license.txt

frappe.query_reports["Meal Summary Report"] = {
	"filters": [
		{
			"fieldname": "from_date",
			"label": __("From Date"),
			"fieldtype": "Date",
			"reqd": 1,
			"default": frappe.defaults.get_default("getFirstDateOfCurrentMonth")
		},
		{
			"fieldname": "to_date",
			"label": __("To Date"),
			"fieldtype": "Date",
			"reqd": 1,
			"default": frappe.defaults.get_default("getFirstDateOfCurrentMonth")
		},
		{
			"fieldname": "meal_supplier",
			"label": __("Meal Supplier"),
			"fieldtype": "Link",
			"options":"Meal Provider"
			// "reqd": 1,
		},

	]
};

function getFirstDateOfCurrentMonth() {
    var today = new Date();
    var firstDay = new Date(today.getFullYear(), today.getMonth(), 1);  // Set the day to 1 to get the first day of the month

    // Format the date to "dd-mm-yyyy"
    var day = String(firstDay.getDate()).padStart(2, '0');
    var month = String(firstDay.getMonth() + 1).padStart(2, '0'); // Months are zero-indexed
    var year = firstDay.getFullYear();

    return `${day}-${month}-${year}`;
}