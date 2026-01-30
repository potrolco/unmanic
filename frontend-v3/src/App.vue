<template>
  <div id="app" :class="{ dark: isDark }">
    <div class="min-h-screen bg-gray-50 dark:bg-gray-900 text-gray-900 dark:text-gray-100">
      <AppNav />

      <!-- Loading State -->
      <DashboardSkeleton v-if="app.boot === 'loading'" />

      <!-- Error State -->
      <div v-else-if="app.boot === 'error'" class="flex items-center justify-center min-h-[60vh]">
        <div class="text-center p-8 bg-red-50 dark:bg-red-900/20 rounded-lg border border-red-200 dark:border-red-800">
          <h2 class="text-xl font-bold text-red-600 dark:text-red-400 mb-4">
            Bootstrap Failed
          </h2>
          <p class="text-red-700 dark:text-red-300 mb-4">{{ app.error }}</p>
          <button
            @click="app.init()"
            class="px-4 py-2 bg-red-600 hover:bg-red-700 text-white rounded"
          >
            Retry
          </button>
        </div>
      </div>

      <!-- Main Content -->
      <router-view v-else />
    </div>
  </div>
</template>

<script setup lang="ts">
import { onMounted } from 'vue'
import { useDark } from '@vueuse/core'
import AppNav from '@/components/AppNav.vue'
import DashboardSkeleton from '@/components/DashboardSkeleton.vue'
import { useAppStore } from '@/stores/app'

// Dark mode toggle (system preference + manual override)
const isDark = useDark({
  selector: 'html',
  attribute: 'class',
  valueDark: 'dark',
  valueLight: 'light',
})

// App store for bootstrap
const app = useAppStore()

// Bootstrap on mount
onMounted(() => {
  app.init()
})
</script>

<style>
@import './assets/main.css';
</style>
