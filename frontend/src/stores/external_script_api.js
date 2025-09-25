import utils from '@/utils'
import { defineStore } from 'pinia'

export const useExternalScriptApi = defineStore('externalScriptApi', {
  state: () => ({
    data: {},
    api: {},
    currentPage: null,
    events: {},
    utils,
  }),
  actions: {
    add_data(key, data) {
      this.data[key] = data
    },

    remove_data(key) {
      delete this.data[key]
    },

    add_fn(key, fn) {
      this.api[key] = fn
    },

    remove_fn(key) {
      delete this.api[key]
    },

    clear_data() {
      this.data = {}
    },

    clear_api() {
      this.api = {}
    },

    clear() {
      this.clear_data()
      this.clear_api()
    },

    on(event, handler) {
      if (!this.events[event]) {
        this.events[event] = []
      }
      this.events[event].push(handler)
    },

    off(event, handler) {
      if (!this.events[event]) return
      this.events[event] = this.events[event].filter((h) => h !== handler)
    },

    async emit(event, payload) {
      if (!this.events[event]) return

      const handlers = this.events[event]
      await Promise.allSettled(
        handlers.map(async (handler) => {
          try {
            await handler(payload)
          } catch (err) {
            console.error(`Error in async event handler for "${event}":`, err)
          }
        }),
      )
    },
  },
})
