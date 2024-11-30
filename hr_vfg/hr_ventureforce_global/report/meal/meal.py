import frappe
from frappe.utils import flt

def execute(filters=None):
    # Columns definition
    columns = [
        {"fieldname": "meal_provider", "label": "Meal Provider", "fieldtype": "Data", "width": 400},
        {"fieldname": "meal_type", "label": "Meal Type", "fieldtype": "Data", "width": 100},
        {"fieldname": "total_contractor", "label": "Total Contractor", "fieldtype": "Float"},
        {"fieldname": "total_employee", "label": "Total Employee", "fieldtype": "Float"},
        {"fieldname": "total_amount", "label": "Total Amount", "fieldtype": "Currency"},
    ]

    # Fetch data
    detailed_data = get_meal_details(filters)
    summary_data = get_meal_summary(filters)

    # Add summary heading
    summary_heading = {
        "meal_provider": "Summary",
        "meal_type": "",
        "total_contractor": "",
        "total_employee": "",
        "total_amount": "",
        "bold":1,
    }

    # Combine detailed data, summary heading, and summary data
    data = detailed_data + [summary_heading] + [
        {
            "meal_provider": summary["meal_provider"],
            "meal_type": "",  # Leave meal type empty for summary rows
            "total_contractor": summary["total_contractor"],
            "total_employee": summary["total_employee"],
            "total_amount": summary["total_amount"],
        }
        for summary in summary_data
    ]

    return columns, data


def get_meal_details(filters):
    """Fetch detailed data grouped by meal_provider and meal_type."""
    conditions = ""
    if filters.get("from_date") and filters.get("to_date"):
        conditions += "WHERE mf.date BETWEEN %(from_date)s AND %(to_date)s"
    
    query = f"""
        SELECT 
            mf.meal_provider AS meal_provider,
            mf.meal_type AS meal_type,
            SUM(COALESCE(mf.total_contractor, 0)) AS total_contractor,
            SUM(COALESCE(mf.total_employees, 0)) AS total_employee,
            SUM(COALESCE(mf.total_amount, 0)) AS total_amount
        FROM 
            `tabMeal Form` AS mf
        {conditions}
        GROUP BY 
            mf.meal_provider, mf.meal_type
    """
    return frappe.db.sql(query, filters, as_dict=True)


def get_meal_summary(filters):
    """Fetch summary totals grouped only by meal_provider."""
    conditions = ""
    if filters.get("from_date") and filters.get("to_date"):
        conditions += "WHERE mf.date BETWEEN %(from_date)s AND %(to_date)s"
    
    query = f"""
        SELECT 
            mf.meal_provider AS meal_provider,
            SUM(COALESCE(mf.total_contractor, 0)) AS total_contractor,
            SUM(COALESCE(mf.total_employees, 0)) AS total_employee,
            SUM(COALESCE(mf.total_amount, 0)) AS total_amount
        FROM 
            `tabMeal Form` AS mf
        {conditions}
        GROUP BY 
            mf.meal_provider
    """
    return frappe.db.sql(query, filters, as_dict=True)
