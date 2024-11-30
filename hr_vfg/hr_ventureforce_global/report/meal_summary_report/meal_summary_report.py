import frappe
from frappe import _
def execute(filters=None):
	columns, data = get_column(filters=filters), get_data(filters=filters)
	return columns, data

def get_column(filters=None):
	return[
		{
			"label":_("From Date"),
			"fieldname": "from_date",
			"fieldtype":"Date",
			"width":100
		},
		{
			"label":_("To Date"),
			"fieldname": "to_date",
			"fieldtype":"Date",
			"width":100
		}
	]
