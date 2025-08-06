// Copyright (c) 2025, OneHash and contributors
// For license information, please see license.txt

frappe.ui.form.on("Assessment", {
  refresh(frm) {
    addAssessmentActions(frm);
  },
});

function addAssessmentActions(frm) {
  if (!frm.is_new()) {
    addSendInternalAssessmentBtn(frm);
  }
}

function addSendInternalAssessmentBtn(frm) {
  if (!frm.doc.is_internal) return;

  const BTN_LABEL = "Send Assessment";
  frm.page.remove_inner_button(BTN_LABEL);
  frm.page.add_inner_button(
    BTN_LABEL,
    async () => {
      if (frm.doc.assessment_sent) {
        try {
          await new Promise((res, rej) => {
            frappe.confirm(
              "Assessment already shared. Do you want to reshare?",
              res,
              rej,
            );
          });
        } catch (err) {
          return;
        }
      }

      frappe.show_alert("Sending Assessment Link...");
      frappe.call({
        method:
          "onehash_education.onehash_education.doctype.assessment.assessment.send_assessment_link",
        args: {
          assessment: frm.doc.name,
        },
        callback: function (res) {
          if (res?.message === "success") {
            frappe.show_alert({
              indicator: "green",
              message: "Assessment link sent successfully.",
            });
          } else {
            frappe.throw(`Error sending assessment: ${res}`);
          }
        },
        freeze: true,
        freeze_message: "Sending internal assessment link.",
      });
    },
    null,
    "primary",
  );
}
