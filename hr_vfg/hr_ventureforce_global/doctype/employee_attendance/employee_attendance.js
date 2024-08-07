// Copyright (c) 2018, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.ui.form.on('Employee Attendance', {
    refresh: function(frm) {
        calculate_total_approved_early_over_time(frm);
    },
    employee_attendance_table_on_form_rendered: function(frm) {
        calculate_total_approved_early_over_time(frm);
    }
});

frappe.ui.form.on('Employee Attendance Table', {
    approved_early_over_time: function(frm, cdt, cdn) {
        calculate_total_approved_early_over_time(frm);
    },
    employee_attendance_table_remove: function(frm, cdt, cdn) {
        calculate_total_approved_early_over_time(frm);
    }
});

function calculate_total_approved_early_over_time(frm) {
    let total_seconds = 0;
    console.log(1)
    $.each(frm.doc.table1 || [], function(i, d) {
        console.log(1)
        if(d.approved_early_over_time) {
            console.log(1)
            let time_parts = d.approved_early_over_time.split(':');
            let hours = parseInt(time_parts[0]);
            let minutes = parseInt(time_parts[1]);
            let seconds = parseInt(time_parts[2]);
            total_seconds += (hours * 3600) + (minutes * 60) + seconds;
            console.log(1)
        }
    });

    let total_hours = Math.floor(total_seconds / 3600);
    let total_minutes = Math.floor((total_seconds % 3600) / 60);
    let total_seconds_remaining = total_seconds % 60;

    let total_time_str = total_hours.toString().padStart(2, '0') + ':' +
                         total_minutes.toString().padStart(2, '0') + ':' +
                         total_seconds_remaining.toString().padStart(2, '0');

    frm.set_value('approved_early_over_time_hour', total_time_str);
    frm.refresh_field('approved_early_over_time_hour');
}


