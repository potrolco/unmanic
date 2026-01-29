<template>
  <div class="container mx-auto px-4 py-8">
    <h1 class="text-3xl font-bold mb-8">Settings</h1>

    <div v-if="loading" class="text-gray-500">Loading settings...</div>
    <div v-else-if="error" class="text-red-500">{{ error }}</div>
    <div v-else>
      <!-- Tab Navigation -->
      <div class="mb-6 border-b border-gray-200 dark:border-gray-700">
        <nav class="flex space-x-8" aria-label="Tabs">
          <button
            v-for="tab in tabs"
            :key="tab.id"
            @click="activeTab = tab.id"
            :class="[
              activeTab === tab.id
                ? 'border-primary-600 text-primary-600 dark:border-primary-500 dark:text-primary-500'
                : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300 dark:text-gray-400 dark:hover:text-gray-300',
              'whitespace-nowrap py-4 px-1 border-b-2 font-medium text-sm'
            ]"
          >
            {{ tab.label }}
          </button>
        </nav>
      </div>

      <!-- General Settings Tab -->
      <div v-show="activeTab === 'general'" class="space-y-6">
        <div class="card">
          <h2 class="text-xl font-semibold mb-4">General Configuration</h2>

          <div class="space-y-4">
            <div>
              <label class="block text-sm font-medium mb-2">Number of Workers</label>
              <input
                v-model.number="settings.number_of_workers"
                type="number"
                min="1"
                max="32"
                class="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md bg-white dark:bg-gray-700"
              />
              <p class="mt-1 text-sm text-gray-500">Maximum concurrent transcoding jobs</p>
            </div>

            <div>
              <label class="block text-sm font-medium mb-2">Cache Directory</label>
              <input
                v-model="settings.cache_path"
                type="text"
                class="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md bg-white dark:bg-gray-700"
              />
              <p class="mt-1 text-sm text-gray-500">Temporary file storage location</p>
            </div>

            <div class="flex items-center">
              <input
                v-model="settings.debugging"
                type="checkbox"
                class="h-4 w-4 text-primary-600 rounded"
              />
              <label class="ml-2 block text-sm">Enable debug logging</label>
            </div>
          </div>
        </div>
      </div>

      <!-- GPU Settings Tab -->
      <div v-show="activeTab === 'gpu'" class="space-y-6">
        <div class="card">
          <h2 class="text-xl font-semibold mb-4">GPU Acceleration</h2>

          <div class="space-y-4">
            <div class="flex items-center">
              <input
                v-model="settings.gpu_enabled"
                type="checkbox"
                class="h-4 w-4 text-primary-600 rounded"
              />
              <label class="ml-2 block text-sm font-medium">Enable GPU acceleration</label>
            </div>

            <div v-if="settings.gpu_enabled">
              <label class="block text-sm font-medium mb-2">Max Workers per GPU</label>
              <input
                v-model.number="settings.max_workers_per_gpu"
                type="number"
                min="1"
                max="8"
                class="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md bg-white dark:bg-gray-700"
              />
              <p class="mt-1 text-sm text-gray-500">Number of concurrent jobs per GPU device</p>
            </div>

            <div v-if="settings.gpu_enabled">
              <label class="block text-sm font-medium mb-2">Assignment Strategy</label>
              <select
                v-model="settings.gpu_assignment_strategy"
                class="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md bg-white dark:bg-gray-700"
              >
                <option value="round_robin">Round Robin</option>
                <option value="least_used">Least Used</option>
                <option value="manual">Manual</option>
              </select>
              <p class="mt-1 text-sm text-gray-500">How to distribute work across GPUs</p>
            </div>
          </div>
        </div>
      </div>

      <!-- Worker Groups Tab -->
      <div v-show="activeTab === 'workers'" class="space-y-6">
        <div class="card">
          <h2 class="text-xl font-semibold mb-4">Worker Configuration</h2>

          <div class="space-y-4">
            <div>
              <label class="block text-sm font-medium mb-2">Worker Event Schedules</label>
              <textarea
                v-model="settings.worker_event_schedules"
                rows="4"
                class="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md bg-white dark:bg-gray-700 font-mono text-sm"
                placeholder="{}"
              ></textarea>
              <p class="mt-1 text-sm text-gray-500">JSON configuration for worker schedules</p>
            </div>

            <div class="flex items-center">
              <input
                v-model="settings.enable_audio_stream_transcoding"
                type="checkbox"
                class="h-4 w-4 text-primary-600 rounded"
              />
              <label class="ml-2 block text-sm">Enable audio stream transcoding</label>
            </div>

            <div class="flex items-center">
              <input
                v-model="settings.enable_video_encoding"
                type="checkbox"
                class="h-4 w-4 text-primary-600 rounded"
              />
              <label class="ml-2 block text-sm">Enable video encoding</label>
            </div>
          </div>
        </div>
      </div>

      <!-- Libraries Tab -->
      <div v-show="activeTab === 'libraries'" class="space-y-6">
        <div class="card">
          <h2 class="text-xl font-semibold mb-4">Library Paths</h2>

          <div class="space-y-4">
            <div>
              <label class="block text-sm font-medium mb-2">Library Scan Interval</label>
              <input
                v-model.number="settings.library_scan_interval"
                type="number"
                min="60"
                class="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md bg-white dark:bg-gray-700"
              />
              <p class="mt-1 text-sm text-gray-500">Seconds between library scans</p>
            </div>

            <div class="flex items-center">
              <input
                v-model="settings.follow_symlinks"
                type="checkbox"
                class="h-4 w-4 text-primary-600 rounded"
              />
              <label class="ml-2 block text-sm">Follow symbolic links when scanning</label>
            </div>

            <div class="bg-blue-50 dark:bg-blue-900/20 p-4 rounded-lg">
              <p class="text-sm text-gray-700 dark:text-gray-300">
                📁 Configure individual libraries in the Libraries section
              </p>
            </div>
          </div>
        </div>
      </div>

      <!-- Save Button -->
      <div class="mt-8 flex justify-end gap-4">
        <button
          @click="handleReset"
          class="btn btn-secondary"
          :disabled="saving"
        >
          Reset
        </button>
        <button
          @click="handleSave"
          class="btn btn-primary"
          :disabled="saving"
        >
          {{ saving ? 'Saving...' : 'Save Changes' }}
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, reactive } from 'vue'
import { apiClient } from '@/api/client'

