# Copyright (c) 2022, 4C Solutions and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils.password import get_decrypted_password
from frappe.utils.background_jobs import enqueue
import TraccarClient
from TraccarClient.rest import ApiException

api_instance = TraccarClient.DefaultApi(TraccarClient.ApiClient())
fetch_total_tasks = 3

class TraccarSettings(Document):
	def validate(self):
		# Configure HTTP basic authorization: basicAuth
		configuration = api_instance.api_client.configuration
		configuration.username = self.admin_username
		configuration.password = self.get_password(fieldname='admin_password')
		configuration.host = self.server_url
		
		try:
			# Fetch Server information
			api_response = api_instance.server_get()			
			if not api_response.id:
				frappe.msgprint("Please check Server API URL", title="Invalid Server URL")
			try:
				api_response = api_instance.session_post(configuration.username, configuration.password)
				if not api_response.id:
					frappe.msgprint("Please check Username and Password", title="Invalid User Credentials")
				else:
					self.user_id = api_response.id
			except ApiException as e:
				frappe.throw("Please enter correct username and password", exc=e, title="Invalid User Credentials")
		except ApiException as e:
			frappe.throw("Please check Server API URL", exc=e, title="Invalid Server URL")
			
	@frappe.whitelist()
	def fetch_traccar_data(self):    				
		frappe.publish_realtime("fetch_data_progress",
				{"progress": "0", "reload": 1}, user=frappe.session.user)
		frappe.msgprint(_('''Traccar records will be created in the background.
				In case of any error the error message will be updated in the Settings.'''))
		enqueue(create_traccar_docs, queue='default', timeout=6000, event='create_traccar_docs',
				doc=self)
       
def create_traccar_docs(doc):
    frappe.flags.traccar_sync = True
    api_instance = TraccarClient.DefaultApi(TraccarClient.ApiClient())
    configuration = api_instance.api_client.configuration
    configuration.username = doc.admin_username
    configuration.password = doc.get_password(fieldname='admin_password')
    configuration.host = doc.server_url
    
    create_traccar_groups(api_instance)
    create_traccar_users(api_instance)
    create_traccar_devices(api_instance)
    frappe.flags.traccar_sync = False
    
def create_traccar_groups(api_instance):
    try:
        # Group get all works only for admin user
        # TODO check if user is admin/manager & accordingly change the api to get groups
        thread = api_instance.groups_get(all='all', async_req=True)
        traccar_groups = thread.get()
        total_records = len(traccar_groups)
        created_records = 0
        for group in traccar_groups:
            doc = frappe.get_doc({
                'doctype': 'Traccar Group',
                'traccar_group_name': group.name,
                'group_id': group.id,
                'parent_traccar_gorup': frappe.db.get_value('Traccar Group', {'group_id': group.group_id}, 'name')
            })            
            doc.insert()
            created_records += 1
            frappe.publish_realtime("fetch_data_progress", {"progress": str(int(created_records * 100/(fetch_total_tasks*total_records)))}, user=frappe.session.user)
    except ApiException as e:
        frappe.throw(_("{0}: {1}").format(e.reason, e.body), exc=e, title="Fetch Group Failed")
        
def create_traccar_users(api_instance):
    try:
        # Fetch all Users
        thread = api_instance.users_get(async_req=True)
        traccar_users = thread.get()
        total_records = len(traccar_users)
        created_records = 0
        for user in traccar_users:
            doc = frappe.get_doc({
                'doctype': 'Traccar User',
                'full_name': user.name,
                'username': user.email,
                'phone' : user.phone,
                'user_id': user.id,
                'is_admin' : user.administrator,
                'readonly' : user.readonly,
                'device_readonly' : user.device_readonly,
                'device_limit' : user.device_limit,
                'user_limit' : user.user_limit                
            })
            doc.insert(ignore_mandatory=True)
            created_records += 1
            frappe.publish_realtime("fetch_data_progress", 
                                    {"progress": str(1/fetch_total_tasks + 
                                                     int(created_records * 100/(fetch_total_tasks*total_records)))}, 
                                    user=frappe.session.user)
    except ApiException as e:
        frappe.throw(_("{0}: {1}").format(e.reason, e.body), exc=e, title="Fetch Group Failed")

def create_traccar_devices(api_instance):
    try:
        # Fetch all Devices
        thread = api_instance.devices_get(async_req=True)
        traccar_devices = thread.get()
        total_records = len(traccar_devices)
        created_records = 0
        for device in traccar_devices:
            doc = frappe.get_doc({
                'doctype': 'Vehicle',
                'license_plate': device.name,
                'model': device.model,
                'category' : device.category.title(),                
                'device_id': device.id,
                'uniqueid' : frappe.get_value('Serial No', {'name': device.unique_id}, 'name'),
                'phone' : frappe.get_value('Serial No', {'name': device.phone}, 'name'),
                'traccar_group' : frappe.db.get_value('Traccar Group', {'group_id': device.group_id}, 'name')
            })            
            doc.insert(ignore_mandatory=True)
            created_records += 1
            frappe.publish_realtime("fetch_data_progress", 
                                    {"progress": str(2/fetch_total_tasks + 
                                                     int(created_records * 100/(fetch_total_tasks*total_records)))}, 
                                    user=frappe.session.user)
    except ApiException as e:
        frappe.throw(_("{0}: {1}").format(e.reason, e.body), exc=e, title="Fetch Group Failed")
