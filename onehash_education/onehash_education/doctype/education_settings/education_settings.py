# Copyright (c) 2025, OneHash and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class EducationSettings(Document):
    pass


@frappe.whitelist()
def get_portal_css():
    return frappe.db.get_single_value("Education Settings", "portal_css")


@frappe.whitelist()
def get_portal_js():
    return frappe.db.get_single_value("Education Settings", "portal_js")


@frappe.whitelist()
def get_applicant_form_css():
    return frappe.db.get_single_value("Education Settings", "web_form_css")


@frappe.whitelist()
def get_applicant_form_js():
    return frappe.db.get_single_value("Education Settings", "web_form_js")
