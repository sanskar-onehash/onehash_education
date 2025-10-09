# Copyright (c) 2025, OneHash and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class AcademicTerm(Document):

    def validate(self):
        self.validate_term_date_range()

    def before_insert(self):
        self.update({"title": f"{self.term_name} ({self.academic_year})"})

        self.validate_term_date_range()

    def validate_term_date_range(self, academic_year=None):
        if not academic_year:
            academic_year = self.academic_year

        start_date = frappe.utils.getdate(self.term_start_date)
        end_date = frappe.utils.getdate(self.term_end_date)

        if start_date > end_date:
            frappe.throw(
                "The Academic Term's start date cannot be later than the end date."
            )

        academic_year_doc = frappe.get_doc("Academic Year", self.academic_year)

        if start_date < academic_year_doc.year_start_date:
            frappe.throw(
                "The Academic Term's start date cannot be earlier than the start of the Academic Year."
            )

        if end_date > academic_year_doc.year_end_date:
            frappe.throw(
                "The Academic Term's end date cannot be later than the end of the Academic Year."
            )
