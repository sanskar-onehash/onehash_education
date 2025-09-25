# Copyright (c) 2025, OneHash and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document


class AcademicTerm(Document):

    def before_insert(self):

        if not self.title:
            self.update({"title": f"{self.term_name} ({self.academic_year})"})
