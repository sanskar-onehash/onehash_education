// Copyright (c) 2025, OneHash and contributors
// For license information, please see license.txt

frappe.ui.form.on("Program Enrollment", {
  onload: function (frm) {
    frm.set_query("academic_term", function () {
      return {
        filters: {
          academic_year: frm.doc.academic_year,
        },
      };
    });

    frm.set_query("student", function () {
      return {
        query:
          "onehash_education.onehash_education.doctype.program_enrollment.program_enrollment.get_students",
        filters: {
          academic_year: frm.doc.academic_year,
          academic_term: frm.doc.academic_term,
        },
      };
    });
  },
});
