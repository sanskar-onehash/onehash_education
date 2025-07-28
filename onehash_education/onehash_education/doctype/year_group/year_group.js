// Copyright (c) 2025, OneHash and contributors
// For license information, please see license.txt

frappe.ui.form.on("Year Group", {
  validate: function (frm) {
    if (frm.is_new()) {
      frm.set_value(
        "year_group_name",
        `${frm.doc.year_group}${frm.doc.grade ? ` (${frm.doc.grade})` : ""}`,
      );
    }
  },
});
