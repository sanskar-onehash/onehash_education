import frappe


def get_default_print_format(doctype):
    meta = frappe.get_meta(doctype)
    return meta.default_print_format
