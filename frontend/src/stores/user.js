import { defineStore } from 'pinia'
import { createResource } from 'frappe-ui'

export const usersStore = defineStore('education-users', () => {
  const user = createResource({
    url: 'onehash_education.api.get_user_info',
    cache: 'User',
    initialData: [],
    onError(error) {
      console.log(error)
      console.log(error.exc_type)
      if (error && error.exc_type === 'AuthenticationError') {
        window.location.href = '/login'
      }
    },
  })

  return {
    user,
  }
})
