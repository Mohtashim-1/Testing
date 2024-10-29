frappe.ui.form.on("Absent Adjustment With Holiday", {
    get_data2(frm) {
        frm.call({
            method: "get_data1",  // Make sure this matches exactly
            doc: frm.doc,
            callback: function(r) {
                frm.reload_doc();  // Refresh the form after the data is fetched
            }
        });
    }
    // get_data2(frm) {
    //     frm.call({
    //         method: "get_data2",  // Make sure this matches exactly
    //         doc: frm.doc,
    //         callback: function(r) {
    //             frm.reload_doc();  // Refresh the form after the data is fetched
    //         }
    //     });
    // }
});

frappe.ui.form.on("Absent Adjustment With Holiday", {
    
    get_data2(frm) {
        frm.call({
            method: "get_data2",  // Make sure this matches exactly
            doc: frm.doc,
            callback: function(r) {
                frm.reload_doc();  // Refresh the form after the data is fetched
            }
        });
    }
});
