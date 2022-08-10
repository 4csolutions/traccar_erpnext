# Copyright (c) 2022, 4C Solutions and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _
from frappe.model.document import Document
import TraccarClient
from TraccarClient.rest import ApiException

api_instance = TraccarClient.DefaultApi(TraccarClient.ApiClient())

class TraccarUser(Document):
	settings_doc = frappe.get_doc('Traccar Settings')
	configuration = api_instance.api_client.configuration
	configuration.username = settings_doc.admin_username
	configuration.password = settings_doc.get_password(fieldname='admin_password')
	configuration.host = settings_doc.server_url

	def before_save(self):
		traccar_test = frappe.db.get_single_value('Traccar Settings','traccar_test')
		if frappe.flags.traccar_sync or traccar_test:
			return
		if self.user_id:
			# User already exists on platform
			update_user(self)
		else:
			body = TraccarClient.User()
			body.name = self.full_name
			body.phone = self.phone
			body.email = self.username
			body.password = self.password
			body.device_limit = self.device_limit
			body.user_limit = self.user_limit
			body.readonly = self.readonly
			body.administrator = self.is_admin
			body.device_readonly = self.device_readonly
			try:
				# Create User
				api_response = api_instance.users_post(body)
				self.user_id = api_response.id
			except ApiException as e:
				frappe.throw(_("{0}: {1}").format(e.reason, e.body), exc=e, title="User Creation Failed")

	def before_rename(self, olddn, newdn, merge=False):
		try:
			api_response = api_instance.users_get()
			body = next((user for user in api_response if (user.id == self.user_id)), None)
			if body is None:
				frappe.msgprint("This User is not present on server", title="User Deleted", raise_exception=1)
		except ApiException as e:
			frappe.throw(_("{0}: {1}").format(e.reason, e.body), exc=e, title="Rename Failed")
		
		body.email = newdn
		try:
			# Update Username
			api_response = api_instance.users_id_put(self.user_id, body)		
		except ApiException as e:
			frappe.throw(_("{0}: {1}").format(e.reason, e.body), exc=e, title="Rename Failed")

	def after_delete(self):
		traccar_test = frappe.db.get_single_value('Traccar Settings','traccar_test')
		if frappe.flags.traccar_sync or traccar_test:
			return
		# try:
		# 	# Delete User
		# 	api_instance.users_id_delete(self.user_id)		
		# except ApiException as e:
		# 	frappe.throw(_("{0}: {1}").format(e.reason, e.body), exc=e, title="User Delete Failed")
  
def update_user(self):
	try:
		api_response = api_instance.users_get()
		body = next((user for user in api_response if (user.id == self.user_id)), None)
		if body is None:
			frappe.msgprint("This User is not present on server", title="User Deleted", raise_exception=1)
	except ApiException as e:
		frappe.throw(_("{0}: {1}").format(e.reason, e.body), exc=e, title="Fetch Users Failed")
	
	body.name = self.full_name
	body.phone = self.phone
	body.email = self.username
	body.password = self.get_password(fieldname="password")
	body.device_limit = self.device_limit
	body.user_limit = self.user_limit
	body.readonly = self.readonly
	body.administrator = self.is_admin
	body.device_readonly = self.device_readonly
	try:
		# Update User
		api_response = api_instance.users_id_put(self.user_id, body)		
	except ApiException as e:
		frappe.throw(_("{0}: {1}").format(e.reason, e.body), exc=e, title="User Update Failed")

# def create_customer(doc):
# 	customer = frappe.get_doc({
# 		'doctype': 'Customer',
# 		'customer_name': doc.full_name,
# 		'customer_group': frappe.db.get_single_value('Selling Settings', 'customer_group'),
# 		'territory' : frappe.db.get_single_value('Selling Settings', 'territory'),
# 		'customer_type': 'Individual',
# 		'default_currency': doc.default_currency,
# 		'default_price_list': doc.default_price_list,
# 		'language': doc.language
# 	}).insert(ignore_permissions=True, ignore_mandatory=True)

# 	frappe.db.set_value('Patient', doc.name, 'customer', customer.name)
# 	frappe.msgprint(_('Customer {0} is created.').format(customer.name), alert=True)