<script setup>
// 极简图标库：全部用内联 SVG，不依赖任何图标包，离线也能显示。
import { computed } from 'vue'

const props = defineProps({
  name: { type: String, default: 'dot' },
  size: { type: [Number, String], default: 20 }
})

const PATHS = {
  compass: '<circle cx="12" cy="12" r="9"/><path d="M15.6 8.4 13.7 13.7 8.4 15.6 10.3 10.3Z"/>',
  list: '<path d="M9 6h11M9 12h11M9 18h11"/><circle cx="4.5" cy="6" r="1.1"/><circle cx="4.5" cy="12" r="1.1"/><circle cx="4.5" cy="18" r="1.1"/>',
  stack: '<rect x="4" y="3.5" width="16" height="4.2" rx="1.4"/><rect x="4" y="9.9" width="16" height="4.2" rx="1.4"/><rect x="4" y="16.3" width="16" height="4.2" rx="1.4"/>',
  grid: '<rect x="3.5" y="3.5" width="17" height="17" rx="2.5"/><path d="M3.5 10h17M10 3.5v17"/>',
  tree: '<circle cx="12" cy="4.6" r="2.2"/><circle cx="6" cy="18.4" r="2.2"/><circle cx="18" cy="18.4" r="2.2"/><path d="M12 6.8v4.4M12 11.2 6 16.3M12 11.2l6 5.1"/>',
  graph: '<circle cx="5.5" cy="6.5" r="2.2"/><circle cx="18.5" cy="6.5" r="2.2"/><circle cx="12" cy="18.5" r="2.2"/><path d="M7.4 7.6 10.6 16.6M16.6 7.6 13.4 16.6M7.7 6.5h8.6"/>',
  search: '<circle cx="10.8" cy="10.8" r="6.2"/><path d="m20 20-4.8-4.8"/>',
  sort: '<path d="M7 20V4M7 4 4 7.4M7 4l3 3.4"/><path d="M17 4v16M17 20l3-3.4M17 20l-3-3.4"/>',
  lock: '<rect x="4.5" y="10" width="15" height="10.5" rx="2.4"/><path d="M8 10V7.2a4 4 0 0 1 8 0V10"/>',
  check: '<path d="m5 12.6 4.3 4.3L19 6.4"/>',
  copy: '<rect x="9" y="9" width="11.5" height="11.5" rx="2.2"/><path d="M15 5.6H6.2A2.2 2.2 0 0 0 4 7.8V16"/>',
  sparkles: '<path d="M11.5 3.5 13.2 8l4.5 1.7-4.5 1.7L11.5 16l-1.7-4.6L5.3 9.7 9.8 8Z"/><path d="m18 15 .9 2.3 2.3.9-2.3.9-.9 2.3-.9-2.3-2.3-.9 2.3-.9Z"/>',
  'arrow-left': '<path d="M15 5.5 8 12l7 6.5"/>',
  'arrow-right': '<path d="M9 5.5 16 12l-7 6.5"/>',
  play: '<path d="M8.5 5.2v13.6L19 12Z"/>',
  pause: '<path d="M9 5v14M15 5v14"/>',
  refresh: '<path d="M20 11a8 8 0 1 0-2.4 6.3"/><path d="M20 4v7h-7"/>',
  book: '<path d="M5 5.2A2.2 2.2 0 0 1 7.2 3H19v17.6H7.2A2.2 2.2 0 0 0 5 22.8Z"/><path d="M5 18.6h14"/>',
  code: '<path d="m9 7.5-4.5 4.5L9 16.5M15 7.5l4.5 4.5L15 16.5"/>',
  target: '<circle cx="12" cy="12" r="8.4"/><circle cx="12" cy="12" r="3.4"/>',
  clock: '<circle cx="12" cy="12" r="8.4"/><path d="M12 7.4V12l3.2 2"/>',
  flame: '<path d="M12 3s5 4.2 5 9a5 5 0 0 1-10 0c0-2 1-3.4 2-4.4 0 2 1 3 2 3 1.4 0 2-1.2 1-7.6Z"/>',
  dot: '<circle cx="12" cy="12" r="4"/>',
  trophy: '<path d="M8 4h8v5a4 4 0 0 1-8 0Z"/><path d="M8 5.5H5.5V7a3 3 0 0 0 3 3M16 5.5h2.5V7a3 3 0 0 1-3 3"/><path d="M12 13v3.5M8.5 20h7M10 16.5h4"/>',
  chevron: '<path d="m6.5 9.5 5.5 5.5 5.5-5.5"/>',
  trash: '<path d="M5 7h14M10 7V4.8h4V7M7 7l1 13h8l1-13"/>',
  bulb: '<path d="M9 18h6M10 21h4"/><path d="M12 3a6 6 0 0 0-3.6 10.8c.5.4.8 1 .8 1.7V16h5.6v-.5c0-.7.3-1.3.8-1.7A6 6 0 0 0 12 3Z"/>',
  send: '<path d="m4 12 16-8-5.5 16-3-6.5Z"/>',
  warn: '<path d="M12 4.5 21 19.5H3Z"/><path d="M12 10v4M12 17h.01"/>'
}

const inner = computed(() => PATHS[props.name] || PATHS.dot)
const px = computed(() => `${props.size}px`)
</script>

<template>
  <svg
    class="icon"
    :width="px"
    :height="px"
    viewBox="0 0 24 24"
    fill="none"
    stroke="currentColor"
    stroke-width="1.8"
    stroke-linecap="round"
    stroke-linejoin="round"
    aria-hidden="true"
    v-html="inner"
  />
</template>

<style scoped>
.icon {
  display: inline-block;
  flex: none;
  vertical-align: -0.15em;
}
</style>
