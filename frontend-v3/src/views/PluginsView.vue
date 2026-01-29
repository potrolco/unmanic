<template>
  <div class="container mx-auto px-4 py-8">
    <h1 class="text-3xl font-bold mb-8">Plugin Management</h1>

    <div v-if="loading" class="text-gray-500">Loading plugins...</div>
    <div v-else-if="error" class="text-red-500">{{ error }}</div>
    <div v-else>
      <!-- Summary Stats -->
      <div class="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
        <div class="bg-blue-50 dark:bg-blue-900/20 p-4 rounded-lg">
          <div class="text-sm text-gray-600 dark:text-gray-400">Total Plugins</div>
          <div class="text-2xl font-bold">{{ plugins.length }}</div>
        </div>
        <div class="bg-green-50 dark:bg-green-900/20 p-4 rounded-lg">
          <div class="text-sm text-gray-600 dark:text-gray-400">Enabled</div>
          <div class="text-2xl font-bold text-green-600">{{ enabledPlugins.length }}</div>
        </div>
        <div class="bg-gray-50 dark:bg-gray-700/20 p-4 rounded-lg">
          <div class="text-sm text-gray-600 dark:text-gray-400">Disabled</div>
          <div class="text-2xl font-bold">{{ disabledPlugins.length }}</div>
        </div>
      </div>

      <!-- Plugins List -->
      <div v-if="plugins.length > 0" class="space-y-4">
        <div
          v-for="plugin in plugins"
          :key="plugin.id"
          class="card hover:shadow-lg transition-shadow"
        >
          <div class="flex items-start justify-between">
            <div class="flex-1">
              <!-- Plugin Header -->
              <div class="flex items-center gap-3 mb-2">
                <h3 class="text-lg font-semibold">{{ plugin.name }}</h3>
                <span
                  :class="plugin.enabled
                    ? 'bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-400'
                    : 'bg-gray-100 text-gray-800 dark:bg-gray-700 dark:text-gray-300'
                  "
                  class="px-2 py-1 text-xs font-medium rounded-full"
                >
                  {{ plugin.enabled ? 'Enabled' : 'Disabled' }}
                </span>
                <span v-if="plugin.version" class="text-sm text-gray-500">
                  v{{ plugin.version }}
                </span>
              </div>

              <!-- Plugin Description -->
              <p v-if="plugin.description" class="text-sm text-gray-600 dark:text-gray-400 mb-3">
                {{ plugin.description }}
              </p>

              <!-- Plugin Details -->
              <div class="flex flex-wrap gap-4 text-sm text-gray-600 dark:text-gray-400">
                <div v-if="plugin.author">
                  <span class="font-medium">Author:</span> {{ plugin.author }}
                </div>
                <div v-if="plugin.plugin_type">
                  <span class="font-medium">Type:</span> {{ plugin.plugin_type }}
                </div>
                <div v-if="plugin.priority !== undefined">
                  <span class="font-medium">Priority:</span> {{ plugin.priority }}
                </div>
              </div>

              <!-- Plugin Tags -->
              <div v-if="plugin.tags && plugin.tags.length > 0" class="mt-3 flex flex-wrap gap-2">
                <span
                  v-for="tag in plugin.tags"
                  :key="tag"
                  class="px-2 py-1 text-xs bg-gray-100 dark:bg-gray-700 rounded"
                >
                  {{ tag }}
                </span>
              </div>
            </div>

            <!-- Actions -->
            <div class="ml-4 flex flex-col gap-2">
              <button
                v-if="!plugin.enabled"
                @click="handleEnablePlugin(plugin.id)"
                class="btn btn-primary text-sm px-3 py-1"
                :disabled="actionLoading"
              >
                Enable
              </button>
              <button
                v-if="plugin.enabled"
                @click="handleDisablePlugin(plugin.id)"
                class="btn btn-secondary text-sm px-3 py-1"
                :disabled="actionLoading"
              >
                Disable
              </button>
              <button
                v-if="plugin.has_settings"
                @click="handleConfigurePlugin(plugin.id)"
                class="btn btn-secondary text-sm px-3 py-1"
                :disabled="actionLoading"
              >
                Configure
              </button>
            </div>
          </div>
        </div>
      </div>

      <!-- Empty State -->
      <div v-else class="card text-center py-12">
        <div class="text-gray-400 mb-4">
          <svg class="w-16 h-16 mx-auto" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10"></path>
          </svg>
        </div>
        <h3 class="text-xl font-semibold mb-2">No Plugins Installed</h3>
        <p class="text-gray-500">Install plugins to extend TARS functionality</p>
      </div>

      <!-- Install Plugin Section -->
      <div class="card mt-6">
        <h2 class="text-xl font-semibold mb-4">Install New Plugin</h2>
        <div class="flex gap-2">
          <input
            v-model="newPluginId"
            type="text"
            placeholder="Plugin repository URL or ID"
            class="flex-1 px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md bg-white dark:bg-gray-700"
          />
          <button
            @click="handleInstallPlugin"
            class="btn btn-primary"
            :disabled="!newPluginId || installing"
          >
            {{ installing ? 'Installing...' : 'Install' }}
          </button>
        </div>
        <p class="mt-2 text-sm text-gray-500">
          Enter a plugin repository URL or plugin ID to install
        </p>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { apiClient } from '@/api/client'

interface Plugin {
  id: string
  name: string
  description?: string
  author?: string
  version?: string
  enabled: boolean
  plugin_type?: string
  priority?: number
  tags?: string[]
  has_settings?: boolean
}

const plugins = ref<Plugin[]>([])
const loading = ref(false)
const actionLoading = ref(false)
const installing = ref(false)
const error = ref<string | null>(null)
const newPluginId = ref('')

const enabledPlugins = computed(() => plugins.value.filter(p => p.enabled))
const disabledPlugins = computed(() => plugins.value.filter(p => !p.enabled))

async function fetchPlugins() {
  loading.value = true
  error.value = null
  try {
    const response = await apiClient.getPlugins()
    plugins.value = response.data.plugins || []
  } catch (err) {
    error.value = 'Failed to load plugins'
    console.error(err)
  } finally {
    loading.value = false
  }
}

async function handleEnablePlugin(pluginId: string) {
  actionLoading.value = true
  try {
    // API call to enable plugin
    await apiClient.updateSettings({ [`plugin_${pluginId}_enabled`]: true })
    await fetchPlugins()
  } catch (err) {
    console.error('Failed to enable plugin:', err)
  } finally {
    actionLoading.value = false
  }
}

async function handleDisablePlugin(pluginId: string) {
  actionLoading.value = true
  try {
    // API call to disable plugin
    await apiClient.updateSettings({ [`plugin_${pluginId}_enabled`]: false })
    await fetchPlugins()
  } catch (err) {
    console.error('Failed to disable plugin:', err)
  } finally {
    actionLoading.value = false
  }
}

function handleConfigurePlugin(pluginId: string) {
  // Navigate to plugin configuration page or open modal
  alert(`Configuration for plugin: ${pluginId}`)
}

async function handleInstallPlugin() {
  if (!newPluginId.value) return

  installing.value = true
  error.value = null
  try {
    await apiClient.installPlugin(newPluginId.value)
    newPluginId.value = ''
    await fetchPlugins()
    alert('Plugin installed successfully')
  } catch (err) {
    error.value = 'Failed to install plugin'
    console.error(err)
  } finally {
    installing.value = false
  }
}

onMounted(async () => {
  await fetchPlugins()
})
</script>
