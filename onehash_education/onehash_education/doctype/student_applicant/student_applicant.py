# Copyright (c) 2025, OneHash and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

DEFAULT_WELCOME_TEMPLATE = "new_user"


class StudentApplicant(Document):

    def before_validate(self):
        self.set_missing_values()

    def before_insert(self):
        self.set_missing_values()

    def set_missing_values(self):

        # Full name
        if (
            not self.get("applicant_name")
            or self.has_value_changed("first_name")
            or self.has_value_changed("last_name")
        ):
            self.update(
                {
                    "applicant_name": f"{self.get('first_name')} {self.get('last_name', default='')}"
                }
            )

        # Student User
        if not self.student_user and frappe.user.has_role("Student Applicant"):
            self.update({"student_user": frappe.session.user})


@frappe.whitelist()
def send_student_application(
    first_name,
    last_name,
    student_email,
    middle_name=None,
    gender=None,
    birth_date=None,
    phone=None,
):
    student_user = frappe.get_doc(
        {
            "doctype": "User",
            "email": student_email,
            "first_name": first_name,
            "middle_name": middle_name,
            "last_name": last_name,
            "gender": gender,
            "birth_date": birth_date,
            "phone": phone,
            "send_welcome_email": 0,
        }
    )
    student_user.add_roles("Student Applicant")
    student_user = student_user.save()

    education_settings = frappe.get_doc(
        "Education Settings",
    )

    add_args = {
        "link": student_user.reset_password(),
        "site_url": frappe.utils.get_url(),
    }
    subject = education_settings.get("application_email_subject")
    email_template = education_settings.get("application_email_template")

    if not subject:
        subject = f"Welcome to {frappe.defaults.get_defaults().company}"

    student_user.send_login_mail(
        subject, DEFAULT_WELCOME_TEMPLATE, add_args, custom_template=email_template
    )

    return "success"
