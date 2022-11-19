frappe.ui.form.on('Vehicle', {
	onload(frm) {
		// if(frm.doc.device_id){
		// 	frappe.call({
		// 		method: 'traccar_erpnext.traccar_erpnext.utils.get_device_location',
		// 		args: {
		// 			"device_id": frm.doc.device_id
		// 		},
		// 		callback: function(r) {
		// 		    console.log(r.message);
		// 		    if (r.message.length) {
		// 				frm.set_value('total_distance', r.message[0].totalDistance);
		// 				frm.set_value('engine_hours', r.message[0].engineHours);
		// 				frm.set_value('latitude', r.message[0].lat);
		// 				frm.set_value('longitude', r.message[0].lng);						
		// 				const [dateValues, timeValues] = r.message[0].last_update.split(' ');
		// 				const [day, month, year] = dateValues.split('-');
		// 				const [hours, minutes, seconds] = timeValues.split(':');
		// 				const date = new Date(Date.UTC(+year, +month -1, +day, +hours, +minutes, +seconds));
		// 				frm.set_value('last_update', frappe.datetime.convert_to_system_tz(date));
		// 				frm.save();
		// 		    }
		// 		}
		// 	});
		// }
	},
	refresh(frm) {
	    let map_tools = ["a.leaflet-draw-draw-polyline",
			"a.leaflet-draw-draw-polygon",
			"a.leaflet-draw-draw-rectangle",
			"a.leaflet-draw-draw-circle",
			"a.leaflet-draw-draw-circlemarker"];

		map_tools.forEach((element) => $(element).hide());
		if(frm.doc.latitude && frm.doc.longitude) {
			var map = frm.get_field("traccar_location").map;			
			var latlng = L.latLng(frm.doc.latitude, frm.doc.longitude);
			var marker = L.marker(latlng);
			marker.addTo(map);
			map.flyTo(latlng, map.getZoom(), {animate: true, duration: 1.5});
			marker.bindPopup(frm.doc.license_plate + "<br>" + frappe.format(frm.doc.last_update, { fieldtype: 'Datetime' })).openPopup();
		}	    
	}
});