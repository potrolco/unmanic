<template>
  <div class="crt-pane bg-crt-black border-2 border-crt-phosphor-dim rounded-sm p-4">
    <!-- Terminal-style header -->
    <div v-if="title" class="crt-pane-header border-b border-crt-phosphor-dim pb-2 mb-4">
      <h3 class="font-terminal text-crt-phosphor text-lg uppercase tracking-wider">
        {{ title }}
      </h3>
    </div>

    <!-- Content -->
    <div class="crt-pane-content">
      <slot />
    </div>
  </div>
</template>

<script setup lang="ts">
defineProps<{
  title?: string
}>()
</script>

<style scoped>
.crt-pane {
  box-shadow: 0 0 20px rgba(51, 255, 51, 0.1);
}

.crt-pane-header {
  text-shadow: 0 0 8px rgba(51, 255, 51, 0.8);
}
</style>
