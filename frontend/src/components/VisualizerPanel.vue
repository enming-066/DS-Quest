<script setup>
import { computed, ref } from 'vue'
import SeqListViz from './SeqListViz.vue'
import StackViz from './StackViz.vue'
import QueueViz from './QueueViz.vue'

const props = defineProps({
  keys: { type: Array, default: () => ['seqlist', 'stack', 'queue'] },
  compact: { type: Boolean, default: false }
})

const META = {
  seqlist: { label: '顺序表', comp: SeqListViz },
  stack: { label: '栈', comp: StackViz },
  queue: { label: '队列', comp: QueueViz }
}

const active = ref(props.keys[0] || 'seqlist')
const tabs = computed(() => props.keys.map((key) => ({ key, label: META[key]?.label || key })))
const component = computed(() => META[active.value]?.comp || SeqListViz)
</script>

<template>
  <div class="viz-panel card" :class="{ compact }">
    <div v-if="tabs.length > 1" class="viz-tabs">
      <button
        v-for="tab in tabs"
        :key="tab.key"
        class="viz-tab"
        :class="{ on: active === tab.key }"
        @click="active = tab.key"
      >
        {{ tab.label }}
      </button>
    </div>
    <component :is="component" />
  </div>
</template>

<style scoped>
.viz-panel {
  overflow: hidden;
}
.viz-tabs {
  display: flex;
  gap: 6px;
  padding: 14px 18px 0;
}
.viz-tab {
  border: none;
  background: transparent;
  padding: 7px 14px;
  border-radius: 999px;
  font-size: 13px;
  font-weight: 600;
  color: var(--muted);
}
.viz-tab:hover {
  background: var(--bg-soft);
}
.viz-tab.on {
  background: var(--accent-soft);
  color: var(--accent);
}
.compact {
  box-shadow: none;
}
</style>
