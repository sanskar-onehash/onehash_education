<template>
  <div>
    <div class="flex h-screen w-screen">
      <div class="h-full border-r bg-gray-50">
        <Sidebar />
      </div>
      <div class="flex-1 flex flex-col h-full overflow-auto">
        <Navbar />
        <router-view class="flex-1 overflow-auto" />
      </div>
    </div>
  </div>
  <Toasts />
</template>

<script setup>
import Sidebar from '@/components/Sidebar.vue'
import Navbar from '@/components/Navbar.vue'
import { RouterView } from 'vue-router'
import { Toasts } from 'frappe-ui'
import { createResource } from 'frappe-ui'
import { useExternalScriptApi } from '@/stores/external_script_api'

const stylingResource = createResource({
  url: 'onehash_education.onehash_education.doctype.education_settings.education_settings.get_portal_css',
  auto: true,
  onSuccess: (css) => {
    const existing = document.getElementById('external-css-style')
    if (existing) {
      existing.remove()
    }

    const style = document.createElement('style')
    style.id = 'external-css-style'
    style.innerHTML = css
    document.head.appendChild(style)
  },
  onError: (err) => {
    console.error('Failed to fetch portal CSS:', err)
  },
})

const scriptResource = createResource({
  url: 'onehash_education.onehash_education.doctype.education_settings.education_settings.get_portal_js',
  auto: true,
  onSuccess: (jsCode) => {
    const externalScriptStore = useExternalScriptApi()

    const ctx = externalScriptStore

    try {
      const fn = new Function('ctx', jsCode)

      fn(ctx)
    } catch (err) {
      console.error('Failed to execute external JS:', err)
    }
  },
  onError: (err) => {
    console.error('Failed to fetch portal JS:', err)
  },
})
</script>
