# Copyright (c) 2025, OneHash and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class StudentWithdrawal(Document):

    def before_insert(self):
        existing_withdrawal = frappe.db.exists(
            "Student Withdrawal",
            {
                "student": self.student,
                "docstatus": ["!=", 2],
                "name": ["!=", self.name],
            },
        )

        if existing_withdrawal:
            frappe.throw(
                """<a href='{url}'><strong>Student Withdrawal</strong></a> already exists for the student, please cancel it to create new.""".format(
                    url=frappe.utils.get_url_to_form(
                        "Student Withdrawal", existing_withdrawal
                    )
                )
            )

    def before_submit(self):
        if frappe.db.exists(
            "Enrollment",
            {
                "student": self.student,
                "docstatus": 1,
                "status": ["in", ["Active", "Upcoming"]],
            },
        ):
            frappe.throw(
                "Active or Upcoming enrollments exist for the student. Please cancel them."
            )

        student_doc = frappe.get_doc("Student", self.student)
        if student_doc.enabled:
            student_doc.enabled = 0
            student_doc.save()
            frappe.msgprint("Student Document Disabled.")

        self.withdrawn_on = frappe.utils.get_datetime()
        self.withdrawn_by = frappe.session.user
