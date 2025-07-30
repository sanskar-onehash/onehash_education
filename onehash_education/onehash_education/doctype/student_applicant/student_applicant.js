// Copyright (c) 2025, OneHash and contributors
// For license information, please see license.txt

frappe.ui.form.on("Student Applicant", {
  validate(frm) {
    // setFormCompletion(frm);
  },
});

function setFormCompletion(frm, fields) {
  let totalFields = 0.0;
  let filledFields = 0.0;

  for (let field of fields) {
    if (frappe.model.layout_fields.includes(field.df.fieldtype)) {
      continue;
    }

    if (
      !field.df.depends_on ||
      frm.layout.evaluate_depends_on_value(field.df.depends_on)
    ) {
      totalFields++;

      if (frm.doc[field.df.fieldname]) {
        filledFields++;
      }
    }
  }

  frm.set_value("form_completion", (filledFields / totalFields) * 100);
}
