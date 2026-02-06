frappe.query_reports["Salary Sheet"] = {
    "filters": [
        {
            "fieldname": "month",
            "label": __("Month"),
            "fieldtype": "Select",
            "options": "\nJanuary\nFebruary\nMarch\nApril\nMay\nJune\nJuly\nAugust\nSeptember\nOctober\nNovember\nDecember",
            "default": [
                "January", "February", "March", "April", "May", "June",
                "July", "August", "September", "October", "November", "December"
            ][frappe.datetime.str_to_obj(frappe.datetime.get_today()).getMonth()],
        },
        {
            "fieldname": "year",
            "label": __("Year"),
            "fieldtype": "Link",
            "options": "Year",
        },
        {
            "fieldname": "employee",
            "label": __("Employee"),
            "fieldtype": "Link",
            "options": "Employee"
        },
        {
            "fieldname": "department",
            "label": __("Department"),
            "fieldtype": "Link",
            "options": "Department"
        }
    ],

    "onload": function () {
        // Ensure Year records exist dynamically in Year DocType
        frappe.call({
            method: "hr_vfg.hr_ventureforce_global.report.salary_sheet.salary_sheet.ensure_year_records",
            callback: function (r) {
                if (r.message && r.message.success) {
                    // Year records are now ensured
                    // Link field will automatically show all Year records
                    
                    // Set default to current year
                    let year_filter = frappe.query_report.get_filter('year');
                    if (year_filter) {
                        const current_year = new Date().getFullYear().toString();
                        year_filter.set_input(current_year);
                    }
                }
            },
            error: function(err) {
                console.log("Error ensuring year records:", err);
            }
        });
    }
};
