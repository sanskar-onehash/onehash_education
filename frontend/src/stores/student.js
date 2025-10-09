import { defineStore } from 'pinia'
import { ref } from 'vue'
import { createResource } from 'frappe-ui'

export const useStudentStore = defineStore('education-student', () => {
  const studentInfo = ref([])
  const currentStudentInfo = ref(null)

  const STUDENT_STORAGE_KEY = 'current_student_id'

  const student = createResource({
    url: 'onehash_education.api.get_students',
    onSuccess(info) {
      if (!info || !Array.isArray(info) || info.length === 0) {
        return
      }

      studentInfo.value = info

      const urlParams = new URLSearchParams(window.location.search)
      const studentIdFromParam = urlParams.get('student')
      const studentIdFromStorage = localStorage.getItem(STUDENT_STORAGE_KEY)

      let matchedStudent = null

      if (studentIdFromParam) {
        matchedStudent = info.find((s) => s.id === studentIdFromParam)
      }

      if (!matchedStudent && studentIdFromStorage) {
        matchedStudent = info.find((s) => s.id === studentIdFromStorage)
      }

      currentStudentInfo.value = matchedStudent || info[0]

      if (currentStudentInfo.value?.id) {
        localStorage.setItem(STUDENT_STORAGE_KEY, currentStudentInfo.value.id)
      }
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
    const student = studentInfo.value[idx]
    currentStudentInfo.value = student

    if (student?.id) {
      localStorage.setItem(STUDENT_STORAGE_KEY, student.id)
    }
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
