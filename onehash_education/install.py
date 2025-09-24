import frappe
from onehash_education.config.custom_fields import SALES_INVOICE_CUSTOM_FIELDS


def before_install():
    add_roles()

    frappe.db.commit()


def after_install():
    add_custom_fields()

    frappe.db.commit()


def add_roles():
    from onehash_education.config.config import ROLES

    for role in ROLES:
        if not frappe.db.exists("Role", {"role_name": role.get("name")}):
            frappe.get_doc(
                {
                    "doctype": "Role",
                    "role_name": role.get("name"),
                    "desk_access": role.get("desk_access"),
                }
            ).insert()


def add_custom_fields():
    for custom_field in SALES_INVOICE_CUSTOM_FIELDS:
        if not frappe.db.exists(
            "Custom Field",
            {"dt": custom_field["dt"], "fieldname": custom_field["fieldname"]},
        ):
            frappe.get_doc(custom_field).save()
