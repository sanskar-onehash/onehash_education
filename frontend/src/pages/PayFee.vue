<template>
  <div class="px-5 py-6 space-y-6" :id="PAGE_NAME">
    <h2 class="text-2xl font-semibold">Pay Fees</h2>

    <MissingData
      v-if="invoices.length === 0"
      message="No pending invoices to pay"
    />

    <div v-else class="space-y-4">
      <div class="flex justify-end">
        <Button
          :label="areAllSelected ? 'Unselect All' : 'Select All'"
          variant="outline"
          size="sm"
          @click="toggleSelectAll"
        />
      </div>
      <Card
        v-for="(invoice, idx) in invoices"
        :key="invoice.name"
        :data-invoice-id="invoice.name"
        class="border shadow-sm"
        @click="handleInvoiceCardClick(invoice)"
      >
        <div class="flex items-center justify-between bg-gray-50 px-4 py-3">
          <div class="flex items-center space-x-3">
            <div @click.stop>
              <Checkbox
                v-model="invoice.selected"
                :disabled="invoice.disabled"
                :ref="
                  (el) =>
                    (checkboxRefs[invoice.name] =
                      el?.$el?.querySelector('input'))
                "
                @update:model-value="calculateTotal"
              />
            </div>
            <div>
              <div class="font-medium">Invoice: {{ invoice.name }}</div>
              <div class="text-sm text-gray-500">
                Due Date: {{ invoice.due_date }}
              </div>
            </div>
          </div>
        </div>

        <div class="px-4 py-3 bg-white space-y-2">
          <div
            v-for="(item, j) in invoice.items"
            :key="j"
            class="flex justify-between border-b pb-2"
          >
            <div class="text-sm text-gray-700">{{ item.item_name }}</div>
            <div
              class="text-sm font-medium"
              :class="{
                'text-green-600': item.item_amount > 0,
                'text-red-600': item.item_amount < 0,
              }"
            >
              {{ item.item_amount_formatted }}
            </div>
          </div>

          <div class="flex justify-between pt-3 font-semibold">
            <span>Invoice Total</span>
            <span>{{ invoice.grand_total_formatted }}</span>
          </div>

          <div
            v-if="
              invoice.grand_total_formatted !== invoice.payable_amount_formatted
            "
            class="flex justify-between pt-1 font-semibold"
          >
            <span>Payable Amount</span>
            <span>{{ invoice.payable_amount_formatted }}</span>
          </div>
        </div>
      </Card>
    </div>

    <div
      v-if="invoices.length > 0"
      class="border-t pt-6 flex justify-between items-center"
    >
      <div class="text-xl font-bold">Total to Pay</div>
      <div class="text-2xl font-bold text-blue-600">
        {{ formatCurrency(totalAmount, currency) }}
      </div>
    </div>

    <div v-if="invoices.length > 0" class="text-right">
      <Button
        label="Pay Now"
        icon-left="credit-card"
        variant="solid"
        size="md"
        id="btn-pay_now"
        :disabled="selectedInvoices.length === 0"
        @click="onPayNow"
      />
    </div>
  </div>
  <Dialog
    v-model="showNoSelectionDialog"
    :options="{
      title: 'No Invoices Selected',
      message: 'Please select at least one invoice to proceed with payment.',
      size: 'md',
      icon: {
        name: 'alert-triangle',
        appearance: 'warning',
      },
      actions: [
        {
          label: 'OK',
          variant: 'solid',
          onClick: () => {
            showNoSelectionDialog = false
          },
        },
      ],
    }"
  />
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { Button, Card, Checkbox, createResource, Dialog } from 'frappe-ui'
import { useStudentStore } from '@/stores/student'
import { useExternalScriptApi } from '@/stores/external_script_api'
import MissingData from '@/components/MissingData.vue'

const PAGE_NAME = 'pay-fee'

const studentStore = useStudentStore()
const externalScriptApiStore = useExternalScriptApi()

let invoices = reactive([])

const totalAmount = ref(0)
const currency = ref('INR')
const showNoSelectionDialog = ref(false)
const checkboxRefs = reactive({})

const selectedInvoices = computed(() => invoices.filter((inv) => inv.selected))
const areAllSelected = computed(() => {
  return (
    invoices.length > 0 &&
    invoices.every((inv) => {
      const el = checkboxRefs[inv.name]
      return el?.disabled || inv.selected
    })
  )
})

function fetchStudentInvoices() {
  const invoiceResource = createResource({
    url: 'onehash_education.api.get_invoices_to_pay',
    params: {
      customer: studentStore.currentStudentInfo.customer,
    },
    onSuccess: (response) => {
      invoices.splice(
        0,
        invoices.length,
        ...response.map((invoice) => ({
          ...invoice,
          selected: true,
          disabled: invoice.payable_amount <= 0,
        })),
      )
      calculateTotal()
    },
    auto: true,
  })
}

fetchStudentInvoices()
studentStore.$subscribe(fetchStudentInvoices)

function toggleInvoiceSelection(invoice) {
  invoice.selected = !invoice.selected
  calculateTotal()
}

function toggleSelectAll() {
  const newValue = !areAllSelected.value

  invoices.forEach((inv) => {
    const checkboxEl = checkboxRefs[inv.name]
    if (checkboxEl && !checkboxEl.disabled) {
      inv.selected = newValue
    }
  })

  calculateTotal()
}

function calculateTotal() {
  if (selectedInvoices.value.length) {
    currency.value = selectedInvoices.value[0].currency
  }
  totalAmount.value = selectedInvoices.value.reduce(
    (sum, inv) => sum + inv.payable_amount,
    0,
  )
}

function onPayNow() {
  if (selectedInvoices.value.length === 0) {
    showNoSelectionDialog.value = true
    return
  }

  externalScriptApiStore.emit('pay-now', {
    invoices: selectedInvoices.value,
    student: studentStore.currentStudentInfo,
  })
}

onMounted(() => {
  calculateTotal()

  externalScriptApiStore.currentPage = PAGE_NAME
  externalScriptApiStore.emit('mounted', PAGE_NAME)
})

function handleInvoiceCardClick(invoice) {
  const selection = window.getSelection()
  if (selection && selection.toString().length > 0) {
    return
  }

  toggleInvoiceSelection(invoice)
}

function formatCurrency(val, cur) {
  return new Intl.NumberFormat('en-IN', {
    style: 'currency',
    currency: cur || 'INR',
  }).format(val)
}
</script>
