frappe.ui.form.on('Vehicle', {
	refresh(frm) {
	    let map_tools = ["a.leaflet-draw-draw-polyline",
			"a.leaflet-draw-draw-polygon",
			"a.leaflet-draw-draw-rectangle",
			"a.leaflet-draw-draw-circle",
			"a.leaflet-draw-draw-circlemarker"];

		map_tools.forEach((element) => $(element).hide());
		
	    if(frm.doc.device_id){
			frappe.call({
				method: 'traccar_erpnext.traccar_erpnext.utils.get_device_location',
				args: {
					"device_id": frm.doc.device_id
				},
				callback: function(r) {
				    console.log(r.message);
				    if (r.message.length) {
						frm.set_value('total_distance', r.message[0].totalDistance);
						frm.set_value('engine_hours', r.message[0].engineHours);
				        var map = frm.get_field("traccar_location").map;
				        var latlng = L.latLng(r.message[0].lat,r.message[0].lng);
						var marker = L.marker(latlng);						
				        map.flyTo(latlng, map.getZoom());
				        marker.addTo(map);
				        marker.bindPopup(frm.doc.license_plate + "<br>" + r.message[0].last_update).openPopup();
				    }
				}
			});
		}
	}
});