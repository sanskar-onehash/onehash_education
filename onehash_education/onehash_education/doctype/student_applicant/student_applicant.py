# Copyright (c) 2025, OneHash and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

DEFAULT_WELCOME_TEMPLATE = "new_user"


class StudentApplicant(Document):

    def before_validate(self):
        self.set_missing_values()

        if not self.get("submitted"):
            self.flags.ignore_mandatory = 1

    def before_save(self):
        self.sync_addresses()
        self.clear_name_for_new_child_entries()

    def before_insert(self):
        self.set_missing_values()

    def clear_name_for_new_child_entries(self):
        # Webform saves new child table entries with name like 'row 1'
        # which conflicts on other entries at idx 1
        table_fields = self.meta.get_table_fields()
        for field in table_fields:
            rows = self.get(field.fieldname)
            for row in rows:
                if row.is_new():
                    row.name = None

    def set_missing_values(self):
        title_field = self.meta.get_title_field()
        if self.get(title_field) is None:
            self.update({title_field: ""})

        # Full name
        if self.get("first_name") and (
            not self.get("applicant_name")
            or self.has_value_changed("first_name")
            or self.has_value_changed("last_name")
        ):
            self.update(
                {
                    "applicant_name": f"{self.get('first_name')}{(self.get('last_name') or '') and f' {self.last_name}'}"
                }
            )

    def sync_addresses(self):
        if not self.same_as_permanent:
            return
        if self.correspondence_country != self.permanent_country:
            self.set("permanent_country", self.correspondence_country)
        if self.correspondence_state != self.permanent_state:
            self.set("permanent_state", self.correspondence_state)
        if self.correspondence_city != self.permanent_city:
            self.set("permanent_city", self.correspondence_city)
        if self.correspondence_address_line_1 != self.permanent_address_line_1:
            self.set("permanent_address_line_1", self.correspondence_address_line_1)
        if self.correspondence_address_line_2 != self.permanent_address_line_2:
            self.set("permanent_address_line_2", self.correspondence_address_line_2)
        if self.correspondence_pincode != self.permanent_pincode:
            self.set("permanent_pincode", self.correspondence_pincode)


@frappe.whitelist()
def send_student_application(
    first_name,
    last_name,
    student_email,
    middle_name=None,
    guardian=None,
    guardian_first_name=None,
    guardian_middle_name=None,
    guardian_last_name=None,
    gender=None,
    birth_date=None,
    phone=None,
):
    education_settings = frappe.get_doc(
        "Education Settings",
    )
    student_user = frappe.db.exists("User", {"email": student_email})

    if birth_date:
        birth_date = frappe.utils.getdate(birth_date)
    student_user_doc = None

    if not student_user:
        student_user_doc = frappe.get_doc(
            {
                "doctype": "User",
                "email": student_email,
                "first_name": guardian_first_name or first_name,
                "middle_name": guardian_middle_name or middle_name,
                "last_name": guardian_last_name or last_name,
                "gender": gender,
                "birth_date": birth_date,
                "phone": phone,
                "send_welcome_email": 0,
            }
        )
        student_user_doc.add_roles("Student Applicant")
        student_user_doc = student_user_doc.save()
        student_user = student_user_doc.name

        student_user_permission = frappe.get_doc(
            {
                "doctype": "User Permission",
                "user": student_user,
                "allow": "User",
                "for_value": student_user,
                "apply_to_all_doctypes": 0,
                "applicable_for": "Student Applicant",
            }
        ).save(ignore_permissions=True)

    student_applicant_doc = frappe.get_doc(
        {
            "doctype": "Student Applicant",
            "first_name": first_name,
            "last_name": last_name,
            "gender": gender,
            "date_of_birth": birth_date,
            "student_user": student_user,
            "guardian": guardian,
        }
    ).save()
    frappe.db.set_value(
        "Student Applicant",
        student_applicant_doc.name,
        "owner",
        student_user,
        update_modified=False,
    )

    if student_user_doc:
        send_student_login_mail(student_user_doc, education_settings)

    return student_applicant_doc.name


def send_student_login_mail(student_user_doc, education_settings):
    add_args = {
        "link": student_user_doc.reset_password(),
        "site_url": frappe.utils.get_url(),
    }
    subject = education_settings.get("application_email_subject")
    email_template = education_settings.get("application_email_template")

    if not subject:
        subject = f"Welcome to {frappe.defaults.get_defaults().company}"

    student_user_doc.send_login_mail(
        subject, DEFAULT_WELCOME_TEMPLATE, add_args, custom_template=email_template
    )
