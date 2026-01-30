<template>
  <div class="vu-meter">
    <!-- Label -->
    <div v-if="label" class="text-xs text-gray-400 mb-1">{{ label }}</div>

    <!-- Meter container -->
    <div class="vu-meter-container flex items-center gap-0.5">
      <!-- Segments -->
      <div
        v-for="i in totalSegments"
        :key="i"
        class="vu-segment"
        :class="[
          getSegmentClass(i),
          i <= activeSegments ? 'active' : 'inactive'
        ]"
      />

      <!-- Peak hold indicator -->
      <div v-if="showPeak && peakSegment > 0" class="ml-2 flex items-center">
        <div class="w-1 h-4 bg-led-red" style="box-shadow: 0 0 8px rgba(255, 0, 0, 0.8)"></div>
      </div>
    </div>

    <!-- Percentage label -->
    <div v-if="showValue" class="text-xs text-crt-phosphor mt-1 font-terminal">
      {{ Math.round(percentage) }}%
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, ref, watch } from 'vue'

const props = withDefaults(defineProps<{
  value: number // 0-100
  label?: string
  totalSegments?: number
  showPeak?: boolean
  showValue?: boolean
}>(), {
  totalSegments: 20,
  showPeak: true,
  showValue: true,
})

const peakSegment = ref(0)

const percentage = computed(() => Math.max(0, Math.min(100, props.value)))

const activeSegments = computed(() => {
  return Math.round((percentage.value / 100) * props.totalSegments)
})

// Update peak hold
watch(activeSegments, (newVal) => {
  if (newVal > peakSegment.value) {
    peakSegment.value = newVal
    // Decay peak slowly
    setTimeout(() => {
      peakSegment.value = Math.max(0, peakSegment.value - 1)
    }, 1000)
  }
})

function getSegmentClass(index: number) {
  const percent = (index / props.totalSegments) * 100
  if (percent < 60) return 'segment-green'
  if (percent < 85) return 'segment-amber'
  return 'segment-red'
}
</script>

<style scoped>
.vu-segment {
  width: 8px;
  height: 16px;
  border-radius: 1px;
  transition: all 0.1s ease;
}

.vu-segment.inactive {
  background-color: #1a1a1a;
  border: 1px solid #2a2a2a;
}

.vu-segment.active.segment-green {
  background-color: #00ff00;
  box-shadow: 0 0 6px rgba(0, 255, 0, 0.6);
  border: 1px solid #00ff00;
}

.vu-segment.active.segment-amber {
  background-color: #ff9500;
  box-shadow: 0 0 6px rgba(255, 149, 0, 0.6);
  border: 1px solid #ff9500;
}

.vu-segment.active.segment-red {
  background-color: #ff3333;
  box-shadow: 0 0 6px rgba(255, 51, 51, 0.6);
  border: 1px solid #ff3333;
}
</style>
