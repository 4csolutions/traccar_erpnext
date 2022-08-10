// Copyright (c) 2022, 4C Solutions and contributors
// For license information, please see license.txt

frappe.ui.form.on('Traccar Settings', {
	onload: function(frm) {
		frappe.realtime.on("fetch_data_progress", function(data) {
			if (data.reload && data.reload === 1) {
				frm.reload_doc();
			}
			if (data.progress) {
				let progress_bar = $(cur_frm.dashboard.progress_area).find(".progress-bar");
				if (progress_bar) {
					$(progress_bar).removeClass("progress-bar-danger").addClass("progress-bar-success progress-bar-striped");
					$(progress_bar).css("width", data.progress+"%");
				}
			}
		});
	},
	
	refresh: function(frm) {
		if (frm.doc.user_id) {
			frm.add_custom_button(__('Fetch Traccar Data'), function() {
				frm.dashboard.add_progress("Fetch Traccar Data Status", "0");
				frappe.call({
					method: "fetch_traccar_data",
					doc: frm.doc,
					callback: function() {						
					}
				});
			}, "fa fa-play", "btn-success");
		}		
	}
});
