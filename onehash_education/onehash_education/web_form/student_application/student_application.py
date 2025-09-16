import frappe

from onehash_education.onehash_education.doctype.student_applicant.student_applicant import (
    get_applicant_custom_scripts,
)


def get_context(context):
    convert_autocomplete_back_to_link(context.web_form_doc.web_form_fields)

    # Add custom js & css
    custom_scripts = get_applicant_custom_scripts()
    if custom_scripts.get("script"):
        context.web_form_doc.custom_script = custom_scripts.get("script")
    if custom_scripts.get("style"):
        context.web_form_doc.custom_style = custom_scripts.get("style")


def convert_autocomplete_back_to_link(web_form_fields):
    applicant_meta = frappe.get_meta("Student Applicant", True)
    for field in web_form_fields:
        if field.fieldtype == "Autocomplete":
            applicant_field = applicant_meta.get_field(field.fieldname)

            if applicant_field.fieldtype != field.fieldtype:
                field.fieldtype = applicant_field.fieldtype
                field.options = applicant_field.options
