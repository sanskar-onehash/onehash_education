# Copyright (c) 2025, OneHash and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document


class YearGroup(Document):

    def before_save(self):
        self.set_docname()

    def before_insert(self):
        self.set_docname()

    def set_docname(self):
        if self.is_new():
            self.name = f"{self.year_group}{f' ({self.grade})' if self.grade else ''}"
