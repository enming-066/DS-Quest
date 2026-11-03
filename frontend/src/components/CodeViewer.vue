<script setup>
import { computed, ref } from 'vue'
import Icon from './Icon.vue'
import { toast } from '../store'

const props = defineProps({
  code: { type: String, default: '' },
  lang: { type: String, default: 'cpp' },
  explanations: { type: Array, default: () => [] },
  filename: { type: String, default: '' }
})

const lines = computed(() => props.code.replace(/\r\n/g, '\n').split('\n'))
const active = ref(-1)
const copied = ref(false)

// 解释用"锚点文本"而不是行号，这样以后改代码不会导致高亮错位
const ranges = computed(() =>
  props.explanations.map((exp) => {
    const anchor = (exp.anchor || '').trim()
    let start = lines.value.findIndex((line) => line.includes(anchor))
    if (start < 0) start = -1
    return { ...exp, start, end: start < 0 ? -1 : start + Math.max(1, exp.span || 1) - 1 }
  })
)

function isHighlighted(index) {
  const current = ranges.value[active.value]
  if (!current || current.start < 0) return false
  return index >= current.start && index <= current.end
}

function pick(index) {
  active.value = active.value === index ? -1 : index
  const current = ranges.value[index]
  if (current?.start >= 0) {
    const el = document.querySelector(`[data-line="${current.start}"]`)
    el?.scrollIntoView({ block: 'center', behavior: 'smooth' })
  }
}

async function copy() {
  try {
    await navigator.clipboard.writeText(props.code)
  } catch {
    const area = document.createElement('textarea')
    area.value = props.code
    document.body.appendChild(area)
    area.select()
    document.execCommand('copy')
    area.remove()
  }
  copied.value = true
  toast('代码已复制', 'success', 1600)
  setTimeout(() => (copied.value = false), 1600)
}
</script>

<template>
  <div class="code-viewer">
    <div class="code-head">
      <span class="file">
        <Icon name="code" :size="14" />
        {{ filename || lang.toUpperCase() }}
      </span>
      <button class="copy-btn" @click="copy">
        <Icon :name="copied ? 'check' : 'copy'" :size="14" />
        {{ copied ? '已复制' : '复制' }}
      </button>
    </div>

    <div class="code-body">
      <div class="code-lines">
        <div
          v-for="(line, index) in lines"
          :key="index"
          class="code-line"
          :class="{ hl: isHighlighted(index) }"
          :data-line="index"
        >
          <span class="ln">{{ index + 1 }}</span>
          <code class="src">{{ line || ' ' }}</code>
        </div>
      </div>

      <aside v-if="explanations.length" class="notes">
        <div class="notes-title">逐段解释 · 点一下高亮对应代码</div>
        <button
          v-for="(exp, index) in ranges"
          :key="index"
          class="note"
          :class="{ active: active === index }"
          @click="pick(index)"
        >
          <span class="note-idx">{{ index + 1 }}</span>
          <span class="note-text">{{ exp.text }}</span>
        </button>
      </aside>
    </div>
  </div>
</template>

<style scoped>
.code-viewer {
  border: 1px solid var(--line);
  border-radius: 14px;
  overflow: hidden;
  background: #1c1b2b;
}
.code-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 9px 14px;
  background: #232136;
  border-bottom: 1px solid #302d48;
}
.file {
  display: inline-flex;
  align-items: center;
  gap: 7px;
  color: #a9a6c9;
  font-size: 12px;
  font-family: var(--font-mono);
  letter-spacing: 0.04em;
}
.copy-btn {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  border: 1px solid #3a3753;
  background: #2b2841;
  color: #cbc8e4;
  border-radius: 8px;
  padding: 4px 10px;
  font-size: 12px;
}
.copy-btn:hover {
  background: #363253;
}
.code-body {
  display: grid;
  grid-template-columns: minmax(0, 1fr);
}
.code-lines {
  overflow-x: auto;
  padding: 10px 0;
  max-height: 560px;
  overflow-y: auto;
}
.code-line {
  display: flex;
  align-items: flex-start;
  padding: 0 14px 0 0;
  font-family: var(--font-mono);
  font-size: 13px;
  line-height: 1.72;
  white-space: pre;
  transition: background 0.2s ease;
}
.code-line.hl {
  background: rgba(139, 92, 246, 0.18);
  box-shadow: inset 3px 0 0 #8b5cf6;
}
.ln {
  flex: none;
  width: 46px;
  padding-right: 14px;
  text-align: right;
  color: #5d5a7d;
  user-select: none;
  font-size: 12px;
}
.src {
  color: #e6e4f7;
  font-family: inherit;
}
.notes {
  border-top: 1px solid #302d48;
  padding: 14px;
  background: #201e31;
  display: flex;
  flex-direction: column;
  gap: 8px;
}
.notes-title {
  font-size: 11px;
  letter-spacing: 0.08em;
  text-transform: uppercase;
  color: #7c789f;
  margin-bottom: 2px;
}
.note {
  display: flex;
  gap: 10px;
  text-align: left;
  border: 1px solid transparent;
  background: #262338;
  border-radius: 10px;
  padding: 9px 12px;
  color: #c4c1dd;
  font-size: 13px;
  line-height: 1.65;
}
.note:hover {
  background: #2e2a44;
}
.note.active {
  border-color: #7c5cf6;
  background: #322c52;
  color: #efeafe;
}
.note-idx {
  flex: none;
  width: 18px;
  height: 18px;
  margin-top: 2px;
  border-radius: 50%;
  background: #3a3559;
  color: #b9b4e0;
  font-size: 11px;
  line-height: 18px;
  text-align: center;
}
.note.active .note-idx {
  background: #7c5cf6;
  color: #fff;
}
@media (min-width: 1100px) {
  .code-body {
    grid-template-columns: minmax(0, 1fr) 320px;
  }
  .notes {
    border-top: none;
    border-left: 1px solid #302d48;
    max-height: 560px;
    overflow-y: auto;
  }
}
</style>
