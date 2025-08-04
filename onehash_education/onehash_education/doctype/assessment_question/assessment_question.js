// Copyright (c) 2025, OneHash and contributors
// For license information, please see license.txt

frappe.ui.form.on("Assessment Question", {
  validate(frm) {
    if (
      frm.doc.question_type === "Multiple Choice" ||
      frm.doc.question_type === "Single Choice"
    ) {
      const correctOptions = getNumberOfCorrectOptions(frm);

      if (!correctOptions) {
        frappe.throw("Atleast one correct option is required.");
      }

      if (frm.doc.question_type === "Multiple Choice" && correctOptions < 2) {
        frappe.throw("Select `Single Choice` or add another correct option.");
      }
      if (frm.doc.question_type === "Single Choice" && correctOptions > 1) {
        frappe.throw("Only one correct option is allowed.");
      }
    }
  },
});

function getNumberOfCorrectOptions(frm) {
  return (frm.doc.options || []).filter((option) => option.is_correct).length;
}
