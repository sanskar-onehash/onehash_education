// Fixes overflowing S.No.
frappe._messages["No.:Title of the 'row number' column"] = "S.No.";
clientsideStylesFix();

const LOCAL_STORAGE_DOC_KEY = "custom_doc";

frappe.ready(function () {
  const frm = frappe.web_form;
  const frmDoc = frappe.web_form_doc;
  const $submitBtn = $(".submit-btn");
  const $discardBtn = $(".discard-btn.btn");
  const $editBtn = $(".edit-button.btn");

  setupEducation();
  setupForm();

  function setupEducation() {
    window.education = {};
    education.before_submit_events = [];
    education.before_submit = function (fn) {
      education.before_submit_events.push(fn);
    };
  }

  function setupForm() {
    setupFormUI();
    loadFromLocalStorage();
    runCustomScript();
    setupListeners();
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

  function loadFromLocalStorage() {
    const lastDoc = getLocalStorageDoc();
    for (let key in lastDoc) {
      if (!frm.fields_dict[key] || frm.fields_dict[key].df.hidden) {
        continue;
      }

      if ($.isArray(frm.doc[key])) {
        let udpated = false;
        if (frm.doc[key].length === lastDoc[key].length) {
          for (let i = 0; i < frm.doc[key].length; i++) {
            for (let childKey in frm.doc[key][i]) {
              if (frm.doc[key][i][childKey] !== lastDoc[key][i][childKey]) {
                udpated = true;
                break;
              }
            }
            if (udpated) {
              break;
            }
          }
        } else {
          udpated = true;
        }
        if (udpated) {
          frm.fields_dict[key].doc[key] = lastDoc[key];
          frm.fields_dict[key].refresh();
        }
      } else if (frm.doc[key] !== lastDoc[key]) {
        try {
          frm.set_value(key, lastDoc[key]);
        } catch (err) {
          //
        }
      }
    }
  }

  function setupListeners() {
    $("body").click((e) => {
      const stepIdEl = e.target.closest("[data-step-id]");
      if (stepIdEl) {
        handleStepClick(e, stepIdEl);
      }
    });

    $("body").on(
      "change, input, select, textarea, click",
      handleDoctypeUpdates,
    );
    $discardBtn[0]?.addEventListener("click", handleDiscard, true);
  }

  function handleStepClick(e, stepIdEl) {
    frm.current_section = +stepIdEl.dataset.stepId;
    frm.toggle_section();
  }

  function handleDoctypeUpdates() {
    updateLocalStorageDoc(frm.get_values(true, false));
  }

  function handleDiscard() {
    clearLocalStorageDoc();
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

    const $customDiscardBtn = $(
      `<div class='btn discard-btn-custom btn-default'>Discard</div>`,
    );
    $customDiscardBtn.click(handleCustomDiscard);
    $customDiscardBtn.after($discardBtn);

    $submitBtn.hide();
    // $discardBtn.hide();
  }

  function handleCustomDiscard() {
    if (frappe.form_dirty) {
      frappe.warn(
        __("Discard?"),
        __("Are you sure you want to discard the changes?"),
        discardForm,
        __("Discard"),
      );
    } else {
      discardForm();
    }
    return false;
  }

  function discardForm() {
    let path = window.location.href;
    // remove new or edit after last / from url
    path = path.substring(0, path.lastIndexOf("/"));

    clearLocalStorageDoc();
    window.location.href = path;
  }

  function handleCustomSave(e) {
    handleSave();
  }

  async function handleCustomSaveAndSubmit(e) {
    await frm.set_value("submitted", 1);
    validateMandatories();

    await triggerBeforeSubmit(frm);
    handleSave();
  }

  function handleSave() {
    clearLocalStorageDoc();
    setFormCompletion(frm);
    $submitBtn.click();
  }

  async function triggerBeforeSubmit(frm) {
    return await Promise.all(
      education.before_submit_events.map(function (fn) {
        return fn(frm);
      }),
    );
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

function getLocalStorageDoc() {
  return JSON.parse(window.localStorage.getItem(LOCAL_STORAGE_DOC_KEY) || "{}");
}

function updateLocalStorageDoc(doc) {
  const preparedDoc = { ...doc };
  delete preparedDoc.name;
  window.localStorage.setItem(
    LOCAL_STORAGE_DOC_KEY,
    JSON.stringify(preparedDoc),
  );
}

function clearLocalStorageDoc() {
  window.localStorage.removeItem(LOCAL_STORAGE_DOC_KEY);
}

function setFormCompletion(frm) {
  let totalFields = 0.0;
  let filledFields = 0.0;

  for (let field of frm.fields_list) {
    if (frappe.model.layout_fields.includes(field.df.fieldtype)) {
      continue;
    }

    if (
      !field.df.depends_on ||
      field.layout.evaluate_depends_on_value(field.df.depends_on)
    ) {
      totalFields++;

      if (frm.doc[field.df.fieldname]) {
        filledFields++;
      }
    }
  }

  frm.set_value("form_completion", (filledFields / totalFields) * 100);
}
