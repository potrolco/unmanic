<template>
  <div class="container mx-auto px-4 py-8">
    <h1 class="text-3xl font-bold mb-8">Workers Management</h1>

    <div v-if="workersStore.loading" class="text-gray-500">Loading workers...</div>
    <div v-else-if="workersStore.error" class="text-red-500">{{ workersStore.error }}</div>
    <div v-else>
      <!-- Summary Stats -->
      <div class="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
        <div class="bg-blue-50 dark:bg-blue-900/20 p-4 rounded-lg">
          <div class="text-sm text-gray-600 dark:text-gray-400">Total Workers</div>
          <div class="text-2xl font-bold">{{ workersStore.workerCount }}</div>
        </div>
        <div class="bg-green-50 dark:bg-green-900/20 p-4 rounded-lg">
          <div class="text-sm text-gray-600 dark:text-gray-400">Active</div>
          <div class="text-2xl font-bold text-green-600">{{ workersStore.activeWorkers.length }}</div>
        </div>
        <div class="bg-gray-50 dark:bg-gray-700/20 p-4 rounded-lg">
          <div class="text-sm text-gray-600 dark:text-gray-400">Idle</div>
          <div class="text-2xl font-bold">{{ workersStore.idleWorkers.length }}</div>
        </div>
        <div class="bg-orange-50 dark:bg-orange-900/20 p-4 rounded-lg">
          <div class="text-sm text-gray-600 dark:text-gray-400">Paused</div>
          <div class="text-2xl font-bold text-orange-600">{{ workersStore.pausedWorkers.length }}</div>
        </div>
      </div>

      <!-- Workers List -->
      <div class="space-y-4">
        <div
          v-for="worker in workersStore.workers"
          :key="worker.id"
          class="card"
        >
          <div class="flex items-start justify-between">
            <div class="flex-1">
              <!-- Worker Name and Status -->
              <div class="flex items-center gap-3 mb-2">
                <h3 class="text-lg font-semibold">{{ worker.name }}</h3>
                <span
                  :class="getStatusBadgeClass(worker)"
                  class="px-2 py-1 text-xs font-medium rounded-full"
                >
                  {{ getStatusText(worker) }}
                </span>
              </div>

              <!-- Current Task -->
              <div v-if="worker.current_file" class="mb-2">
                <div class="text-sm text-gray-600 dark:text-gray-400">Current Task:</div>
                <div class="text-sm font-mono truncate">{{ worker.current_file }}</div>
              </div>
              <div v-else class="text-sm text-gray-500 italic mb-2">
                No active task
              </div>

              <!-- Worker Details -->
              <div class="flex gap-6 text-sm text-gray-600 dark:text-gray-400">
                <div v-if="worker.start_time">
                  <span class="font-medium">Started:</span> {{ formatDate(worker.start_time) }}
                </div>
                <div v-if="worker.current_task">
                  <span class="font-medium">Task ID:</span> #{{ worker.current_task }}
                </div>
              </div>
            </div>

            <!-- Actions -->
            <div class="flex gap-2 ml-4">
              <button
                v-if="!worker.paused && !worker.idle"
                @click="handlePauseWorker(worker.id)"
                class="btn btn-secondary text-sm px-3 py-1"
                :disabled="workersStore.loading"
              >
                Pause
              </button>
              <button
                v-if="worker.paused"
                @click="handleResumeWorker(worker.id)"
                class="btn btn-primary text-sm px-3 py-1"
                :disabled="workersStore.loading"
              >
                Resume
              </button>
            </div>
          </div>
        </div>

        <!-- Empty State -->
        <div v-if="workersStore.workerCount === 0" class="card text-center py-12">
          <p class="text-gray-500">No workers configured</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { onMounted } from 'vue'
import { useWorkersStore } from '@/stores/workers'
import { wsClient } from '@/api/websocket'
import type { Worker } from '@/stores/workers'

const workersStore = useWorkersStore()

// Worker control handlers
async function handlePauseWorker(workerId: string) {
  await workersStore.pauseWorker(workerId)
}

async function handleResumeWorker(workerId: string) {
  await workersStore.resumeWorker(workerId)
}

// Status helpers
function getStatusText(worker: Worker): string {
  if (worker.paused) return 'Paused'
  if (worker.idle) return 'Idle'
  return 'Active'
}

function getStatusBadgeClass(worker: Worker): string {
  if (worker.paused) return 'bg-orange-100 text-orange-800 dark:bg-orange-900/30 dark:text-orange-400'
  if (worker.idle) return 'bg-gray-100 text-gray-800 dark:bg-gray-700 dark:text-gray-300'
  return 'bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-400'
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
  await workersStore.fetchWorkers()

  // Setup WebSocket for real-time updates
  workersStore.setupWebSocket()
  wsClient.connect()
})
</script>
