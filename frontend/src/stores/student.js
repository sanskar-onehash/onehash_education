import { defineStore } from 'pinia'
import { ref } from 'vue'
import { createResource } from 'frappe-ui'

export const studentStore = defineStore('education-student', () => {
  const studentInfo = ref({})

  const student = createResource({
    url: 'onehash_education.api.get_students',
    onSuccess(info) {
      if (!info) {
        window.location.href = '/'
      }

      studentInfo.value = info
    },
    onError(err) {
      console.error(err)
    },
  })

  function getStudentInfo() {
    return studentInfo
  }

  return {
    student,
    studentInfo,
    getStudentInfo,
  }
})
