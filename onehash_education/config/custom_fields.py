SALES_INVOICE_CUSTOM_FIELDS = [
    {
        "doctype": "Custom Field",
        "dt": "Sales Invoice",
        "insert_after": "company_tax_id",
        "label": "Academic Year",
        "fieldname": "custom_academic_year",
        "fieldtype": "Link",
        "options": "Academic Year",
    },
    {
        "doctype": "Custom Field",
        "dt": "Sales Invoice",
        "insert_after": "custom_academic_year",
        "label": "Year Group",
        "fieldname": "custom_year_group",
        "fieldtype": "Link",
        "options": "Year Group",
    },
]
