// Copyright (c) 2022, 4C Solutions and contributors
// For license information, please see license.txt

frappe.ui.form.on('Traccar User', {
	customer_address: function(frm){
		if(frm.doc.customer_address){
			frappe.call({
				method: 'frappe.contacts.doctype.address.address.get_address_display',
				args: {
					"address_dict": frm.doc.customer_address
				},
				callback: function(r) {
					frm.set_value("address", r.message);
				}
			});
		}
		if(!frm.doc.customer_address){
			frm.set_value("address", "");
		}
	}
	// refresh: function(frm) {

	// }
});
