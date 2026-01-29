<template>
  <div class="container mx-auto px-4 py-8">
    <h1 class="text-3xl font-bold mb-8">Task Queue</h1>

    <div v-if="queueStore.loading" class="text-gray-500">Loading queue...</div>
    <div v-else-if="queueStore.error" class="text-red-500">{{ queueStore.error }}</div>
    <div v-else>
      <!-- Summary -->
      <div class="card mb-6">
        <div class="flex items-center justify-between">
          <div>
            <h2 class="text-xl font-semibold mb-2">Pending Tasks</h2>
            <p class="text-gray-600 dark:text-gray-400">{{ queueStore.pendingCount }} task(s) in queue</p>
          </div>
          <div v-if="queueStore.pendingCount > 0" class="flex gap-2">
            <button
              @click="handleLoadMore"
              class="btn btn-secondary text-sm"
              :disabled="queueStore.loading || !hasMore"
            >
              {{ hasMore ? 'Load More' : 'All Loaded' }}
            </button>
          </div>
        </div>
      </div>

      <!-- Task List -->
      <div v-if="!queueStore.isEmpty" class="space-y-3">
        <div
          v-for="task in queueStore.tasks"
          :key="task.id"
          class="card hover:shadow-lg transition-shadow"
        >
          <div class="flex items-start justify-between">
            <div class="flex-1 min-w-0">
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
                <div>
                  <span class="font-medium">Priority:</span> {{ task.priority }}
                </div>
                <div v-if="task.library_id">
                  <span class="font-medium">Library ID:</span> {{ task.library_id }}
                </div>
                <div v-if="task.created_at">
                  <span class="font-medium">Created:</span> {{ formatDate(task.created_at) }}
                </div>
              </div>
            </div>

            <!-- Actions -->
            <div class="ml-4">
              <button
                @click="handleDeleteTask(task.id)"
                class="btn btn-danger text-sm px-3 py-1"
                :disabled="queueStore.loading"
                title="Delete task"
              >
                Delete
              </button>
            </div>
          </div>
        </div>
      </div>

      <!-- Empty State -->
      <div v-else class="card text-center py-12">
        <div class="text-gray-400 mb-4">
          <svg class="w-16 h-16 mx-auto" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"></path>
          </svg>
        </div>
        <h3 class="text-xl font-semibold mb-2">No Tasks in Queue</h3>
        <p class="text-gray-500">Add media files to your libraries to start processing</p>
      </div>

      <!-- Load More Footer -->
      <div v-if="hasMore && queueStore.tasks.length > 0" class="mt-6 text-center">
        <button
          @click="handleLoadMore"
          class="btn btn-secondary"
          :disabled="queueStore.loading"
        >
          Load More Tasks
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { onMounted, computed, ref } from 'vue'
import { useQueueStore } from '@/stores/queue'
import { wsClient } from '@/api/websocket'

const queueStore = useQueueStore()
const pageSize = 50
const currentPage = ref(0)

const hasMore = computed(() => {
  return queueStore.tasks.length < queueStore.totalTasks
})

// Task control handlers
async function handleDeleteTask(taskId: number) {
  await queueStore.deleteTask(taskId)
}

async function handleLoadMore() {
  currentPage.value++
  const start = currentPage.value * pageSize
  await queueStore.fetchQueue(start, pageSize)
}

function formatDate(dateString: string): string {
  try {
    const date = new Date(dateString)
    return date.toLocaleString()
  } catch {
    return dateString
  }
}

onMounted(async () => {
  // Fetch initial data
  await queueStore.fetchQueue(0, pageSize)

  // Setup WebSocket for real-time updates
  queueStore.setupWebSocket()
  wsClient.connect()
})
</script>
