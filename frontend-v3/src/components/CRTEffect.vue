<template>
  <div v-if="enabled" class="crt-effect-overlay">
    <!-- Scanlines -->
    <div class="scanlines"></div>

    <!-- Subtle flicker -->
    <div class="flicker"></div>
  </div>
</template>

<script setup lang="ts">
withDefaults(defineProps<{
  enabled?: boolean
}>(), {
  enabled: false, // Optional - user can enable
})
</script>

<style scoped>
.crt-effect-overlay {
  pointer-events: none;
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  z-index: 9999;
}

.scanlines {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: repeating-linear-gradient(
    0deg,
    rgba(0, 0, 0, 0.1),
    rgba(0, 0, 0, 0.1) 1px,
    transparent 1px,
    transparent 2px
  );
  animation: scanline-move 8s linear infinite;
}

.flicker {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(51, 255, 51, 0.02);
  animation: flicker-animation 0.15s infinite;
}

@keyframes scanline-move {
  0% { transform: translateY(0); }
  100% { transform: translateY(10px); }
}

@keyframes flicker-animation {
  0% { opacity: 0.95; }
  50% { opacity: 1; }
  100% { opacity: 0.93; }
}
</style>
