<template>
  <div class="container mx-auto px-4 py-8">
    <h1 class="text-3xl font-bold mb-8">Task History</h1>

    <div v-if="historyStore.loading" class="text-gray-500">Loading history...</div>
    <div v-else-if="historyStore.error" class="text-red-500">{{ historyStore.error }}</div>
    <div v-else>
      <!-- Summary -->
      <div class="card mb-6">
        <div class="flex items-center justify-between">
          <div>
            <h2 class="text-xl font-semibold mb-2">Completed Tasks</h2>
            <div class="flex gap-6 text-sm text-gray-600 dark:text-gray-400">
              <div>
                <span class="font-medium">Total:</span> {{ historyStore.totalTasks }}
              </div>
              <div>
                <span class="font-medium text-green-600">Success:</span> {{ historyStore.successTasks.length }}
              </div>
              <div>
                <span class="font-medium text-red-600">Failed:</span> {{ historyStore.failedTasks.length }}
              </div>
            </div>
          </div>
          <div class="flex gap-2">
            <button
              v-if="historyStore.totalTasks > 0"
              @click="handleBulkDelete"
              class="btn btn-danger text-sm"
              :disabled="historyStore.loading"
              title="Delete all completed tasks"
            >
              Clear History
            </button>
            <button
              @click="handleLoadMore"
              class="btn btn-secondary text-sm"
              :disabled="historyStore.loading || !hasMore"
            >
              {{ hasMore ? 'Load More' : 'All Loaded' }}
            </button>
          </div>
        </div>
      </div>

      <!-- Task List -->
      <div v-if="!historyStore.isEmpty" class="space-y-3">
        <div
          v-for="task in historyStore.tasks"
          :key="task.id"
          class="card hover:shadow-lg transition-shadow"
        >
          <div class="flex items-start justify-between">
            <div class="flex-1 min-w-0">
              <!-- Task Status Badge -->
              <div class="flex items-center gap-3 mb-2">
                <span
                  :class="task.task_success
                    ? 'bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-400'
                    : 'bg-red-100 text-red-800 dark:bg-red-900/30 dark:text-red-400'
                  "
                  class="px-2 py-1 text-xs font-medium rounded-full"
                >
                  {{ task.task_success ? 'Success' : 'Failed' }}
                </span>
                <span v-if="task.task_label" class="text-sm text-gray-600 dark:text-gray-400">
                  {{ task.task_label }}
                </span>
              </div>

              <!-- Task Path -->
              <div class="mb-2">
                <div class="text-sm text-gray-600 dark:text-gray-400 mb-1">File Path:</div>
                <div class="font-mono text-sm break-all">{{ task.abspath }}</div>
              </div>

              <!-- Task Details -->
              <div class="flex flex-wrap gap-4 text-sm text-gray-600 dark:text-gray-400">
                <div>
                  <span class="font-medium">Task ID:</span> #{{ task.id }}
                </div>
                <div v-if="task.processed_by_worker">
                  <span class="font-medium">Worker:</span> {{ task.processed_by_worker }}
                </div>
                <div v-if="task.library_id">
                  <span class="font-medium">Library:</span> {{ task.library_id }}
                </div>
                <div v-if="task.start_time">
                  <span class="font-medium">Started:</span> {{ formatDate(task.start_time) }}
                </div>
                <div v-if="task.finish_time">
                  <span class="font-medium">Finished:</span> {{ formatDate(task.finish_time) }}
                </div>
                <div v-if="task.start_time && task.finish_time">
                  <span class="font-medium">Duration:</span> {{ calculateDuration(task.start_time, task.finish_time) }}
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Empty State -->
      <div v-else class="card text-center py-12">
        <div class="text-gray-400 mb-4">
          <svg class="w-16 h-16 mx-auto" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"></path>
          </svg>
        </div>
        <h3 class="text-xl font-semibold mb-2">No History</h3>
        <p class="text-gray-500">Completed tasks will appear here</p>
      </div>

      <!-- Load More Footer -->
      <div v-if="hasMore && historyStore.tasks.length > 0" class="mt-6 text-center">
        <button
          @click="handleLoadMore"
          class="btn btn-secondary"
          :disabled="historyStore.loading"
        >
          Load More Tasks
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { onMounted, computed, ref } from 'vue'
import { useHistoryStore } from '@/stores/history'

const historyStore = useHistoryStore()
const pageSize = 50
const currentPage = ref(0)

const hasMore = computed(() => {
  return historyStore.tasks.length < historyStore.totalTasks
})

// Task control handlers
async function handleBulkDelete() {
  if (confirm('Are you sure you want to clear all history? This cannot be undone.')) {
    await historyStore.bulkDeleteCompleted()
    currentPage.value = 0
  }
}

async function handleLoadMore() {
  currentPage.value++
  const start = currentPage.value * pageSize
  await historyStore.fetchHistory(start, pageSize)
}

function formatDate(dateString: string): string {
  try {
    const date = new Date(dateString)
    return date.toLocaleString()
  } catch {
    return dateString
  }
}

function calculateDuration(startTime: string, finishTime: string): string {
  try {
    const start = new Date(startTime)
    const finish = new Date(finishTime)
    const durationMs = finish.getTime() - start.getTime()

    const hours = Math.floor(durationMs / (1000 * 60 * 60))
    const minutes = Math.floor((durationMs % (1000 * 60 * 60)) / (1000 * 60))
    const seconds = Math.floor((durationMs % (1000 * 60)) / 1000)

    if (hours > 0) {
      return `${hours}h ${minutes}m ${seconds}s`
    } else if (minutes > 0) {
      return `${minutes}m ${seconds}s`
    } else {
      return `${seconds}s`
    }
  } catch {
    return 'Unknown'
  }
}

onMounted(async () => {
  // Fetch initial data
  await historyStore.fetchHistory(0, pageSize)
})
</script>
