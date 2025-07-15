import frappe


@frappe.whitelist(allow_guest=True)
def get_admission_years():
    return frappe.db.get_all("Academic Year", ["name"], {"admission_open": 1})


@frappe.whitelist(allow_guest=True)
def get_admission_programs(academic_year):
    return frappe.db.get_all(
        "Programs",
        ["program"],
        {
            "parenttype": "Academic Year",
            "parentfield": "admissions_open_for",
            "parent": academic_year,
        },
    )
