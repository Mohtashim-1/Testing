// Copyright (c) 2024, VFG and contributors
// For license information, please see license.txt

frappe.ui.form.on("Late Compensation Employee Wise", {
	// refresh(frm) {

	// },
    get_data(frm){
        frm.call({
            method:'get_data1',
            doc:frm.doc,
            args:{

            },
            callback: function(r){
                frm.reload_doc()
            }
        })
    }
});