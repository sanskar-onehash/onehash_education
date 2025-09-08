const studentApplicationTasks = [];
if (window.location.pathname === "/student-application/list") {
  $(".button-new").remove();

  studentApplicationTasks.push(() => {
    const webFormListInterval = setInterval(() => {
      if (!frappe.web_form_list || !frappe.web_form_list.data) {
        return;
      }
      clearInterval(webFormListInterval);

      if (frappe.web_form_list.data.length === 1) {
        window.location.href =
          window.location.origin +
          `/student-application/${frappe.web_form_list.data[0].name}`;
      }
    }, 300);
  });
} else if (window.location.pathname === "/student-application/new") {
  redirectToStudentApplicationList();
} else if (window.location.pathname === "/") {
  studentApplicationTasks.push(() => {
    if (
      frappe.web_form_doc &&
      frappe.web_form_doc.title === "Student Application"
    ) {
      redirectToStudentApplicationList();
    }
  });
}

function redirectToStudentApplicationList() {
  window.location.href = window.location.origin + "/student-application/list";
}

frappe.ready(() => {
  studentApplicationTasks.forEach((task) => task());
});
