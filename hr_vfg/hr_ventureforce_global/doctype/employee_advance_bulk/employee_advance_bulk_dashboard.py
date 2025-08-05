from frappe import _


def get_data():
	return {
		"fieldname": "custom_employee_advance_bulk",
		"transactions": [
			{"label": _("Employee Advances"), "items": ["Employee Advance"]},
			{"label": _("Payments"), "items": ["Payment Entry"]},
		],
	} 