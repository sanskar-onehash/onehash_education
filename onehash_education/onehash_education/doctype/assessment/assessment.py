# Copyright (c) 2025, OneHash and contributors
# For license information, please see license.txt


import frappe
from frappe.email.doctype.email_template.email_template import get_email_template
from frappe.model.document import Document
from frappe.core.doctype.communication.email import make


class Assessment(Document):
    pass


@frappe.whitelist()
def send_assessment_link(assessment):
    assessment_doc = frappe.get_doc("Assessment", assessment)

    if not assessment_doc.is_internal:
        frappe.throw("Assessment is not internal.")
    if not assessment_doc.assessment_master:
        frappe.throw("Assessment Master is not set.")

    assessment_master_doc = frappe.get_doc(
        "Assessment Master", assessment_doc.assessment_master
    )

    assessment_link = f"{frappe.utils.get_url()}/assessment?assessment={frappe.utils.quote(assessment)}"
    applicant_name = frappe.db.get_value(
        "Student Applicant", assessment_doc.applicant, "applicant_name"
    )

    subject = "Action Required: Complete Your Assessment"
    message = """Dear {0},

I hope this message finds you well.

Please complete the following assessment using the link below:

{1}""".format(
        applicant_name, assessment_link
    )
    if assessment_master_doc.email_template:
        email_template = get_email_template(
            assessment_master_doc.email_template,
            {
                "assessment_link": assessment_link,
                "applicant_name": applicant_name,
                **assessment_doc.as_dict(),
            },
        )
        subject = email_template.get("subject")
        message = email_template.get("message")

    make(
        doctype=assessment_doc.doctype,
        name=assessment_doc.name,
        content=message,
        subject=subject,
        recipients=frappe.db.get_value("User", assessment_doc.assessment_for, "email"),
        send_email=True,
    )

    return "success"
