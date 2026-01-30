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

      <!-- Workers List - Retro CRT Style -->
      <div class="space-y-4">
        <WorkerCard
          v-for="worker in workersStore.workers"
          :key="worker.id"
          :worker="worker"
        />

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
import WorkerCard from '@/components/WorkerCard.vue'

const workersStore = useWorkersStore()

onMounted(async () => {
  // Fetch initial data
  await workersStore.fetchWorkers()

  // Setup WebSocket for real-time updates
  workersStore.setupWebSocket()
  wsClient.connect()
})
</script>
