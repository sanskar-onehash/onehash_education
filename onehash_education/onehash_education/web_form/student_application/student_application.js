// Fixes overflowing S.No.
frappe._messages["No.:Title of the 'row number' column"] = "S.No.";
// clientsideStylesFix();

// Increase link fields list size
frappe.boot.sysdefaults.link_field_results_limit = 50;

const LOCAL_STORAGE_DOC_KEY = "custom_doc";

async function fixLanguages() {
  for (let language of frappe.web_form.doc.language_proficiency || []) {
    await frappe.utils.fetch_link_title("Language", language.language);
  }
  for (let row of frappe.web_form.fields_dict.language_proficiency.grid
    .grid_rows) {
    row.refresh();
  }
}

frappe.ready(function () {
  const frm = frappe.web_form;
  const frmDoc = frappe.web_form_doc;
  const $submitBtn = $(".submit-btn");
  const $discardBtn = $(".discard-btn.btn");
  const $editBtn = $(".edit-button.btn");

  fixLanguages();
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

    refreshLinkFilters();
    refreshCalculatedFields();

    setupFormListeners();
    setupDOMListeners();

    runCustomScript();

    customizePhoneFields();
  }

  function setupFormListeners() {
    frm.on("date_of_birth", calculateAndSetAge);
    frm.on("correspondence_country", handleCorrespondanceCountryChange);
    frm.on("correspondence_state", handleCorrespondanceStateChange);
    frm.on("permanent_country", handlePermanentCountryChange);
    frm.on("permanent_state", handlePermanentStateChange);
    frm.on("academic_year", handleAcademicYearChange);
  }

  function refreshCalculatedFields() {
    calculateAndSetAge();
  }

  function calculateAndSetAge() {
    const dateOfBirth = frm.get_value("date_of_birth");
    const lastAge = frm.get_value("age_as_on");
    if (!dateOfBirth && !lastAge) {
      return;
    } else if (!dateOfBirth) {
      frm.set_value("age_as_on", "");
      return;
    }

    const currentYear = new Date().getFullYear();
    const dob = new Date(dateOfBirth);
    const targetDate = new Date(`${currentYear}-08-01`); // 1st August

    if (dob > targetDate) {
      frappe.msgprint("Invalid Date of Birth.");
      frm.set_value("date_of_birth", "");
      return;
    }

    let years = targetDate.getFullYear() - dob.getFullYear();
    let months = targetDate.getMonth() - dob.getMonth();
    let days = targetDate.getDate() - dob.getDate();

    if (days < 0) {
      months -= 1;
      const prevMonth = new Date(
        targetDate.getFullYear(),
        targetDate.getMonth(),
        0,
      );
      days += prevMonth.getDate();
    }

    if (months < 0) {
      years -= 1;
      months += 12;
    }

    const age = `${years} years, ${months} months, and ${days} days`;
    if (age !== lastAge) {
      frm.set_value("age_as_on", age);
    }
  }

  function handleCorrespondanceCountryChange(field, value) {
    if (!value) {
      frm.set_value("correspondence_state", "");
      return;
    }
    refreshLinkFilters();
  }

  function handleCorrespondanceStateChange(field, value) {
    if (!value) {
      frm.set_value("correspondence_city", "");
      return;
    }
    refreshLinkFilters();
  }

  function handlePermanentCountryChange(field, value) {
    if (!value) {
      frm.set_value("permanent_state", "");
      return;
    }
    refreshLinkFilters();
  }

  function handlePermanentStateChange(field, value) {
    if (!value) {
      frm.set_value("permanent_city", "");
      return;
    }
    refreshLinkFilters();
  }

  function handleAcademicYearChange(field, academicYear) {
    handleYearGroupForAcademicYear(academicYear);
  }

  async function handleYearGroupForAcademicYear(academicYear) {
    frm.set_df_property("year_group", "hidden", 1);
    if (academicYear) {
      const { message: yearGroups } = await frappe.call({
        method: "onehash_education.api.get_admission_year_groups",
        args: { academic_year: academicYear },
      });
      frm.fields_dict.year_group.get_query = {
        name: ["in", yearGroups.map((yg) => yg.year_group)],
      };
      frm.set_df_property("year_group", "hidden", 0);
    }
  }

  function fixYearGroupAwesomeListSorting() {
    if (!frm.fields_dict.year_group.awesomplete?.sort) {
      return;
    }
    frm.fields_dict.year_group.awesomplete.sort = (a, b) => {
      const getSortValue = (item) => {
        const label = item.label?.trim() || "";

        // Pre-Nursery, Nursery, and Reception should come first
        if (label.startsWith("Pre-Nursery")) return 0;
        if (label.startsWith("Nursery")) return 1;
        if (label.startsWith("Reception")) return 2;

        // Handle dynamic Year entries like "Year 1 (KG 2)"
        const match = label.match(/^Year (\d+)/);
        if (match) {
          return 2 + parseInt(match[1], 10);
        }

        return Infinity;
      };

      return getSortValue(a) - getSortValue(b);
    };
  }

  function customizePhoneFields() {
    frm.fields_list.forEach((field) => {
      if (field.df.fieldtype === "Phone") {
        setupPhoneField(field);
      }
    });
  }

  function refreshLinkFilters() {
    if (frm.get_value("correspondence_country")) {
      frm.fields_dict.correspondence_state.get_query = () => ({
        filters: { country: frm.get_value("correspondence_country") },
      });
    }

    if (frm.get_value("correspondence_state")) {
      frm.fields_dict.correspondence_city.get_query = () => ({
        filters: { state: frm.get_value("correspondence_state") },
      });
    }

    if (frm.get_value("permanent_country")) {
      frm.fields_dict.permanent_state.get_query = () => ({
        filters: { country: frm.get_value("permanent_country") },
      });
    }

    if (frm.get_value("permanent_state")) {
      frm.fields_dict.permanent_city.get_query = () => ({
        filters: { state: frm.get_value("permanent_state") },
      });
    }
  }

  function setupPhoneField(field) {
    const originalReadOnly = field.df.read_only;
    field.df.read_only = true;
    field.refresh();

    const setFieldInputListeners = () => {
      field.$input.off("focus", handlePhoneInputFocus);
      field.$input.on("focus", handlePhoneInputFocus);

      field.df.read_only = originalReadOnly;
      field.refresh();
    };

    if (field.$input) {
      setFieldInputListeners();
    } else {
      // There is no event fired when input is ready,
      // the one which is fired: `field.df.on_make` doesn't consider
      // that the make_input can be an async function
      const inputWaitInterval = setInterval(() => {
        if (field.$input) {
          clearInterval(inputWaitInterval);
          setFieldInputListeners();
        }
      }, 150);
    }
  }

  function handlePhoneInputFocus(e) {
    const { fieldname } = this.dataset;
    const field = frm.fields_dict[fieldname];
    if (!field.country_code_picker.country) {
      field.$input.blur();
      field.$wrapper.popover("show");
    }
  }

  function setupFormUI() {
    const currentYear = new Date().getFullYear();
    const today = frappe.datetime.get_today();

    frm.set_df_property(
      "age_as_on",
      "label",
      `Age as on 1st August ${currentYear}`,
    );
    if (!frm.doc.submitted) {
      frm.set_value("date_of_declaration", today);
    }

    handleYearGroupForAcademicYear();
    fixYearGroupAwesomeListSorting();
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
    if (lastDoc.modified !== frm.doc.modified) {
      clearLocalStorageDoc();
      return;
    }

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

  function setupDOMListeners() {
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
    updateLocalStorageDoc({
      ...frm.get_values(true, false),
      modified: frm.doc.modified,
    });
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
    validateMandatories();

    await triggerBeforeSubmit(frm);
    await frm.set_value("submitted", 1);
    try {
      handleSave();
    } catch (err) {
      await frm.set_value("submitted", 0);
    }
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
