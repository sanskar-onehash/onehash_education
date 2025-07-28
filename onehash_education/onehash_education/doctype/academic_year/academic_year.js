// Copyright (c) 2025, OneHash and contributors
// For license information, please see license.txt

frappe.ui.form.on("Academic Year", {
  refresh: function (frm) {
    setupAcademicYearUI(frm);
  },
  add_all: async function (frm) {
    const currentYearGroups =
      frm.doc.admissions_open_for?.map((year_group) => year_group.year_group) ||
      [];
    const otherYearGroups = await frappe.db.get_list("Year Group", {
      fields: ["name"],
      filters: { name: ["not in", currentYearGroups] },
    });

    for (let otherYearGroup of otherYearGroups) {
      frm.add_child("admissions_open_for", { year_group: otherYearGroup.name });
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
