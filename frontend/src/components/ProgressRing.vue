<script setup>
import { computed } from 'vue'

const props = defineProps({
  percent: { type: Number, default: 0 },
  size: { type: Number, default: 54 },
  stroke: { type: Number, default: 5 },
  color: { type: String, default: 'var(--accent)' },
  label: { type: String, default: '' }
})

const radius = computed(() => (props.size - props.stroke) / 2)
const circumference = computed(() => 2 * Math.PI * radius.value)
const offset = computed(
  () => circumference.value * (1 - Math.min(100, Math.max(0, props.percent)) / 100)
)
</script>

<template>
  <div class="ring" :style="{ width: size + 'px', height: size + 'px' }">
    <svg :width="size" :height="size" :viewBox="`0 0 ${size} ${size}`">
      <circle
        :cx="size / 2"
        :cy="size / 2"
        :r="radius"
        fill="none"
        stroke="var(--bg-soft)"
        :stroke-width="stroke"
      />
      <circle
        :cx="size / 2"
        :cy="size / 2"
        :r="radius"
        fill="none"
        :stroke="color"
        :stroke-width="stroke"
        stroke-linecap="round"
        :stroke-dasharray="circumference"
        :stroke-dashoffset="offset"
        :transform="`rotate(-90 ${size / 2} ${size / 2})`"
        class="ring-progress"
      />
    </svg>
    <span class="ring-text">{{ label || Math.round(percent) + '%' }}</span>
  </div>
</template>

<style scoped>
.ring {
  position: relative;
  display: grid;
  place-items: center;
  flex: none;
}
.ring svg {
  position: absolute;
  inset: 0;
}
.ring-progress {
  transition: stroke-dashoffset 0.6s ease;
}
.ring-text {
  font-size: 11px;
  font-weight: 700;
  color: var(--ink-2);
  font-variant-numeric: tabular-nums;
}
</style>
