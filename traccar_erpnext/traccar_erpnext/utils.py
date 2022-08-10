# -*- coding: utf-8 -*-
# Copyright (c) 2020, 4C Solutions and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _
from frappe.model.document import Document
import TraccarClient
from TraccarClient.rest import ApiException

api_instance = TraccarClient.DefaultApi(TraccarClient.ApiClient())
settings_doc = frappe.get_doc('Traccar Settings')
configuration = api_instance.api_client.configuration
configuration.username = settings_doc.admin_username
configuration.password = settings_doc.get_password(fieldname='admin_password')
configuration.host = settings_doc.server_url

def update_device(doc):
    try:
        api_response = api_instance.devices_get(id=str(doc.device_id))
        device = api_response[0]
    except ApiException as e:
        frappe.throw(_("{0}: {1}").format(e.reason, e.body), exc=e, title="Fetch Device Failed")
    
    group_doc = frappe.get_doc('Traccar Group', doc.traccar_group)
    user_doc = frappe.get_doc('Traccar User', doc.traccar_user)

    device.name = doc.license_plate
    device.unique_id = doc.uniqueid
    device.group_id = group_doc.group_id
    device.phone = doc.phone
    device.model = doc.model
    device.contact = user_doc.phone
    device.category = doc.category

    permission = TraccarClient.Permission()
    permission.user_id = user_doc.user_id
    permission.device_id = doc.device_id
    
    try:
        # Update Device
        api_response = api_instance.devices_id_put(doc.device_id, device)
        # Associate device to the user of the device               
        api_response = api_instance.permissions_post(permission)
    except ApiException as e:
        frappe.throw(_("{0}: {1}").format(e.reason, e.body), exc=e, title="Update Device Failed")

def create_device(doc, method):
    if frappe.flags.traccar_sync or settings_doc.traccar_test:
        return
    if doc.device_id:
        update_device(doc)
    else:       
        group_doc = frappe.get_doc('Traccar Group', doc.traccar_group)
        user_doc = frappe.get_doc('Traccar User', doc.traccar_user)

        device = TraccarClient.Device()
        device.name = doc.license_plate
        device.unique_id = doc.uniqueid
        device.group_id = group_doc.group_id
        device.phone = doc.phone
        device.model = doc.model
        device.contact = user_doc.phone
        device.category = doc.category

        permission = TraccarClient.Permission()
        permission.user_id = user_doc.user_id
        
        try:
            # Create Device
            api_response = api_instance.devices_post(device)
            doc.device_id = api_response.id
            # Associate device to the user of the device
            permission.device_id = api_response.id
            api_response = api_instance.permissions_post(permission)            
        except ApiException as e:
            frappe.throw(_("{0}: {1}").format(e.reason, e.body), exc=e, title="Create Device Failed")

def delete_device(doc, method):
    if frappe.flags.traccar_sync or settings_doc.traccar_test:
        return
    # try:
    #     # Delete Device
    #     api_response = api_instance.devices_id_delete(doc.device_id)
    # except ApiException as e:
    #     frappe.throw(_("{0}: {1}").format(e.reason, e.body), exc=e, title="Delete Device Failed")

def convertMilliSeconds(milliSeconds):
    seconds = milliSeconds // 1000
    hour = seconds // 3600
    seconds %= 3600
    minutes = seconds // 60
      
    return "%d Hrs %02d Mins" % (hour, minutes)

@frappe.whitelist()
def get_device_location(device_id):
    try:
        # Fetch Device Location
        api_response = api_instance.devices_get(id=str(device_id))
        last_update = api_response[0].last_update.strftime("%d-%m-%Y %H:%M:%S")
        position_id = api_response[0].position_id
        if position_id:
            api_response = api_instance.positions_get(id=str(position_id))
            longitude = api_response[0].longitude
            latitude = api_response[0].latitude
            totalDistance = "{:.2f}".format(api_response[0].attributes.get('totalDistance')/1000)
            engineHours = convertMilliSeconds(api_response[0].attributes.get('hours'))
            return [{ "lat":latitude,
                     "lng":longitude,
                     "last_update":last_update,
                     "totalDistance": totalDistance,
                     "engineHours":  engineHours}]
        return []
    except ApiException as e:
        frappe.throw(_("{0}: {1}").format(e.reason, e.body), exc=e, title="Fetch Device Location Failed")
