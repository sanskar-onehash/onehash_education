import frappe


@frappe.whitelist(allow_guest=True)
def get_admission_years():
    return frappe.db.get_all("Academic Year", ["name"], {"admission_open": 1})


@frappe.whitelist(allow_guest=True)
def get_admission_year_groups(academic_year):
    return frappe.db.get_all(
        "Year Groups",
        ["year_group"],
        {
            "parenttype": "Academic Year",
            "parentfield": "admissions_open_for",
            "parent": academic_year,
        },
    )


@frappe.whitelist(allow_guest=True)
def get_admission_years_and_groups():
    admission_data = {}

    admission_years = get_admission_years()

    for admission_year in admission_years:
        admission_year_group = get_admission_year_groups(admission_year["name"])

        admission_data[admission_year["name"]] = [
            yg["year_group"] for yg in admission_year_group
        ]

    return admission_data
