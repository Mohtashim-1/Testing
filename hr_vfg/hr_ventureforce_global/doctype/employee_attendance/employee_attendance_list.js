frappe.listview_settings['Employee Attendance'] = {
	colwidths: {"subject": 6},
	onload: function(listview) {
	
		var methods = "hr_vfg.hr_ventureforce_global.doctype.employee_attendance.attendance_connector.get_attendance_long";
        
				listview.page.add_menu_item(__("Get Attendance"), function() {
					var dialog = new frappe.ui.Dialog({
						title: __('Add Follow Up'),
						fields: [
				
							{ fieldtype: 'Date', reqd:1, fieldname: 'from_date', label: __("From Date"),default: frappe.datetime.add_months(frappe.datetime.get_today(), -1), },
							{ fieldtype: 'Column Break' },
							{ fieldtype: 'Date',reqd:1, fieldname: 'to_date', label: __("To Date"), default: frappe.datetime.get_today(),},
							{ fieldtype: 'Section Break' },
				
							{ fieldtype: 'Link', fieldname: 'employee', label: __("Employee"),options:"Employee" },
							{ fieldtype: 'Link', fieldname: 'department', label: __("Department"),options:"Department" },
				
				
						],
						primary_action: function () {
							var args = dialog.get_values();
							console.log(args)
							listview.call_for_selected_items(methods, args);
							dialog.hide()
						},
						primary_action_label: __("Submit")
					})
					dialog.show()
			
		});

		//var methods = "hr_vfg.hr_ventureforce_global.doctype.attendance_logs.attendance_logs.sync_attendance";
       
		// listview.page.add_menu_item(__("Generate Attendance"), function() {
		// 	listview.call_for_selected_items(method, {"status": "Open"});
		// });


		// 		listview.page.add_menu_item(__("Sync Manual Attendance"), function() {
		// 			var dialog = new frappe.ui.Dialog({
		// 				title: __('Filters'),
		// 				fields: [
				
		// 					{ fieldtype: 'Date', reqd:1, fieldname: 'from_date', label: __("From Date") },
		// 					{ fieldtype: 'Column Break' },
		// 					{ fieldtype: 'Date',reqd:1, fieldname: 'to_date', label: __("To Date") },
		// 					{ fieldtype: 'Section Break' },
				
		// 					{ fieldtype: 'Link', fieldname: 'employee', label: __("Employee"),options:"Employee" },
		// 					{ fieldtype: 'Link', fieldname: 'department', label: __("Department"),options:"Department" },
				
				
		// 				],
		// 				primary_action: function () {
		// 					var args = dialog.get_values();
		// 					console.log(args)
		// 					listview.call_for_selected_items(methods, args);
		// 					dialog.hide()
		// 				},
		// 				primary_action_label: __("Submit")
		// 			})
		// 			dialog.show()
			
		// });


	
}
}



frappe.listview_settings['Employee Attendance'] = {
    onload: function(listview) {
        listview.page.add_action_item(__('Refresh'), function() {
            // Get selected documents
            const selected_docs = listview.get_checked_items();
            if (!selected_docs.length) {
                frappe.msgprint(__('Please select at least one document.'));
                return;
            }

            // Confirm action
            frappe.confirm(
                __('Are you sure you want to refresh the table for selected records?'),
                function() {
                    frappe.call({
                        method: "hr_vfg.hr_ventureforce_global.doctype.employee_attendance.employee_attendance.refresh_table",
                        args: {
                            docname: selected_docs[0].name // Process the first selected doc (you can loop if required)
                        },
                        callback: function(response) {
                            if (response.message) {
                                frappe.msgprint(response.message);
                                listview.refresh(); // Refresh the List View
                            }
                        }
                    });
                }
            );
        });
    }
};
