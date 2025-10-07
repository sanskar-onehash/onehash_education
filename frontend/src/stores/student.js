import { defineStore } from 'pinia'
import { ref } from 'vue'
import { createResource } from 'frappe-ui'

export const useStudentStore = defineStore('education-student', () => {
  const studentInfo = ref([])
  const currentStudentInfo = ref(null)

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

  function setCurrentStudent(idx) {
    currentStudentInfo.value = studentInfo.value[idx]
  }

  return {
    student,
    studentInfo,
    currentStudentInfo,
    getStudentInfo,
    getCurrentStudentInfo,
    setCurrentStudent,
  }
})
