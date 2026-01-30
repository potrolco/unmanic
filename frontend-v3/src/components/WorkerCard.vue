<template>
  <div class="worker-card bg-gradient-to-b from-gray-800 to-gray-900 rounded-lg p-4 border border-gray-700" style="box-shadow: inset 2px 2px 4px rgba(255,255,255,0.1), inset -2px -2px 4px rgba(0,0,0,0.3)">
    <!-- Header: Worker name + status badge -->
    <div class="flex items-center justify-between mb-4">
      <h3 class="font-terminal text-crt-phosphor text-lg">{{ worker.name }}</h3>
      <span
        class="px-3 py-1 rounded text-xs font-bold uppercase"
        :class="statusBadgeClass"
      >
        {{ statusText }}
      </span>
    </div>

    <!-- LED Displays -->
    <div v-if="!worker.idle" class="grid grid-cols-2 gap-3 mb-4">
      <div>
        <div class="text-xs text-gray-400 mb-1">FPS</div>
        <LEDDisplay :value="fps" color="orange" size="lg" />
      </div>
      <div>
        <div class="text-xs text-gray-400 mb-1">CPU %</div>
        <LEDDisplay :value="cpuPercent" color="cyan" size="lg" />
      </div>
    </div>

    <!-- Progress bar (VU Meter style) -->
    <div v-if="!worker.idle && worker.current_file" class="mb-3">
      <VUMeter
        :value="progress"
        :label="truncatedFilename"
        :show-peak="true"
      />
    </div>

    <!-- Stats -->
    <div v-if="!worker.idle" class="text-sm text-crt-cyan font-terminal">
      <div v-if="elapsed">Elapsed: {{ elapsed }}s</div>
      <div v-if="memPercent">Memory: {{ memPercent }}%</div>
    </div>

    <!-- Idle state -->
    <div v-else class="text-center py-8 text-gray-500 font-terminal">
      [ IDLE - AWAITING TASKS ]
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import type { Worker } from '@/stores/workers'
import LEDDisplay from './LEDDisplay.vue'
import VUMeter from './VUMeter.vue'

const props = defineProps<{
  worker: Worker
}>()

const statusText = computed(() => {
  if (props.worker.paused) return 'Paused'
  if (props.worker.idle) return 'Idle'
  return 'Transcoding'
})

const statusBadgeClass = computed(() => {
  if (props.worker.paused) return 'bg-amber-600 text-white'
  if (props.worker.idle) return 'bg-gray-600 text-gray-300'
  return 'bg-green-600 text-white shadow-phosphor-glow'
})

const fps = computed(() => {
  // Extract FPS from worker log or subprocess data
  return 47 // Placeholder - should parse from worker.worker_log_tail
})

const progress = computed(() => {
  const percent = props.worker.subprocess?.percent
  return typeof percent === 'number' ? percent : parseFloat(String(percent) || '0')
})

const cpuPercent = computed(() => {
  const cpu = props.worker.subprocess?.cpu_percent
  return cpu ? parseFloat(String(cpu)) : 0
})

const memPercent = computed(() => {
  const mem = props.worker.subprocess?.mem_percent
  return mem ? parseFloat(String(mem)) : 0
})

const elapsed = computed(() => {
  return props.worker.subprocess?.elapsed
})

const truncatedFilename = computed(() => {
  if (!props.worker.current_file) return ''
  const filename = props.worker.current_file.split('/').pop() || ''
  return filename.length > 40 ? filename.substring(0, 37) + '...' : filename
})
</script>

<style scoped>
.worker-card {
  background: linear-gradient(135deg, #2a2e35 0%, #1a1e25 100%);
}
</style>
