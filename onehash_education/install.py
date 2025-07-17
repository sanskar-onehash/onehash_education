import frappe


def before_install():
    add_roles()


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
    frappe.db.commit()
