<template>
  <div id="app" :class="{ dark: isDark }">
    <div class="min-h-screen bg-gray-50 dark:bg-gray-900 text-gray-900 dark:text-gray-100">
      <router-view />
    </div>
  </div>
</template>

<script setup lang="ts">
import { useDark } from '@vueuse/core'

// Dark mode toggle (system preference + manual override)
const isDark = useDark({
  selector: 'html',
  attribute: 'class',
  valueDark: 'dark',
  valueLight: 'light',
})
</script>

<style>
@import './assets/main.css';
</style>
