import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { apiClient } from '@/api/client'
import { wsClient } from '@/api/websocket'

export interface QueueTask {
  id: number
  library_id: number
  abspath: string
  priority: number
  created_at: string
}

export const useQueueStore = defineStore('queue', () => {
  // State
  const tasks = ref<QueueTask[]>([])
  const totalTasks = ref(0)
  const loading = ref(false)
  const error = ref<string | null>(null)

  // Computed
  const pendingCount = computed(() => totalTasks.value)
  const isEmpty = computed(() => tasks.value.length === 0)

  // Actions
  async function fetchQueue(start = 0, length = 50) {
    loading.value = true
    error.value = null
    try {
      const response = await apiClient.getQueue(start, length)
      tasks.value = response.data.data || []
      totalTasks.value = response.data.recordsTotal || 0
    } catch (err) {
      error.value = 'Failed to fetch queue'
      console.error(err)
    } finally {
      loading.value = false
    }
  }

  async function deleteTask(taskId: number) {
    try {
      await apiClient.deleteQueueTask(taskId)
      tasks.value = tasks.value.filter(t => t.id !== taskId)
      totalTasks.value--
    } catch (err) {
      error.value = 'Failed to delete task'
      console.error(err)
    }
  }

  // WebSocket real-time updates
  function setupWebSocket() {
    wsClient.on('pending_tasks_info', (message: any) => {
      // Backend sends: {success: true, type: "pending_tasks_info", pending_tasks_info: {...}}
      if (message.pending_tasks_info) {
        const info = message.pending_tasks_info
        tasks.value = info.results || []
        totalTasks.value = info.recordsTotal || 0
      }
    })

    // Start streaming pending tasks info
    wsClient.startStream('pending_tasks_info')
  }

  return {
    // State
    tasks,
    totalTasks,
    loading,
    error,
    // Computed
    pendingCount,
    isEmpty,
    // Actions
    fetchQueue,
    deleteTask,
    setupWebSocket
  }
})
