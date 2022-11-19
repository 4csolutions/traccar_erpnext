frappe.listview_settings['Vehicle'] = {
    onload: function(listview) {
        frappe.call({
            method: 'traccar_erpnext.traccar_erpnext.utils.update_all_vehicle_location',            
            callback: function(r) {
                console.log("Updated Locations");            
            }
        });
    },
}