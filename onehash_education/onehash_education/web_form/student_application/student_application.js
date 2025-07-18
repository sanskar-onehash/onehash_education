frappe.ready(function () {
  const frm = frappe.web_form;
  const $submitBtn = $(".submit-btn");

  setupForm();

  function setupForm() {
    setupFormUI();
  }

  function setupFormUI() {
    // `FIXES:` clientside app web.html template
    // Wrap page-content in container
    $(".page-content-wrapper").append(
      $("<div class='container my-4 fix-container'><div>"),
    );
    $(".page-content-wrapper .fix-container").append(
      $(".page-content-wrapper .page_content"),
    );

    addCustomActionButtons();
  }

  function addCustomActionButtons() {
    // Custom Save button
    const $customSaveBtn = $(
      `<div class='btn submit-btn-custom btn-info'>${frm.button_label}</div>`,
    );
    $customSaveBtn.click(handleCustomSave);

    // Custom Save & Submit Button
    const $customSaveAndSubmitBtn = $(
      `<div class='btn submit-btn-custom btn-warning'>Save & Submit</div>`,
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

  function handleCustomSaveAndSubmit(e) {
    frm.set_value("submitted", 1);
    $submitBtn.click();
  }
});

