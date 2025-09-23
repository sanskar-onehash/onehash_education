# Copyright (c) 2025, OneHash and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class ProgramEnrollment(Document):
    def validate(self):
        self.set_student_name()
        self.validate_duplication()

    def set_student_name(self):
        if not self.student_name:
            self.student_name = frappe.db.get_value(
                "Student", self.student, "student_name"
            )

    def validate_duplication(self):
        enrollment = frappe.db.exists(
            "Program Enrollment",
            {
                "student": self.student,
                "program": self.program,
                "academic_year": self.academic_year,
                "academic_term": self.academic_term,
                "docstatus": ("<", 2),
                "name": ("!=", self.name),
            },
        )
        if enrollment:
            frappe.throw(frappe._("Student is already enrolled."))


@frappe.whitelist()
@frappe.validate_and_sanitize_search_inputs
def get_students(doctype, txt, searchfield, start, page_len, filters):
    education_settings = frappe.get_single("Education Settings")
    if not filters.get("academic_term"):
        filters["academic_term"] = education_settings.current_academic_term

    if not filters.get("academic_year"):
        filters["academic_year"] = education_settings.current_academic_year

    enrolled_students = frappe.get_list(
        "Program Enrollment",
        filters={
            "academic_term": filters.get("academic_term"),
            "academic_year": filters.get("academic_year"),
        },
        fields=["student"],
    )

    students = [d.student for d in enrolled_students] if enrolled_students else [""]

    return frappe.db.sql(
        """select
			name, student_name from tabStudent
		where
			name not in (%s)
		and
			`%s` LIKE %s
		order by
			idx desc, name
		limit %s, %s"""
        % (", ".join(["%s"] * len(students)), searchfield, "%s", "%s", "%s"),
        tuple(students + ["%%%s%%" % txt, start, page_len]),
    )
