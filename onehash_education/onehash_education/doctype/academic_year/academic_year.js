// Copyright (c) 2025, OneHash and contributors
// For license information, please see license.txt

frappe.ui.form.on("Academic Year", {
  refresh: function (frm) {
    setupAcademicYearUI(frm);
  },
  add_all: async function (frm) {
    const currentPrograms =
      frm.doc.programs?.map((program) => program.program) || [];
    const otherPrograms = await frappe.db.get_list("Program", {
      fields: ["name"],
      filters: { name: ["not in", currentPrograms] },
    });

    for (let otherProgram of otherPrograms) {
      frm.add_child("admissions_open_for", { program: otherProgram.name });
    }
    frm.refresh_field("admissions_open_for");
  },
  clear: function (frm) {
    frm.set_value("admissions_open_for", []);
    frm.dirty();
  },
});

function setupAcademicYearUI(frm) {
  frm.$wrapper
    .find("[data-fieldname='add_all'], [data-fieldname='clear']")
    .css({ display: "inline-block" });
}
