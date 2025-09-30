// Copyright (c) 2025, OneHash and contributors
// For license information, please see license.txt

frappe.ui.form.on("Program Enrollment Tool", {
  setup: function (frm) {
    frm.add_fetch("student", "title", "student_name");
    frm.add_fetch("student_applicant", "title", "student_name");
  },

  refresh: function (frm) {
    frm.disable_save();

    frm.fields_dict.enroll_students.$input.addClass(" btn btn-primary");

    frappe.realtime.on("program_enrollment_tool", function (data) {
      frappe.hide_msgprint(true);
      frappe.show_progress(
        __("Enrolling students..."),
        data.progress[0],
        data.progress[1],
      );
    });
  },

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
                "Successfully generated the invoices, please check the list and submit them to confirm.",
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
