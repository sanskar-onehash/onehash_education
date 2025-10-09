<template>
  <div
    class="flex h-full flex-col justify-between transition-all duration-300 ease-in-out"
    :class="isSidebarCollapsed ? 'w-12' : 'w-56'"
    :id="COMPONENT_NAME"
  >
    <div class="flex flex-col overflow-hidden">
      <UserDropdown
        class="p-2"
        :isCollapsed="isSidebarCollapsed"
        :educationSettings="
          !educationSettings.loading && educationSettings.data
        "
      />
      <div class="flex flex-col">
        <SidebarLink
          :label="link.label"
          :to="link.to"
          v-for="link in links"
          :isCollapsed="isSidebarCollapsed"
          :icon="link.icon"
          class="mx-2 my-0.5"
        />
      </div>
    </div>
    <SidebarLink
      :label="isSidebarCollapsed ? 'Expand' : 'Collapse'"
      :isCollapsed="isSidebarCollapsed"
      @click="isSidebarCollapsed = !isSidebarCollapsed"
      class="m-2"
    >
      <template #icon>
        <span class="grid h-5 w-6 flex-shrink-0 place-items-center">
          <ArrowLeftToLine
            class="h-4.5 w-4.5 text-gray-700 duration-300 ease-in-out"
            :class="{ '[transform:rotateY(180deg)]': isSidebarCollapsed }"
          />
        </span>
      </template>
    </SidebarLink>
  </div>
</template>

<script setup>
import { useStorage } from '@vueuse/core'
import SidebarLink from '@/components/SidebarLink.vue'
import {
  Banknote,
  ArrowLeftToLine,
  Wallet,
  ClipboardList,
  Home,
} from 'lucide-vue-next'
import UserDropdown from './UserDropdown.vue'
import { createResource } from 'frappe-ui'

const COMPONENT_NAME = 'sidebar'

const links = [
  { label: 'Home', to: '/', icon: Home },
  {
    label: 'Pay Fees',
    to: '/pay-fee',
    icon: Wallet,
  },
  {
    label: 'Transactions',
    to: '/transactions',
    icon: Banknote,
  },
  {
    label: 'Applications',
    to: '/applications',
    icon: ClipboardList,
  },
]

const isSidebarCollapsed = useStorage('sidebar_is_collapsed', false)

const educationSettings = createResource({
  url: 'onehash_education.api.get_school_abbr_logo',
  auto: true,
})
</script>
