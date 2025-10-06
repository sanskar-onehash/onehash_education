<template>
  <div :id="PAGE_NAME">
    <iframe
      id="applications-iframe"
      ref="iframeEl"
      :src="iframeSrc"
      class="w-full min-h-full"
    ></iframe>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'

const PAGE_NAME = 'applications'

const iframeSrc = ref('')
const iframeEl = ref(null)

iframeSrc.value = window.location.origin + '/student-application'

onMounted(() => {
  window.addEventListener('message', (message) => {
    if (iframeEl.value && message.source === iframeEl.value.contentWindow) {
      if (
        message.data &&
        ['number', 'string'].includes(typeof message.data.height)
      ) {
        iframeEl.value.style.height = `${message.data.height}px`
      }
    }
  })
})
</script>
