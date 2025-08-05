// Copyright (c) 2024, VFG and contributors
// For license information, please see license.txt

frappe.ui.form.on('Employee Advance Bulk', {
    refresh: function(frm) {
        // Add custom button only if document is submitted and no payment entries exist
        if (frm.doc.docstatus === 1) {
            // Check if any payment entries exist
            let hasPaymentEntries = false;
            if (frm.doc.employee_advance_bulk_ct) {
                hasPaymentEntries = frm.doc.employee_advance_bulk_ct.some(row => row.payment_entry);
            }
            
            // Only show button if no payment entries exist
            if (!hasPaymentEntries) {
                frm.add_custom_button(__('Create Disbursed Payment'), function() {
                    create_disbursed_payment(frm);
                }).addClass('btn-primary');
            }
        }
    },
    
    get_data: function(frm) {
        frm.call({
            method: 'get_data',
            doc: frm.doc,
            args: {},
            callback: function(r) {
                frm.reload_doc();
            }
        });
    }
});

function create_disbursed_payment(frm) {
    // Show dialog to select payment account
    frappe.prompt([
        {
            'fieldname': 'payment_account',
            'fieldtype': 'Link',
            'label': 'Payment Account',
            'options': 'Account',
            'reqd': 1,
            'description': 'Select the account from which payment will be made'
        }
    ], function(values) {
        if (values.payment_account) {
            frappe.call({
                method: 'hr_vfg.hr_ventureforce_global.doctype.employee_advance_bulk.employee_advance_bulk.create_disbursed_payment',
                args: {
                    docname: frm.doc.name,
                    payment_account: values.payment_account
                },
                callback: function(r) {
                    if (r.exc) {
                        frappe.msgprint(__('Error: ') + r.exc);
                    } else {
                        frappe.msgprint(__('Payment entries created successfully!'));
                        frm.reload_doc();
                        // Refresh the form to hide the button
                        frm.refresh();
                    }
                }
            });
        }
    }, __('Select Payment Account'), __('Create Payment'));
}
