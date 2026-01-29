<template>
  <nav class="bg-white dark:bg-gray-800 border-b border-gray-200 dark:border-gray-700">
    <div class="container mx-auto px-4">
      <div class="flex items-center justify-between h-16">
        <!-- Logo/Brand -->
        <div class="flex items-center">
          <h1 class="text-xl font-bold text-primary-600 dark:text-primary-400">TARS</h1>
        </div>

        <!-- Navigation Links -->
        <div class="hidden md:flex space-x-4">
          <router-link
            v-for="route in navRoutes"
            :key="route.path"
            :to="route.path"
            class="px-3 py-2 rounded-md text-sm font-medium transition-colors"
            :class="isActive(route.path)
              ? 'bg-primary-100 dark:bg-primary-900/30 text-primary-700 dark:text-primary-300'
              : 'text-gray-600 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700'"
          >
            {{ route.name }}
          </router-link>
        </div>

        <!-- Mobile Menu Button -->
        <div class="md:hidden">
          <button
            @click="mobileMenuOpen = !mobileMenuOpen"
            class="p-2 rounded-md text-gray-600 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700"
          >
            <svg class="h-6 w-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path
                v-if="!mobileMenuOpen"
                stroke-linecap="round"
                stroke-linejoin="round"
                stroke-width="2"
                d="M4 6h16M4 12h16M4 18h16"
              />
              <path
                v-else
                stroke-linecap="round"
                stroke-linejoin="round"
                stroke-width="2"
                d="M6 18L18 6M6 6l12 12"
              />
            </svg>
          </button>
        </div>
      </div>

      <!-- Mobile Menu -->
      <div v-if="mobileMenuOpen" class="md:hidden pb-4">
        <router-link
          v-for="route in navRoutes"
          :key="route.path"
          :to="route.path"
          @click="mobileMenuOpen = false"
          class="block px-3 py-2 rounded-md text-base font-medium"
          :class="isActive(route.path)
            ? 'bg-primary-100 dark:bg-primary-900/30 text-primary-700 dark:text-primary-300'
            : 'text-gray-600 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700'"
        >
          {{ route.name }}
        </router-link>
      </div>
    </div>
  </nav>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useRoute } from 'vue-router'

const route = useRoute()
const mobileMenuOpen = ref(false)

const navRoutes = [
  { path: '/', name: 'Dashboard' },
  { path: '/workers', name: 'Workers' },
  { path: '/queue', name: 'Queue' },
  { path: '/history', name: 'History' },
  { path: '/plugins', name: 'Plugins' },
  { path: '/settings', name: 'Settings' },
]

const isActive = (path: string) => {
  if (path === '/') {
    return route.path === '/'
  }
  return route.path.startsWith(path)
}
</script>
