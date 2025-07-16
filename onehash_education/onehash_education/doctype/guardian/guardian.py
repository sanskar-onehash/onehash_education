# Copyright (c) 2025, OneHash and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document


class Guardian(Document):

    def validate(self):
        self.set_missing_values()

    def set_missing_values(self):

        # Full name
        if (
            not self.get("guardian_name")
            or self.has_value_changed("first_name")
            or self.has_value_changed("last_name")
        ):
            self.update(
                {
                    "guardian_name": f"{self.get('first_name')} {self.get('last_name', default='')}"
                }
            )
