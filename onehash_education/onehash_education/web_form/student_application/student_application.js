// Fixes overflowing S.No.
frappe._messages["No.:Title of the 'row number' column"] = "S.No.";
clientsideStylesFix();

frappe.ready(function () {
  const frm = frappe.web_form;
  const frmDoc = frappe.web_form_doc;
  const $submitBtn = $(".submit-btn");
  const $discardBtn = $(".discard-btn.btn");
  const $editBtn = $(".edit-button.btn");

  setupForm();

  function setupForm() {
    setupFormUI();
    runCustomScript();
  }

  function setupFormUI() {
    setupActionButtons();

    $(".success-title").text("Changes Saved");
    if (!$submitBtn.length) {
      $(".save-btn-custom").hide();
      $(".submit-btn-custom").hide();
    } else {
      $(".save-btn-custom").show();
      $(".submit-btn-custom").show();
    }
  }

  function runCustomScript() {
    if (frmDoc.custom_script) {
      const customScript = new Function(frmDoc.custom_script);
      customScript();
    }
    if (frmDoc.custom_style) {
      const $style = $(`<style>${frmDoc.custom_style}</style>`);
      $("head").append($style);
    }
  }

  function validateMandatories() {
    if (!frm.doc.submitted) return;

    const errors = [];
    const invalidFields = [];

    frm.fields_list.forEach((field) => {
      if (field.get_value) {
        let value = field.get_value();
        if (
          field.df.reqd &&
          is_null(typeof value === "string" ? strip_html(value) : value)
        )
          errors.push(__(field.df.label));

        if (
          field.df.reqd &&
          field.df.fieldtype === "Text Editor" &&
          is_null(strip_html(cstr(value)))
        )
          errors.push(__(field.df.label));

        if (field.df.invalid) invalidFields.push(__(field.df.label));
      }
    });

    let message = "";
    if (invalidFields.length) {
      message += __(
        "Invalid values for fields:",
        null,
        "Error message in web form",
      );
      message += "<br><br><ul><li>" + invalidFields.join("<li>") + "</ul>";
    }

    if (errors.length) {
      message += __(
        "Mandatory fields required:",
        null,
        "Error message in web form",
      );
      message += "<br><br><ul><li>" + errors.join("<li>") + "</ul>";
    }

    if (invalidFields.length || errors.length) {
      frm.set_value("submitted", 0);
      frappe.throw({
        title: __("Error", null, "Title of error message in web form"),
        message: message,
        indicator: "orange",
      });
    }
  }

  function setupActionButtons() {
    // Custom Save button
    const $customSaveBtn = $(
      `<div class='btn save-btn-custom btn-info'>${frm.button_label}</div>`,
    );
    $customSaveBtn.click(handleCustomSave);

    // Custom Save & Submit Button
    const $customSaveAndSubmitBtn = $(
      `<div class='btn submit-btn-custom btn-primary'>Save & Submit</div>`,
    );
    $customSaveAndSubmitBtn.click(handleCustomSaveAndSubmit);

    $(".web-form-head .web-form-actions").append([
      $customSaveBtn,
      $customSaveAndSubmitBtn,
    ]);
  }

  function handleCustomSave(e) {
    $submitBtn.click();
  }

  async function handleCustomSaveAndSubmit(e) {
    await frm.set_value("submitted", 1);
    validateMandatories();

    $submitBtn.click();
  }
});

function clientsideStylesFix() {
  if (!$(".page-content-wrapper .container .page-content").length) {
    $(".page-content-wrapper").append(
      $("<div class='container my-4 fix-container'><div>"),
    );
    $(".page-content-wrapper .fix-container").append(
      $(".page-content-wrapper .page_content"),
    );
  }
}
