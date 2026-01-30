<template>
  <div class="status-line bg-crt-dark-gray border-t-2 border-crt-phosphor-dim p-2 font-terminal text-sm">
    <div class="container mx-auto flex items-center justify-between">
      <!-- Left side: System status -->
      <div class="flex items-center space-x-6 text-crt-phosphor">
        <span class="flex items-center">
          <span class="status-dot mr-2" :class="wsConnected ? 'connected' : 'disconnected'"></span>
          WS: {{ wsConnected ? 'CONNECTED' : 'DISCONNECTED' }}
        </span>
        <span>WORKERS: {{ workerCount }}</span>
        <span>QUEUE: {{ queueSize }}</span>
      </div>

      <!-- Right side: Stats -->
      <div class="text-crt-cyan">
        <span v-if="fps">FPS: {{ fps }}</span>
        <span v-else>SYSTEM ONLINE</span>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
defineProps<{
  wsConnected: boolean
  workerCount: number
  queueSize: number
  fps?: number
}>()
</script>

<style scoped>
.status-line {
  font-size: 14px;
  text-shadow: 0 0 5px rgba(51, 255, 51, 0.5);
}

.status-dot {
  display: inline-block;
  width: 8px;
  height: 8px;
  border-radius: 50%;
}

.status-dot.connected {
  background-color: #33ff33;
  box-shadow: 0 0 8px #33ff33;
  animation: pulse 2s infinite;
}

.status-dot.disconnected {
  background-color: #ff3333;
  box-shadow: 0 0 8px #ff3333;
}

@keyframes pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.6; }
}
</style>
