<template>
  <div class="container mx-auto p-6 space-y-6">
    <!-- Terminal Header Skeleton -->
    <div class="h-8 bg-gray-700 rounded animate-pulse w-1/3"></div>

    <!-- Stats Grid Skeleton -->
    <div class="grid grid-cols-1 md:grid-cols-4 gap-4">
      <div v-for="i in 4" :key="i" class="h-24 bg-gray-700 rounded animate-pulse"></div>
    </div>

    <!-- Workers Skeleton -->
    <div class="space-y-4">
      <div class="h-6 bg-gray-700 rounded animate-pulse w-1/4"></div>
      <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div v-for="i in 2" :key="i" class="h-48 bg-gray-700 rounded animate-pulse"></div>
      </div>
    </div>

    <!-- Queue Skeleton -->
    <div class="space-y-4">
      <div class="h-6 bg-gray-700 rounded animate-pulse w-1/4"></div>
      <div class="space-y-2">
        <div v-for="i in 5" :key="i" class="h-16 bg-gray-700 rounded animate-pulse"></div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
// Simple loading skeleton - no props needed
</script>