interface Tab {
  id: string
  label: string
}

const tabs: Tab[] = [
  { id: 'general', label: 'General' },
  { id: 'gpu', label: 'GPU' },
  { id: 'workers', label: 'Workers' },
  { id: 'libraries', label: 'Libraries' }
]

const activeTab = ref('general')
const loading = ref(false)
const saving = ref(false)
const error = ref<string | null>(null)

const settings = reactive({
  number_of_workers: 2,
  cache_path: '/tmp/unmanic',
  debugging: false,
  gpu_enabled: false,
  max_workers_per_gpu: 2,
  gpu_assignment_strategy: 'round_robin',
  worker_event_schedules: '{}',
  enable_audio_stream_transcoding: true,
  enable_video_encoding: true,
  library_scan_interval: 300,
  follow_symlinks: false
})

const originalSettings = reactive({ ...settings })

async function fetchSettings() {
  loading.value = true
  error.value = null
  try {
    const response = await apiClient.getSettings()
    Object.assign(settings, response.data)
    Object.assign(originalSettings, response.data)
  } catch (err) {
    error.value = 'Failed to load settings'
    console.error(err)
  } finally {
    loading.value = false
  }
}

async function handleSave() {
  saving.value = true
  error.value = null
  try {
    await apiClient.updateSettings(settings)
    Object.assign(originalSettings, settings)
    // Show success message (could add a toast notification here)
    alert('Settings saved successfully')
  } catch (err) {
    error.value = 'Failed to save settings'
    console.error(err)
  } finally {
    saving.value = false
  }
}

function handleReset() {
  Object.assign(settings, originalSettings)
}

onMounted(async () => {
  await fetchSettings()
})
</script>
