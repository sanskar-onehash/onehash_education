import frappe


def get_context(context):
    convert_autocomplete_back_to_link(context.web_form_doc.web_form_fields)


def convert_autocomplete_back_to_link(web_form_fields):
    applicant_meta = frappe.get_meta("Student Applicant", True)
    for field in web_form_fields:
        if field.fieldtype == "Autocomplete":
            applicant_field = applicant_meta.get_field(field.fieldname)

            if applicant_field.fieldtype != field.fieldtype:
                field.fieldtype = "Link"
                field.options = applicant_field.options
