frappe.ui.form.on('Meal Form', {
    meal_type: function (frm) {
        console.log('Meal Type Selected: ', frm.doc.meal_type); // Debugging

        if (frm.doc.meal_type === 'Breakfast' || frm.doc.meal_type === 'Lunch' || frm.doc.meal_type === 'Dinner' || frm.doc.meal_type === 'Iftari' || frm.doc.meal_type === 'Sehri') {
            // Show child tables
            frm.toggle_display('detail', true);
            frm.toggle_display('detail_meal', true);
            // frm.toggle_display('total_section', true); 
            // frm.toggle_display('service_total_section', true);
            // Hide service charges
            frm.toggle_display('service_charges_ct', false);
        } else {
            // Hide child tables
            frm.toggle_display('detail', false);
            frm.toggle_display('detail_meal', false);
            // frm.toggle_display('total_section', true);
            // frm.toggle_display('service_total_section', true);
            // Show service charges
            frm.toggle_display('service_charges_ct', true);
        }
    },
    refresh: function (frm) {
        // Call the meal_type function on form load to set initial visibility
        frm.trigger('meal_type');
    }
});
