<template>
  <div class="container mx-auto px-4 py-8">
    <h1 class="text-3xl font-bold mb-8">TARS Dashboard</h1>

    <!-- Workers Section -->
    <div class="card mb-6">
      <h2 class="text-xl font-semibold mb-4">Workers</h2>
      <div v-if="workersStore.loading" class="text-gray-500">Loading...</div>
      <div v-else-if="workersStore.error" class="text-red-500">{{ workersStore.error }}</div>
      <div v-else class="space-y-4">
        <div class="grid grid-cols-1 md:grid-cols-3 gap-4 mb-4">
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
        </div>

        <div v-if="workersStore.activeWorkers.length > 0">
          <h3 class="font-semibold mb-2">Active Workers</h3>
          <div class="space-y-2">
            <div
              v-for="worker in workersStore.activeWorkers"
              :key="worker.id"
              class="p-3 bg-gray-50 dark:bg-gray-700 rounded flex items-center justify-between"
            >
              <div class="flex-1">
                <div class="font-medium">{{ worker.name }}</div>
                <div v-if="worker.current_file" class="text-sm text-gray-600 dark:text-gray-400 truncate">
                  {{ worker.current_file }}
                </div>
              </div>
              <button
                @click="handlePauseWorker(worker.id)"
                class="btn btn-secondary ml-4 text-sm px-3 py-1"
                :disabled="workersStore.loading"
              >
                Pause
              </button>
            </div>
          </div>
        </div>

        <div v-if="workersStore.pausedWorkers.length > 0" class="mt-4">
          <h3 class="font-semibold mb-2">Paused Workers</h3>
          <div class="space-y-2">
            <div
              v-for="worker in workersStore.pausedWorkers"
              :key="worker.id"
              class="p-3 bg-orange-50 dark:bg-orange-900/20 rounded flex items-center justify-between"
            >
              <div class="font-medium">{{ worker.name }}</div>
              <button
                @click="handleResumeWorker(worker.id)"
                class="btn btn-primary ml-4 text-sm px-3 py-1"
                :disabled="workersStore.loading"
              >
                Resume
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- GPU Section -->
    <div v-if="gpuStatus && gpuStatus.enabled" class="card mb-6">
      <h2 class="text-xl font-semibold mb-4">GPU Acceleration</h2>
      <div v-if="gpuLoading" class="text-gray-500">Loading...</div>
      <div v-else-if="gpuError" class="text-red-500">{{ gpuError }}</div>
      <div v-else class="space-y-4">
        <div class="grid grid-cols-1 md:grid-cols-4 gap-4">
          <div class="bg-purple-50 dark:bg-purple-900/20 p-4 rounded-lg">
            <div class="text-sm text-gray-600 dark:text-gray-400">Total GPUs</div>
            <div class="text-2xl font-bold">{{ gpuStatus.total_devices }}</div>
          </div>
          <div class="bg-green-50 dark:bg-green-900/20 p-4 rounded-lg">
            <div class="text-sm text-gray-600 dark:text-gray-400">Available</div>
            <div class="text-2xl font-bold text-green-600">{{ gpuStatus.available_devices }}</div>
          </div>
          <div class="bg-blue-50 dark:bg-blue-900/20 p-4 rounded-lg">
            <div class="text-sm text-gray-600 dark:text-gray-400">Active Allocations</div>
            <div class="text-2xl font-bold">{{ gpuStatus.active_allocations }}</div>
          </div>
          <div class="bg-gray-50 dark:bg-gray-700/20 p-4 rounded-lg">
            <div class="text-sm text-gray-600 dark:text-gray-400">Strategy</div>
            <div class="text-sm font-medium">{{ gpuStatus.strategy }}</div>
          </div>
        </div>
      </div>
    </div>

    <!-- Queue Section -->
    <div class="card">
      <h2 class="text-xl font-semibold mb-4">Queue</h2>
      <div v-if="queueStore.loading" class="text-gray-500">Loading...</div>
      <div v-else-if="queueStore.error" class="text-red-500">{{ queueStore.error }}</div>
      <div v-else>
        <div class="bg-yellow-50 dark:bg-yellow-900/20 p-4 rounded-lg mb-4">
          <div class="text-sm text-gray-600 dark:text-gray-400">Pending Tasks</div>
          <div class="text-2xl font-bold">{{ queueStore.pendingCount }}</div>
        </div>

        <div v-if="!queueStore.isEmpty" class="space-y-2">
          <div
            v-for="task in queueStore.tasks.slice(0, 5)"
            :key="task.id"
            class="p-3 bg-gray-50 dark:bg-gray-700 rounded text-sm flex items-center justify-between"
          >
            <div class="flex-1 truncate">{{ task.abspath }}</div>
            <button
              @click="handleDeleteTask(task.id)"
              class="btn btn-danger ml-4 text-sm px-3 py-1"
              :disabled="queueStore.loading"
              title="Delete task"
            >
              Delete
            </button>
          </div>
          <router-link to="/queue" class="btn btn-secondary mt-4 inline-block">
            View All Tasks
          </router-link>
        </div>
        <div v-else class="text-gray-500">No tasks in queue</div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { useWorkersStore } from '@/stores/workers'
import { useQueueStore } from '@/stores/queue'
import { wsClient } from '@/api/websocket'
import { apiClient } from '@/api/client'

const workersStore = useWorkersStore()
const queueStore = useQueueStore()

// GPU status state
interface GPUStatus {
  enabled: boolean
  total_devices: number
  available_devices: number
  active_allocations: number
  max_workers_per_gpu: number
  strategy: string
}

const gpuStatus = ref<GPUStatus | null>(null)
const gpuLoading = ref(false)
const gpuError = ref<string | null>(null)

// Worker control handlers
async function handlePauseWorker(workerId: string) {
  await workersStore.pauseWorker(workerId)
}

async function handleResumeWorker(workerId: string) {
  await workersStore.resumeWorker(workerId)
}

// Queue control handlers
async function handleDeleteTask(taskId: number) {
  await queueStore.deleteTask(taskId)
}

// GPU status fetching
async function fetchGPUStatus() {
  gpuLoading.value = true
  gpuError.value = null
  try {
    const response = await apiClient.getGPUStatus()
    gpuStatus.value = response.data
  } catch (err) {
    gpuError.value = 'Failed to fetch GPU status'
    console.error(err)
  } finally {
    gpuLoading.value = false
  }
}

onMounted(async () => {
  // Fetch initial data
  await Promise.all([
    workersStore.fetchWorkers(),
    queueStore.fetchQueue(),
    fetchGPUStatus()
  ])

  // Setup WebSocket for real-time updates
  workersStore.setupWebSocket()
  queueStore.setupWebSocket()
  wsClient.connect()
})
</script>
