# Copyright (c) 2025, OneHash and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class Student(Document):

    def before_insert(self):

        if self.user_id:
            user = frappe.get_doc("User", self.user_id)
            user.remove_roles("Student Applicant")
            user.add_roles("Student")
