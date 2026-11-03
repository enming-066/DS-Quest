<script setup>
import Icon from './Icon.vue'

defineProps({
  index: { type: Number, default: 0 },
  total: { type: Number, default: 0 },
  playing: { type: Boolean, default: false }
})
const emit = defineEmits(['prev', 'next', 'play', 'pause', 'reset'])
</script>

<template>
  <div class="controls">
    <div class="ctrl-left">
      <button class="mini" title="回到第一步" @click="emit('reset')">
        <Icon name="refresh" :size="15" />
      </button>
      <button class="mini" :disabled="index <= 0" @click="emit('prev')">
        <Icon name="arrow-left" :size="15" />
      </button>
      <button class="mini play" @click="playing ? emit('pause') : emit('play')">
        <Icon :name="playing ? 'pause' : 'play'" :size="15" />
      </button>
      <button class="mini" :disabled="index >= total - 1" @click="emit('next')">
        <Icon name="arrow-right" :size="15" />
      </button>
    </div>
    <div class="dots">
      <span
        v-for="n in total"
        :key="n"
        class="dot-item"
        :class="{ on: n - 1 === index, done: n - 1 < index }"
      ></span>
    </div>
    <span class="counter">{{ total ? index + 1 : 0 }} / {{ total }}</span>
  </div>
</template>

<style scoped>
.controls {
  display: flex;
  align-items: center;
  gap: 14px;
  padding-top: 12px;
}
.ctrl-left {
  display: flex;
  gap: 6px;
}
.mini {
  width: 32px;
  height: 32px;
  display: grid;
  place-items: center;
  border-radius: 9px;
  border: 1px solid var(--line);
  background: var(--surface);
  color: var(--ink-2);
}
.mini:hover:not(:disabled) {
  border-color: var(--accent);
  color: var(--accent);
}
.mini:disabled {
  opacity: 0.4;
  cursor: not-allowed;
}
.mini.play {
  background: var(--accent);
  border-color: var(--accent);
  color: #fff;
}
.mini.play:hover {
  color: #fff;
  filter: brightness(1.06);
}
.dots {
  display: flex;
  gap: 5px;
  flex-wrap: wrap;
}
.dot-item {
  width: 7px;
  height: 7px;
  border-radius: 50%;
  background: var(--line-strong);
  transition: all 0.2s ease;
}
.dot-item.done {
  background: #b9b5f0;
}
.dot-item.on {
  background: var(--accent);
  transform: scale(1.35);
}
.counter {
  margin-left: auto;
  font-size: 12px;
  color: var(--muted);
  font-variant-numeric: tabular-nums;
}
</style>
