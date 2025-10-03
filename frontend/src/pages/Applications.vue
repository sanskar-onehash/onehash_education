<template>
  <iframe ref="iframeEl" :src="iframeSrc"></iframe>
</template>

<script setup>
import { ref, onMounted } from 'vue'

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
