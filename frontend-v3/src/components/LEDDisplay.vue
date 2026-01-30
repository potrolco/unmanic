<template>
  <div class="led-display inline-flex items-center justify-center px-3 py-1 bg-black border border-gray-800 rounded">
    <span
      class="led-text font-mono font-bold tracking-wider"
      :class="[colorClass, sizeClass]"
      :style="{ textShadow: glowShadow }"
    >
      {{ displayValue }}
    </span>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'

const props = withDefaults(defineProps<{
  value: string | number
  color?: 'orange' | 'green' | 'red' | 'cyan'
  size?: 'sm' | 'md' | 'lg'
}>(), {
  color: 'orange',
  size: 'md',
})

const displayValue = computed(() => {
  return typeof props.value === 'number' ? props.value.toFixed(0) : props.value
})

const colorClass = computed(() => {
  const colors = {
    orange: 'text-led-orange',
    green: 'text-led-green',
    red: 'text-led-red',
    cyan: 'text-crt-cyan',
  }
  return colors[props.color]
})

const sizeClass = computed(() => {
  const sizes = {
    sm: 'text-sm',
    md: 'text-base',
    lg: 'text-xl',
  }
  return sizes[props.size]
})

const glowShadow = computed(() => {
  const glows = {
    orange: '0 0 10px rgba(255, 102, 0, 0.8), 0 0 20px rgba(255, 102, 0, 0.4)',
    green: '0 0 10px rgba(0, 255, 0, 0.8), 0 0 20px rgba(0, 255, 0, 0.4)',
    red: '0 0 10px rgba(255, 0, 0, 0.8), 0 0 20px rgba(255, 0, 0, 0.4)',
    cyan: '0 0 10px rgba(0, 255, 255, 0.8), 0 0 20px rgba(0, 255, 255, 0.4)',
  }
  return glows[props.color]
})
</script>

<style scoped>
.led-display {
  background: linear-gradient(180deg, #1a1a1a 0%, #0a0a0a 100%);
  box-shadow: inset 0 2px 4px rgba(0, 0, 0, 0.6), 0 1px 2px rgba(255, 255, 255, 0.1);
}

.led-text {
  letter-spacing: 0.1em;
}
</style>
