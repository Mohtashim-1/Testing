// employee marked as left

frappe.ui.form.on('Employee', {
    refresh: function(frm) {
        if (frm.doc.status == 'Active') {
            frm.add_custom_button(__('Mark as Left'), function() {
                let d = new frappe.ui.Dialog({
                    title: 'Enter Relieving Date',
                    fields: [
                        {
                            fieldtype: 'Date',
                            fieldname: 'relieving_date',
                            label: 'Relieving Date',
                            reqd: true
                        },
                        {
                            fieldtype: 'Small Text',
                            fieldname: 'reason_for_leaving',
                            label: 'Reason for Leaving',
                            reqd: true
                        }
                    ],
                    primary_action_label: 'Mark as Left',
                    primary_action: function(values) {
                        frappe.call({
                            method: "frappe.client.set_value",
                            args: {
                                doctype: "Employee",
                                name: frm.doc.name,
                                fieldname: {
                                    relieving_date: values.relieving_date,
                                    status: "Left",
                                    reason_for_leaving: values.reason_for_leaving
                                }
                            },
                            callback: function(response) {
                                if (!response.exc) {
                                    frappe.msgprint("Employee marked as Left");
                                    frm.reload_doc();
                                    d.hide();
                                }
                            }
                        });
                    }
                });
                d.show();
            });
        }
    }
});


// employee marked as active

frappe.ui.form.on('Employee', {
    refresh: function(frm) {
        if (frm.doc.status === 'Left') {
            frm.add_custom_button(__('Mark as Active'), function() {
                let d = new frappe.ui.Dialog({
                    title: 'Rejoin Employee',
                    fields: [
                        {
                            fieldtype: 'Date',
                            fieldname: 'date_of_joining',
                            label: 'New Date of Joining',
                            reqd: true
                        },
                        {
                            fieldtype: 'Small Text',
                            fieldname: 'reason_for_rejoining',
                            label: 'Reason for Rejoining',
                            reqd: true
                        }
                    ],
                    primary_action_label: 'Mark as Active',
                    primary_action: function(values) {
                        // First update employee fields
                        frappe.call({
                            method: "frappe.client.set_value",
                            args: {
                                doctype: "Employee",
                                name: frm.doc.name,
                                fieldname: {
                                    date_of_joining: values.date_of_joining,
                                    status: "Active",
                                    "relieving_date":""
                                }
                            },
                            callback: function(response) {
                                if (!response.exc) {
                                    // Then insert comment with reason
                                    frappe.call({
                                        method: "frappe.client.insert",
                                        args: {
                                            doc: {
                                                doctype: "Comment",
                                                comment_type: "Comment",
                                                comment_email: frappe.session.user,
                                                comment_by: frappe.session.user_fullname,
                                                reference_doctype: "Employee",
                                                reference_name: frm.doc.name,
                                                content: "Rejoined with reason: " + values.reason_for_rejoining
                                            }
                                        },
                                        callback: function() {
                                            frappe.msgprint("Employee marked as Active");
                                            frm.reload_doc();
                                            d.hide();
                                        }
                                    });
                                }
                            }
                        });
                    }
                });
                d.show();
            });
        }
    }
});
