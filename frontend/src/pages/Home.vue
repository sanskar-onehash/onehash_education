<template>
  <div :id="PAGE_NAME" class="min-h-screen bg-gray-50 py-8 px-6">
    <div class="container mx-auto max-w-7xl">
      <Card class="mb-8 p-8 bg-white shadow-lg rounded-lg">
        <div class="flex flex-col items-center">
          <div
            class="w-32 h-32 flex items-center justify-center bg-indigo-100 rounded-full border-4 border-indigo-600 mb-6"
          >
            <img
              v-if="currentStudent.student_image"
              :src="currentStudent.student_image"
              alt="Profile Picture"
              class="w-full h-full rounded-full object-cover"
            />
            <User2
              v-else
              name="user"
              color="#ededed"
              class="w-20 h-20 text-indigo-600"
            />
          </div>

          <div class="text-center">
            <h2 class="text-2xl font-bold text-gray-900">
              {{ currentStudent.student_name }}
            </h2>
            <p class="text-md text-gray-500 mt-1">
              Student ID:
              <span class="font-semibold">{{ currentStudent.id }}</span>
            </p>
            <p
              v-if="currentEnrollments.length"
              class="text-md font-semibold text-indigo-700 mt-2"
            >
              {{ currentEnrollments[0].year_group }} -
              <span class="font-normal">{{
                currentEnrollments[0].academic_term
              }}</span>
            </p>
          </div>
        </div>
      </Card>

      <div class="flex flex-col sm:flex-row justify-between gap-8">
        <Card
          v-if="currentEnrollments.length"
          class="p-6 shadow-lg rounded-lg w-full sm:w-1/2"
          title="Current Enrollments"
        >
          <ul class="space-y-2 text-gray-600">
            <li v-for="enrollment in currentEnrollments" :key="enrollment.name">
              {{ `${enrollment.year_group} - ${enrollment.academic_term}` }}
            </li>
          </ul>
        </Card>

        <Card
          v-if="upcomingEnrollments.length"
          class="p-6 shadow-lg rounded-lg w-full sm:w-1/2"
          title="Upcoming Enrollments"
        >
          <ul class="space-y-2 text-gray-600">
            <li v-for="enrollment in upcomingEnrollments" :key="enrollment.name">
              {{ `${enrollment.year_group} - ${enrollment.academic_term}` }}
            </li>
          </ul>
        </Card>
      </div>

      <div class="space-y-8 mt-8">
        <Card
          v-if="outstandingInvoices.length"
          class="p-6 shadow-lg rounded-lg"
          title="Outstanding Invoices"
        >
          <div class="space-y-4">
            <div
              v-for="row in outstandingInvoices"
              :key="row.name"
              class="flex flex-col sm:flex-row justify-between sm:items-center gap-4 border-b pb-4"
            >
              <div class="space-y-1">
                <p class="font-semibold">{{ row.name }}</p>
                <p class="text-sm text-gray-500">
                  Amount Due: {{ row.payable_amount_formatted }}
                </p>
                <div
                  class="flex gap-6 text-gray-500 space-y-1 sm:flex-col sm:gap-0"
                >
                  <p class="text-xs">Invoice Date: {{ row.posting_date }}</p>
                  <p class="text-xs">Due Date: {{ row.due_date }}</p>
                </div>
              </div>
              <Button
                @click="payInvoice(row)"
                class="hover:bg-indigo-700 hover:text-white flex items-center justify-center"
                icon-left="credit-card"
                label="Pay Now"
              />
            </div>
          </div>
        </Card>

        <Card
          v-if="upcomingInvoices.length"
          class="p-6 shadow-lg rounded-lg"
          title="Upcoming Invoices"
        >
          <div class="space-y-4">
            <div
              v-for="row in upcomingInvoices"
              :key="row.name"
              class="flex flex-col sm:flex-row justify-between sm:items-center gap-4 border-b pb-4"
            >
              <div class="space-y-1">
                <p class="font-semibold">{{ row.name }}</p>
                <p class="text-sm text-gray-500">
                  Amount Due: {{ row.payable_amount_formatted }}
                </p>
                <div
                  class="flex gap-6 text-gray-500 space-y-1 sm:flex-col sm:gap-0"
                >
                  <p class="text-xs">Invoice Date: {{ row.posting_date }}</p>
                  <p class="text-xs">Due Date: {{ row.due_date }}</p>
                </div>
              </div>
              <Button
                @click="payInvoice(row)"
                class="hover:bg-indigo-700 hover:text-white flex items-center justify-center"
                icon-left="credit-card"
                label="Pay Now"
              />
            </div>
          </div>
        </Card>
      </div>
    </div>
  </div>
</template>

<script setup>
import { reactive } from 'vue'
import { useRouter } from 'vue-router'
import { useStudentStore } from '@/stores/student'
import { Button, Card, createResource } from 'frappe-ui'
import { User2 } from 'lucide-vue-next'

const PAGE_NAME = 'home'

const router = useRouter()
const studentStore = useStudentStore()

const currentEnrollments = reactive([])
const upcomingEnrollments = reactive([])
const outstandingInvoices = reactive([])
const upcomingInvoices = reactive([])

const currentStudent = studentStore.getCurrentStudentInfo()

function fetchStudentInvoices() {
  createResource({
    url: 'onehash_education.api.get_invoices_to_pay',
    params: {
      customer: studentStore.currentStudentInfo.customer,
    },
    onSuccess: (invoices) => {
      if (!invoices) {
        return
      }
      const outstandingInvoicesData = []
      const upcomingInvoicesData = []
      const today = new Date()

      invoices.forEach((invoice) => {
        const dueDate = new Date(invoice.due_date)

        if (dueDate < today) {
          outstandingInvoicesData.push(invoice)
        } else {
          upcomingInvoicesData.push(invoice)
        }
      })

      outstandingInvoices.splice(
        0,
        outstandingInvoices.length,
        ...outstandingInvoicesData,
      )
      upcomingInvoices.splice(
        0,
        upcomingInvoices.length,
        ...upcomingInvoicesData,
      )
    },
    auto: true,
  })
}

function fetchStudentCurrentPorgrams() {
  if (studentStore.currentStudentInfo.is_applicant) {
    if (currentEnrollments.length) {
      currentEnrollments.splice(0, currentEnrollments.length)
    }
    return
  }
  createResource({
    url: 'onehash_education.onehash_education.doctype.enrollment.enrollment.get_active_enrollments',
    params: {
      student: studentStore.currentStudentInfo.id,
    },
    onSuccess: (enrollments) => {
      if (enrollments) {
        currentEnrollments.splice(0, currentEnrollments.length, ...enrollments)
      }
    },
    auto: true,
  })
}

function fetchStudentUpcomingEnrollments() {
  if (studentStore.currentStudentInfo.is_applicant) {
    if (upcomingEnrollments.length) {
      upcomingEnrollments.splice(0, upcomingEnrollments.length)
    }
    return
  }
  createResource({
    url: 'onehash_education.onehash_education.doctype.enrollment.enrollment.get_upcoming_enrollments',
    params: {
      student: studentStore.currentStudentInfo.id,
    },
    onSuccess: (enrollments) => {
      if (enrollments) {
        upcomingEnrollments.splice(0, upcomingEnrollments.length, ...enrollments)
      }
    },
    auto: true,
  })
}

function fetchDynamicData() {
  fetchStudentInvoices()
  fetchStudentCurrentPorgrams()
  fetchStudentUpcomingEnrollments()
}

fetchDynamicData()

studentStore.$subscribe(fetchDynamicData)

const payInvoice = (invoice) => {
  router.push('/pay-fee')
}
</script>
