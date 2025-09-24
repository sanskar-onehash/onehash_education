import { defineStore } from 'pinia'
import { ref } from 'vue'
import { createResource } from 'frappe-ui'

export const studentStore = defineStore('education-student', () => {
  const studentInfo = ref({})
  const currentStudentInfo = ref({})

  const student = createResource({
    url: 'onehash_education.api.get_students',
    onSuccess(info) {
      if (!info) {
        window.location.href = '/'
      }

      studentInfo.value = info
      currentStudentInfo.value = info[0]
    },
    onError(err) {
      console.error(err)
    },
  })

  function getStudentInfo() {
    return studentInfo
  }

  function getCurrentStudentInfo() {
    return currentStudentInfo
  }

  return {
    student,
    studentInfo,
    getStudentInfo,
    getCurrentStudentInfo,
  }
})
