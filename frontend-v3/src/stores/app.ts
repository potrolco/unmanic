import { defineStore } from 'pinia'
import { ref } from 'vue'
import { useWorkersStore } from './workers'
import { useQueueStore } from './queue'
import { useHistoryStore } from './history'
import { wsClient } from '@/api/websocket'

export type BootStatus = 'idle' | 'loading' | 'ready' | 'error'

export const useAppStore = defineStore('app', () => {
  // State
  const boot = ref<BootStatus>('idle')
  const error = ref<string>('')

  // Actions
  async function init() {
    // Prevent duplicate initialization
    if (boot.value === 'loading' || boot.value === 'ready') {
      return
    }

    boot.value = 'loading'
    error.value = ''

    try {
      // Fetch initial snapshots in parallel
      await Promise.all([
        useWorkersStore().fetchWorkers(),
        useQueueStore().fetchQueue(),
        useHistoryStore().fetchHistory(),
      ])

      // Connect WebSocket for real-time updates
      wsClient.connect()

      boot.value = 'ready'
    } catch (e: any) {
      boot.value = 'error'
      error.value = e?.message ?? String(e)
      console.error('Bootstrap failed:', e)
    }
  }

  function reset() {
    boot.value = 'idle'
    error.value = ''
  }

  return {
    boot,
    error,
    init,
    reset,
  }
})
