import frappe

def execute(filters=None):
    columns, data = get_column(filters), []
    
    # Fetch data based on filters
    if filters:
        data = get_data(filters)
    
    return columns, data

def get_column(filters):
    columns = [
        {"fieldname": "date", "label": "Date", "fieldtype": "Date", "width": 100},
        {"fieldname": "meal_provider", "label": "Meal Provider", "fieldtype": "Data", "width": 400},
        {"fieldname": "meal_type", "label": "Meal Type", "fieldtype": "Data", "width": 100},
        {"fieldname": "total_contractor", "label": "Total Contractor", "fieldtype": "Float"},
        {"fieldname": "total_employees", "label": "Total Employee", "fieldtype": "Float"},
        {"fieldname": "total_qty", "label": "Qty", "fieldtype": "Float"},
        {"fieldname": "total_amount", "label": "Total Amount", "fieldtype": "Currency"},
    ]
    return columns



def get_data(filters):
    # Debugging to check if filters are being passed correctly
    print(f"Filters received: {filters}")
    
    from_date = filters.get('from_date')
    to_date = filters.get('to_date')
    meal_supplier = filters.get('meal_supplier')  # Dynamically get the meal_supplier filter value
    meal_type = filters.get('meal_type')
    
    # Ensure filters are present and in the correct format
    if from_date and to_date:
        filter_conditions = {
            'date': ['between', [from_date, to_date]],
            'docstatus':1
        }
        
        # If meal_supplier is provided, add it to the filter conditions
        if meal_supplier:
            filter_conditions['meal_provider'] = meal_supplier
        if meal_type:
            filter_conditions['meal_type'] = meal_type
        
        # Print the final filter conditions and SQL query for debugging
        print(f"Filter conditions: {filter_conditions}")
        
        # Fetch data with the dynamically applied filters
        data = frappe.db.get_all('Meal Form', 
                                 fields=['date', 'meal_provider', 'meal_type', 'total_contractor', 'total_employees', 'total_qty','total_amount'], 
                                 filters=filter_conditions,  # Using dynamic filter conditions
                                 order_by='date asc')  # Sorting by date in ascending order
        
        print(f"Data retrieved: {data}")
    else:
        data = []  # Return empty list if filters are not set
    
    return data
