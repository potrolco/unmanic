import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { apiClient } from '@/api/client'

export interface HistoryTask {
  id: number
  library_id: number
  abspath: string
  task_label: string
  task_success: boolean
  processed_by_worker: string
  finish_time: string
  start_time: string
}

export const useHistoryStore = defineStore('history', () => {
  // State
  const tasks = ref<HistoryTask[]>([])
  const totalTasks = ref(0)
  const loading = ref(false)
  const error = ref<string | null>(null)

  // Computed
  const successTasks = computed(() => tasks.value.filter(t => t.task_success))
  const failedTasks = computed(() => tasks.value.filter(t => !t.task_success))
  const isEmpty = computed(() => tasks.value.length === 0)

  // Actions
  async function fetchHistory(start = 0, length = 50) {
    loading.value = true
    error.value = null
    try {
      const response = await apiClient.getHistory(start, length)
      const newTasks = response.data.data || []

      // Append new tasks (pagination)
      if (start === 0) {
        tasks.value = newTasks
      } else {
        tasks.value = [...tasks.value, ...newTasks]
      }

      totalTasks.value = response.data.recordsTotal || 0
    } catch (err) {
      error.value = 'Failed to fetch history'
      console.error(err)
    } finally {
      loading.value = false
    }
  }

  async function bulkDeleteCompleted() {
    loading.value = true
    error.value = null
    try {
      await apiClient.bulkDeleteCompleted()
      // Refresh the history after deletion
      await fetchHistory(0, 50)
    } catch (err) {
      error.value = 'Failed to delete completed tasks'
      console.error(err)
    } finally {
      loading.value = false
    }
  }

  return {
    // State
    tasks,
    totalTasks,
    loading,
    error,
    // Computed
    successTasks,
    failedTasks,
    isEmpty,
    // Actions
    fetchHistory,
    bulkDeleteCompleted
  }
})
