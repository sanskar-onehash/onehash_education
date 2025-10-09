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
import { ref } from 'vue'

const PAGE_NAME = 'applications'

const iframeSrc = ref('')
const iframeEl = ref(null)

iframeSrc.value = window.location.origin + '/student-application'
</script>
