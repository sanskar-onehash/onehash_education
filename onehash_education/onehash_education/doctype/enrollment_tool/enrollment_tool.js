// Copyright (c) 2025, OneHash and contributors
// For license information, please see license.txt

frappe.ui.form.on("Enrollment Tool", {
  setup: function (frm) {
    frm.add_fetch("student", "title", "student_name");
    frm.add_fetch("student_applicant", "title", "student_name");
  },

  refresh: function (frm) {
    frm.disable_save();

    frm.fields_dict.enroll_students.$input.addClass(" btn btn-primary");
  },

  get_students_from: setupTermFilters,
  academic_year: setupTermFilters,
  new_academic_year: setupTermFilters,

  get_students: async function (frm) {
    try {
      frappe.dom.freeze("Fetching Students...");

      frm.set_value("students", []);
      await frappe.call({
        method: "get_students",
        doc: frm.doc,
        callback: function (r) {
          if (r.message) {
            frm.set_value("students", r.message);
            frappe.hide_msgprint(true);
            frappe.show_alert({
              indicator: "green",
              message: "Successfully fetched students.",
            });
          }
        },
      });
    } catch (error) {
      frappe.throw(error);
    } finally {
      frappe.dom.unfreeze();
    }
  },

  enroll_students: async function (frm) {
    try {
      frappe.dom.freeze("Enrolling Students...");

      await frappe.call({
        method: "enroll_students",
        doc: frm.doc,
        callback: function (r) {
          if (r.message) {
            frm.set_value("students", []);
            frappe.hide_msgprint(true);
            frappe.show_alert({
              indicator: "green",
              message:
                "Successfully enrolled students, please check the list and submit them to confirm.",
            });
          }
        },
      });
    } catch (error) {
      frappe.throw(error);
    } finally {
      frappe.dom.unfreeze();
    }
  },
});

function setupTermFilters(frm) {
  frm.set_query("academic_term", () => ({
    filters: { academic_year: frm.doc.academic_year },
  }));

  if (frm.doc.get_students_from === "Enrollment") {
    frm.set_query("new_academic_terms", () => ({
      filters: { academic_year: frm.doc.new_academic_year },
    }));
  } else {
    frm.set_query("new_academic_terms", () => ({
      filters: { academic_year: frm.doc.academic_year },
    }));
  }
}
