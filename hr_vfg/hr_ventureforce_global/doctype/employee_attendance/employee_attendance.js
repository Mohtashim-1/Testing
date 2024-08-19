// let save_in_progress = false;  // Flag to prevent multiple saves

// frappe.ui.form.on('Employee Attendance', {
//     onload_post_render: function(frm) {
//         // Only calculate when the form is fully loaded
//         calculate_total_approved_early_over_time(frm);
//     },
//     employee_attendance_table_on_form_rendered: function(frm) {
//         calculate_total_approved_early_over_time(frm);
//     }
// });

// frappe.ui.form.on('Employee Attendance Table', {
//     approved_eot: function(frm, cdt, cdn) {
//         calculate_total_approved_early_over_time(frm);
//     },
//     employee_attendance_table_remove: function(frm, cdt, cdn) {
//         calculate_total_approved_early_over_time(frm);
//     }
// });

// function calculate_total_approved_early_over_time(frm) {
//     if (save_in_progress) return;  // Prevent saving if already in progress

//     save_in_progress = true;  // Set flag to true

//     let total_seconds = 0;
//     console.log("Calculating total approved early overtime...");

//     // Iterate over each row in the child table
//     $.each(frm.doc.table1 || [], function(i, d) {
//         if (d.approved_eot) {
//             // Split the time string into hours, minutes, and seconds
//             let time_parts = d.approved_eot.split(':');
//             console.log(time_parts)
//             console.log(d.approved_eot)
//             let hours = parseInt(time_parts[0]) || 0;
//             let minutes = parseInt(time_parts[1]) || 0;
//             let seconds = parseInt(time_parts[2]) || 0;
//             total_seconds += (hours * 3600) + (minutes * 60) + seconds;
//             console.log(total_seconds)
//         }
//     });

//     // Convert total seconds to hours as a float
//     let total_hours = total_seconds / 3600;
//     console.log(total_hours)
//     total_hours = parseFloat(total_hours.toFixed(2));  // Round to 2 decimal places
//     console.log("total_hours",total_hours)
//     // Update the parent doctype field value
//     frm.set_value('early_ot', total_hours);

//     // Save the form with a delay to avoid continuous saving loop
//     setTimeout(() => {
//         frm.save()
//             .then(() => {
//                 console.log("Data saved successfully.");
//                 save_in_progress = false;  // Reset flag after successful save
//                 // Refresh the field to update the UI
//                 frm.refresh_field('early_ot');
//                 console.log("Total hours (early_ot):", total_hours);
//             })
//             .catch((error) => {
//                 console.error("Error saving data:", error);
//                 save_in_progress = false;  // Reset flag on error
//             });
//     }, 500);  // Adjust the delay as needed (500 milliseconds in this example)
// }


