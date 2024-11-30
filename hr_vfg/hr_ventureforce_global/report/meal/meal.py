# Copyright (c) 2024, VFG and contributors
# For license information, please see license.txt

import frappe
from frappe.utils import flt

def execute(filters=None):
    # Columns definition
    columns = [
        {"fieldname": "meal_provider", "label": "Meal Provider", "fieldtype": "Data", "width": 400},
        {"fieldname": "meal_type","label":"Meal Type", "fieldtype": "Data", "width":100},
        {"fieldname": "total_contractor", "label": "Total Contractor", "fieldtype": "Float"},
        {"fieldname": "total_employee", "label": "Total Employee", "fieldtype": "Float"},
        {"fieldname": "total_amount", "label": "Total Amount", "fieldtype": "Currency"},
    ]
    
    # Fetch data
    data = get_meal_summary(filters)

    return columns, data

def get_meal_summary(filters):
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