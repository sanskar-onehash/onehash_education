const studentApplicationTasks = []
if (window.location.pathname === '/student-application/list') {
  $('.button-new').remove()

  studentApplicationTasks.push(runCustomScript)
} else if (window.location.pathname === '/student-application/new') {
  redirectToStudentApplicationList()
} else if (window.location.pathname === '/') {
  studentApplicationTasks.push(() => {
    if (
      frappe.web_form_doc &&
      frappe.web_form_doc.title === 'Student Application'
    ) {
      redirectToStudentApplicationList()
    }
  })
}

if (window.location.pathname.startsWith('/student-application')) {
  if (window.self !== window.top) {
    // Inside Iframe
    $('.navbar').hide()
  }

  function triggerHeightResize() {
    const height = document.body.scrollHeight
    window.parent.postMessage({ height }, '*')
  }

  window.addEventListener('DOMContentLoaded', triggerHeightResize)
  window.addEventListener('load', triggerHeightResize)
  window.addEventListener('resize', triggerHeightResize)
}

function redirectToStudentApplicationList() {
  window.location.href = window.location.origin + '/student-application/list'
}

frappe.ready(() => {
  studentApplicationTasks.forEach((task) => task())
})

function runCustomScript() {
  if (frappe.web_form_doc.custom_script) {
    const customScript = new Function(frappe.web_form_doc.custom_script)
    customScript()
  }
  if (frappe.web_form_doc.custom_style) {
    const $style = $(`<style>${frappe.web_form_doc.custom_style}</style>`)
    $('head').append($style)
  }
}
