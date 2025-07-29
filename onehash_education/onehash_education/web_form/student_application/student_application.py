import frappe


def get_context(context):
    education_settings = frappe.get_single("Education Settings")
    convert_autocomplete_back_to_link(context.web_form_doc.web_form_fields)

    # Add custom js
    if education_settings.get("web_form_js"):
        context.web_form_doc.custom_script = education_settings.get("web_form_js")

    # Add custom css
    if education_settings.get("web_form_css"):
        context.web_form_doc.custom_style = education_settings.get("web_form_css")


def convert_autocomplete_back_to_link(web_form_fields):
    applicant_meta = frappe.get_meta("Student Applicant", True)
    for field in web_form_fields:
        if field.fieldtype == "Autocomplete":
            applicant_field = applicant_meta.get_field(field.fieldname)

            if applicant_field.fieldtype != field.fieldtype:
                field.fieldtype = applicant_field.fieldtype
                field.options = applicant_field.options
