// Fixes overflowing S.No.
frappe._messages["No.:Title of the 'row number' column"] = "S.No.";

frappe.ready(function () {
  const frm = frappe.web_form;
  const $submitBtn = $(".submit-btn");
  const $discardBtn = $(".discard-btn.btn");
  const $editBtn = $(".edit-button.btn");

  setupForm();

  function setupForm() {
    setupFormUI();
  }

  function setupFormUI() {
    // `FIXES:` clientside app web.html template
    // Wrap page-content in container
    if (!$(".page-content-wrapper .container .page-content").length) {
      $(".page-content-wrapper").append(
        $("<div class='container my-4 fix-container'><div>"),
      );
      $(".page-content-wrapper .fix-container").append(
        $(".page-content-wrapper .page_content"),
      );
    }

    setupDependsOn();
    setupActionButtons();

    if (!$submitBtn.length) {
      $(".save-btn-custom").hide();
      $(".submit-btn-custom").hide();
    } else {
      $(".save-btn-custom").show();
      $(".submit-btn-custom").show();
    }
  }

  async function setupDependsOn() {
    if (!frm.doc.naming_series) {
      // As initial fields are dependant on naming_series
      await frm.set_value(
        "naming_series",
        frm.fields_dict.naming_series.df.default,
      );
    }
    frm.fields_list.forEach((field) => {
      if (
        field.df.mandatory_depends_on &&
        frm.evaluate_depends_on_value(field.df.mandatory_depends_on)
      ) {
        frm.set_df_property(field.df.fieldname, "reqd", 1);
      }

      if (
        field.df.read_only_depends_on &&
        frm.evaluate_depends_on_value(field.df.read_only_depends_on)
      ) {
        frm.set_df_property(field.df.fieldname, "read_only", 1);
      }

      if (
        field.df.depends_on &&
        frm.evaluate_depends_on_value(field.df.depends_on)
      ) {
        frm.set_value(field.df.fieldname, "hidden", 1);
      }
    });
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
    // Unmark mandatory fields
    frm.fields_list.forEach((field) => {
      if (field.df.reqd) {
        frm.set_df_property(field.df.fieldname, "reqd", 0);
      }
    });
    $submitBtn.click();
  }

  function handleCustomSaveAndSubmit(e) {
    frm.set_value("submitted", 1);
    $submitBtn.click();
  }
});
