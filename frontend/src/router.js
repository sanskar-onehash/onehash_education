import { createRouter, createWebHistory } from 'vue-router'
import { usersStore } from '@/stores/user'
import { sessionStore } from '@/stores/session'
import { useStudentStore } from '@/stores/student'

const routes = [
  { path: '/', name: 'Home', component: () => import('@/pages/Home.vue') },
  {
    path: '/pay-fee',
    name: 'Pay Fees',
    component: () => import('@/pages/PayFee.vue'),
  },
  {
    path: '/transactions',
    name: 'Transactions',
    component: () => import('@/pages/Transactions.vue'),
  },
  {
    path: '/applications',
    name: 'Applications',
    component: () => import('@/pages/Applications.vue'),
  },

  // {
  //   path: '/:catchAll(.*)',
  //   redirect: '/transactions',
  // },
]

let router = createRouter({
  history: createWebHistory('/student-portal'),
  routes,
})

router.beforeEach(async (to, from, next) => {
  const { isLoggedIn } = sessionStore()
  const { user } = usersStore()
  const studentStore = useStudentStore()

  if (!isLoggedIn) {
    window.location.href = '/login'
    return
  }

  if (user.data.length === 0) {
    await user.reload()
    await studentStore.student.reload()
  }

  if (to.query.student) {
    const { student, ...rest } = to.query
    return next({ path: to.path, query: rest, replace: true })
  }

  next()
})

export default router
