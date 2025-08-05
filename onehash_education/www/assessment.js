document.addEventListener("DOMContentLoaded", function () {
  const form = document.getElementById("assessmentForm");
  if (!form) return;

  form.querySelectorAll(".password-toggle").forEach((toggle) => {
    toggle.addEventListener("click", function () {
      const input = this.previousElementSibling;
      if (input.type === "password") {
        input.type = "text";
        this.classList.add("visible");
      } else {
        input.type = "password";
        this.classList.remove("visible");
      }
    });
  });

  form
    .querySelectorAll(
      'textarea[maxlength], input[type="text"][maxlength], input[type="password"][maxlength]',
    )
    .forEach((el) => {
      const counter = document.createElement("span");
      counter.className = "char-counter";
      el.parentNode.appendChild(counter);
      const updateCounter = () => {
        counter.textContent = `${el.value.length}/${el.maxLength}`;
      };
      el.addEventListener("input", updateCounter);
      updateCounter();
    });

  form.addEventListener("submit", function (e) {
    let valid = true;
    form.querySelectorAll("[required]").forEach((input) => {
      if (!input.value.trim()) {
        input.classList.add("input-error");
        valid = false;
      } else {
        input.classList.remove("input-error");
      }
    });
    if (!valid) {
      e.preventDefault();
      form.querySelector(".form-error")?.remove();
      const error = document.createElement("div");
      error.className = "form-error";
      error.textContent = "Please fill all required fields.";
      form.prepend(error);
      window.scrollTo({ top: 0, behavior: "smooth" });
    }
  });

  form.querySelectorAll(".multi-choice-group").forEach((group) => {
    const max = parseInt(group.dataset.max, 10);
    if (!max) return;
    group.querySelectorAll('input[type="checkbox"]').forEach((checkbox) => {
      checkbox.addEventListener("change", function () {
        const checked = group.querySelectorAll(
          'input[type="checkbox"]:checked',
        );
        if (checked.length > max) {
          this.checked = false;
        }
      });
    });
  });

  form.querySelectorAll('input[type="date"]').forEach((input) => {
    if (input.type !== "date") {
    }
  });

  const groups = Array.from(document.querySelectorAll(".question-group"));
  const prevBtn = document.getElementById("prev-page-btn");
  const nextBtn = document.getElementById("next-page-btn");
  const pageInfo = document.getElementById("page-info");

  let currentPage = 0;
  const totalPages = groups.length > 1 ? groups.length - 1 : 1;

  function allVisibleQuestionsAnswered() {
    const visibleGroups = groups.filter((g) => g.style.display !== "none");
    let allAnswered = true;
    visibleGroups.forEach((group) => {
      const requiredInputs = group.querySelectorAll(
        ".question-block input[required], .question-block textarea[required]",
      );
      requiredInputs.forEach((input) => {
        if (input.type === "checkbox" || input.type === "radio") {
          const name = input.name;
          const groupInputs = group.querySelectorAll(`[name='${name}']`);
          const anyChecked = Array.from(groupInputs).some((i) => i.checked);
          if (!anyChecked) allAnswered = false;
        } else if (!input.value.trim()) {
          allAnswered = false;
        }
      });
    });
    return allAnswered;
  }

  function updateSubmitButton() {
    const submitBtn = document.getElementById("submit-btn");
    if (submitBtn) {
      submitBtn.disabled = !allVisibleQuestionsAnswered();
    }
  }

  function showPage(page) {
    groups.forEach((group, idx) => {
      let visible = false;
      if (page === 0) {
        visible = idx === 0 || idx === 1;
      } else {
        visible = idx === page + 1;
      }
      group.style.display = visible ? "" : "none";
      const fields = group.querySelectorAll("input, textarea, select");
      fields.forEach((f) => {
        if (visible) {
          f.removeAttribute("disabled");
        } else {
          f.setAttribute("disabled", "disabled");
        }
      });
    });
    if (pageInfo) {
      pageInfo.textContent = `Page ${page + 1} of ${totalPages}`;
    }
    if (prevBtn) prevBtn.disabled = page === 0;
    if (nextBtn) nextBtn.disabled = page >= totalPages - 1;
    updateSubmitButton();
  }

  function bindInputValidation() {
    document.addEventListener("input", updateSubmitButton);
    document.addEventListener("change", updateSubmitButton);
    document.addEventListener("keyup", updateSubmitButton);
  }
  bindInputValidation();

  if (groups.length > 0) {
    showPage(currentPage);
  }
  if (prevBtn) {
    prevBtn.addEventListener("click", function () {
      if (currentPage > 0) {
        currentPage--;
        showPage(currentPage);
      }
    });
  }
  if (nextBtn) {
    nextBtn.addEventListener("click", function () {
      if (currentPage < totalPages - 1) {
        currentPage++;
        showPage(currentPage);
      }
    });
  }
});
