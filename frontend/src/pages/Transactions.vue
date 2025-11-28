<template>
  <div :id="PAGE_NAME">
    <div v-if="tableData.rows.length > 0" class="px-5 py-4">
      <ListView
        :columns="tableData.columns"
        :rows="tableData.rows"
        :options="{
          selectable: false,
          showTooltip: false,
          onRowClick: () => {},
        }"
        row-key="id"
        v-if="tableData.rows.length > 0"
      >
        <ListHeader>
          <ListHeaderItem
            v-for="column in tableData.columns"
            :key="column.key"
            :item="column"
          />
        </ListHeader>
        <ListRow
          v-for="row in tableData.rows"
          :key="row.id"
          :row="row"
          v-slot="{ column, item }"
        >
          <ListRowItem :item="item" :align="column.align">
            <Badge
              v-if="column.key === 'status'"
              variant="subtle"
              :theme="badgeColor(row.status) || 'gray'"
              size="md"
              :label="item"
            />

            <Button
              v-if="column.key === 'invoice'"
              @click="openInvoicePDF(row)"
              class="hover:bg-gray-900 hover:text-white"
              icon-left="download"
              label="Download Invoice"
            />

            <Button
              v-if="column.key === 'receipt' && row.receipt"
              @click="openReceiptPDF(row)"
              class="hover:bg-gray-900 hover:text-white"
              icon-left="download"
              label="Download Receipt"
            />
            <Button
              v-if="
                column.key === 'receipt' &&
                !['Paid', 'Return'].includes(row.status)
              "
              @click="payInvoice(row)"
              class="hover:bg-gray-900 hover:text-white flex flex-column items-center justify-center"
              icon-left="credit-card"
              label="Pay Now"
            />
          </ListRowItem>
        </ListRow>
      </ListView>
    </div>

    <div v-else>
      <MissingData message="No Transactions found" />
    </div>
  </div>
</template>

<script setup>
import { reactive } from 'vue'
import {
  ListView,
  ListHeader,
  ListHeaderItem,
  ListRow,
  ListRowItem,
  Badge,
  createResource,
} from 'frappe-ui'
import { useRouter } from 'vue-router'
import { useStudentStore } from '@/stores/student'
import MissingData from '@/components/MissingData.vue'

const PAGE_NAME = 'transactions'

const router = useRouter()
const studentStore = useStudentStore()

function fetchTransactions() {
  const feesResource = createResource({
    url: 'onehash_education.api.get_customer_transactions',
    params: {
      customer: studentStore.currentStudentInfo.customer,
    },
    onSuccess: (response) => {
      invoiceFormat = response?.invoice_format
      receiptFormat = response?.receipt_format
      const transactions = (response?.transactions || []).sort((a, b) => {
        const statusOrder = {
          Overdue: 0,
          Unpaid: 1,
          'Partly Paid': 2,
          Return: 3,
          Paid: 4,
        }

        const statusA = statusOrder[a.status]
        const statusB = statusOrder[b.status]

        if (statusA !== statusB) {
          return statusA - statusB
        }
      })
      tableData.rows = transactions
    },
    auto: true,
  })
}

fetchTransactions()
studentStore.$subscribe(fetchTransactions)

const tableData = reactive({
  rows: [],
  columns: [
    {
      label: 'Year Group',
      key: 'year_group',
      width: 1,
    },
    {
      label: 'Status',
      key: 'status',
      width: 1,
    },
    {
      label: 'Payment Date',
      key: 'payment_date',
      width: 1,
    },
    {
      label: 'Due Date',
      key: 'due_date',
      width: 1,
    },
    {
      label: 'Amount',
      key: 'formatted_amount',
      width: 1,
    },
    {
      label: 'Invoice',
      key: 'invoice',
      width: 1,
    },
    {
      label: 'Receipt',
      key: 'receipt',
      width: 1,
    },
  ],
})

let invoiceFormat = 'Standard'
let receiptFormat = 'Standard'
const openInvoicePDF = (row) => {
  let url = `/api/method/frappe.utils.print_format.download_pdf?
		doctype=${encodeURIComponent('Sales Invoice')}
		&name=${encodeURIComponent(row.invoice)}
		&format=${encodeURIComponent(invoiceFormat)}
	`
  window.open(url, '_blank')
}
const openReceiptPDF = (row) => {
  let url = `/api/method/frappe.utils.print_format.download_pdf?
		doctype=${encodeURIComponent('Payment Entry')}
		&name=${encodeURIComponent(row.receipt)}
		&format=${encodeURIComponent(receiptFormat)}
	`
  window.open(url, '_blank')
}

const payInvoice = (_) => {
  router.push('/pay-fee')
}

const badgeColor = (status) => {
  const badgeColorMap = {
    Paid: 'green',
    Return: 'green',
    Unpaid: 'orange',
    Overdue: 'red',
    'Partly Paid': 'blue',
  }
  return badgeColorMap[status]
}
</script>
