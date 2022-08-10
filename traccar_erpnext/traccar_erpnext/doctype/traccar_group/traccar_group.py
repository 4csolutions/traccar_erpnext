# Copyright (c) 2022, 4C Solutions and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _
from frappe.utils.nestedset import NestedSet
import TraccarClient
from TraccarClient.rest import ApiException

api_instance = TraccarClient.DefaultApi(TraccarClient.ApiClient())

class TraccarGroup(NestedSet):
	settings_doc = frappe.get_doc('Traccar Settings')
	configuration = api_instance.api_client.configuration
	configuration.username = settings_doc.admin_username
	configuration.password = settings_doc.get_password(fieldname='admin_password')
	configuration.host = settings_doc.server_url

	def before_save(self):
		traccar_test = frappe.db.get_single_value('Traccar Settings','traccar_test')
		if frappe.flags.traccar_sync or traccar_test:
			return
		if self.group_id:
			# Group already exists on platform
			update_group(self)
		else:
			body = TraccarClient.Group()
			body.name = self.traccar_group_name
			if self.parent_traccar_group:
				parent = frappe.get_doc("Traccar Group", self.parent_traccar_group)
				body.group_id = parent.group_id

			try:
				# Create a Group
				api_response = api_instance.groups_post(body)
				self.group_id = api_response.id
			except ApiException as e:
				frappe.throw(_("{0}: {1}").format(e.reason, e.body), exc=e, title="Group Creation Failed")

	def before_rename(self, olddn, newdn, merge=False, group_fname='is_group'):
		try:
			api_response = api_instance.groups_get()
			body = next((group for group in api_response if (group.id == self.group_id)), None)
			if body is None:
				frappe.msgprint("This Group is not present on server", title="Group Deleted", raise_exception=1)
		except ApiException as e:
			frappe.throw(_("{0}: {1}").format(e.reason, e.body), exc=e, title="Group Update Failed")

		body.name = newdn
		try:
			# Update Group
			api_response = api_instance.groups_id_put(self.group_id, body)
		except ApiException as e:
			frappe.throw(_("{0}: {1}").format(e.reason, e.body), exc=e, title="Group Update Failed")
		return super().before_rename(olddn, newdn, merge=merge, group_fname=group_fname)

	def after_delete(self):
		traccar_test = frappe.db.get_single_value('Traccar Settings','traccar_test')
		if frappe.flags.traccar_sync or traccar_test:
			return
		# try:
		# 	# Delete a Group
		# 	api_instance.groups_id_delete(self.group_id)
		# except ApiException as e:
		# 	frappe.throw(_("{0}: {1}").format(e.reason, e.body), exc=e, title="Group Delete Failed")
  
def update_group(self):
	try:
		api_response = api_instance.groups_get()
		body = next((group for group in api_response if (group.id == self.group_id)), None)
		if body is None:
			frappe.msgprint("This Group is not present on server", title="Group Deleted", raise_exception=1)
	except ApiException as e:
		frappe.throw("This Group is not present on server", exc=e, title="Group Deleted")

	body.name = self.traccar_group_name
	if self.parent_traccar_group:
		parent = frappe.get_doc("Traccar Group", self.parent_traccar_group)
		body.group_id = parent.group_id
	
	try:
		# Update Group
		api_response = api_instance.groups_id_put(self.group_id, body)		
	except ApiException as e:
		frappe.throw(_("{0}: {1}").format(e.reason, e.body), exc=e, title="Group Update Failed")

