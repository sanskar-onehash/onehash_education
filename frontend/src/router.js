import { createRouter, createWebHistory } from 'vue-router'
import { usersStore } from '@/stores/user'
import { sessionStore } from '@/stores/session'
import { studentStore } from '@/stores/student'

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
  },{
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

router.beforeEach(async (to, from) => {
  const { isLoggedIn, user: sessionUser } = sessionStore()
  const { user } = usersStore()
  const { student } = studentStore()

  if (!isLoggedIn) {
    window.location.href = '/login'
    return await next(false)
  }

  if (user.data.length === 0) {
    await user.reload()
  }
  await student.reload()
})

export default router
