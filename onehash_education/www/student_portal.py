import frappe


def get_context(context):
    abbr = frappe.db.get_single_value("Education Settings", "school_college_name")
    logo = frappe.db.get_single_value("Education Settings", "school_college_logo")

    context.no_cache = True
    context.csrf_token = frappe.sessions.get_csrf_token()
    context.abbr = abbr or "OneHash Education"
    context.logo = logo or "/favicon.png"
