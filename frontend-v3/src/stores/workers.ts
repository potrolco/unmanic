import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { apiClient } from '@/api/client'
import { wsClient } from '@/api/websocket'

export interface Worker {
  id: string
  name: string
  idle: boolean
  paused: boolean
  current_file?: string
  current_task?: number
  start_time?: string
}

export const useWorkersStore = defineStore('workers', () => {
  // State
  const workers = ref<Worker[]>([])
  const loading = ref(false)
  const error = ref<string | null>(null)

  // Computed
  const activeWorkers = computed(() => workers.value.filter(w => !w.idle && !w.paused))
  const idleWorkers = computed(() => workers.value.filter(w => w.idle))
  const pausedWorkers = computed(() => workers.value.filter(w => w.paused))
  const workerCount = computed(() => workers.value.length)

  // Actions
  async function fetchWorkers() {
    loading.value = true
    error.value = null
    try {
      const response = await apiClient.getWorkers()
      workers.value = response.data.workers || []
    } catch (err) {
      error.value = 'Failed to fetch workers'
      console.error(err)
    } finally {
      loading.value = false
    }
  }

  async function pauseWorker(workerId: string) {
    try {
      await apiClient.pauseWorker(workerId)
      await fetchWorkers()
    } catch (err) {
      error.value = 'Failed to pause worker'
      console.error(err)
    }
  }

  async function resumeWorker(workerId: string) {
    try {
      await apiClient.resumeWorker(workerId)
      await fetchWorkers()
    } catch (err) {
      error.value = 'Failed to resume worker'
      console.error(err)
    }
  }

  // WebSocket real-time updates
  function setupWebSocket() {
    wsClient.on('workers', (message: any) => {
      // Backend sends: {success: true, type: "workers", workers: [...]}
      if (message.workers) {
        workers.value = message.workers
      }
    })

    // Start streaming worker info
    wsClient.startStream('workers_info')
  }

  return {
    // State
    workers,
    loading,
    error,
    // Computed
    activeWorkers,
    idleWorkers,
    pausedWorkers,
    workerCount,
    // Actions
    fetchWorkers,
    pauseWorker,
    resumeWorker,
    setupWebSocket
  }
})
