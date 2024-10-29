// Copyright (c) 2023, VFG and contributors
// For license information, please see license.txt

frappe.ui.form.on('Salary Increments', {
	get_employee:function(frm){
		frm.call({
			method:"get_employee",
			doc:frm.doc,
			args:{
				employee:frm.doc.employee_filter,
				department:frm.doc.department_filter,
				designation:frm.doc.designation_filter,
				branch:frm.doc.branch_filter
			},
			callback:function(r){
				//frm.save()
				frm.reload_doc()
			}
		})
	}
});
