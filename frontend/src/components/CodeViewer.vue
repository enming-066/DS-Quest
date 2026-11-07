<script setup>
import { computed, ref } from 'vue'
import Icon from './Icon.vue'
import { toast } from '../store'

const props = defineProps({
  code: { type: String, default: '' },
  lang: { type: String, default: 'cpp' },
  explanations: { type: Array, default: () => [] },
  lineNotes: { type: Array, default: () => [] },
  filename: { type: String, default: '' }
})

const lines = computed(() => props.code.replace(/\r\n/g, '\n').split('\n'))
const active = ref(-1)
const copied = ref(false)
// block = 逐段（讲算法）；line = 逐行（讲语法）
const mode = ref('block')
const picked = ref(-1)

// 解释用"锚点文本"而不是行号，这样以后改代码不会导致高亮错位
const ranges = computed(() =>
  props.explanations.map((exp) => {
    const anchor = (exp.anchor || '').trim()
    let start = lines.value.findIndex((line) => line.includes(anchor))
    if (start < 0) start = -1
    return { ...exp, start, end: start < 0 ? -1 : start + Math.max(1, exp.span || 1) - 1 }
  })
)

// 逐行注释也按锚点定位
const lineMap = computed(() => {
  const map = new Map()
  for (const note of props.lineNotes) {
    const anchor = (note.anchor || '').trim()
    if (!anchor) continue
    const index = lines.value.findIndex((line) => line.includes(anchor))
    if (index >= 0) map.set(index, note)
  }
  return map
})

const currentNote = computed(() => (picked.value >= 0 ? lineMap.value.get(picked.value) : null))
const noteCount = computed(() => lineMap.value.size)

function isHighlighted(index) {
  if (mode.value === 'line') return index === picked.value
  const current = ranges.value[active.value]
  if (!current || current.start < 0) return false
  return index >= current.start && index <= current.end
}

function pick(index) {
  picked.value = picked.value === index ? -1 : index
}

function pickBlock(index) {
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
  <div class="code-viewer" :class="{ 'line-mode': mode === 'line' }">
    <div class="code-head">
      <span class="file">
        <Icon name="code" :size="14" />
        {{ filename || lang.toUpperCase() }}
      </span>
      <div class="head-actions">
        <button
          v-if="lineNotes.length"
          class="mode-btn"
          :class="{ on: mode === 'line' }"
          :title="mode === 'line' ? '切回逐段解释（讲算法）' : '切到逐行拆解（讲语法）'"
          @click="mode = mode === 'line' ? 'block' : 'line'"
        >
          <Icon name="bulb" :size="13" />
          {{ mode === 'line' ? '逐行拆解中' : '逐行拆解' }}
        </button>
        <button class="copy-btn" @click="copy">
          <Icon :name="copied ? 'check' : 'copy'" :size="14" />
          {{ copied ? '已复制' : '复制' }}
        </button>
      </div>
    </div>

    <!-- 逐段模式：点右侧解释，高亮对应片段 -->
    <div v-if="mode === 'block'" class="code-body">
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
          @click="pickBlock(index)"
        >
          <span class="note-idx">{{ index + 1 }}</span>
          <span class="note-text">{{ exp.text }}</span>
        </button>
      </aside>
    </div>

    <!-- 逐行模式：点某一行，右侧讲这行的语法 -->
    <div v-else class="code-body">
      <div class="code-lines">
        <div
          v-for="(line, index) in lines"
          :key="index"
          class="code-line clickable"
          :class="{ hl: isHighlighted(index), noted: lineMap.has(index) }"
          @click="pick(index)"
        >
          <span class="ln">{{ index + 1 }}</span>
          <span v-if="lineMap.has(index)" class="mark"></span>
          <code class="src">{{ line || ' ' }}</code>
        </div>
      </div>

      <aside class="notes">
        <template v-if="currentNote">
          <div class="notes-title">第 {{ picked + 1 }} 行</div>
          <p class="what">{{ currentNote.what }}</p>
          <div v-if="currentNote.syntax" class="syntax-box">
            <span class="tag">语法点</span>
            <span>{{ currentNote.syntax }}</span>
          </div>
          <div v-if="currentNote.c" class="c-box">
            <span class="tag c">C 里怎么写</span>
            <span>{{ currentNote.c }}</span>
          </div>
        </template>
        <template v-else>
          <div class="notes-title">逐行拆解 · 共 {{ noteCount }} 行有注释</div>
          <p class="hint">
            点左边任意一行，看这一行在干什么、用到什么语法、对应的 C 写法是什么。
            带小圆点的行是有注释的重点行。
          </p>
        </template>
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
  gap: 10px;
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
.head-actions {
  display: flex;
  gap: 8px;
}
.mode-btn,
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
.mode-btn.on {
  background: #3b2f63;
  border-color: #7c5cf6;
  color: #efeafe;
}
.copy-btn:hover,
.mode-btn:hover {
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
.code-line.clickable {
  cursor: pointer;
}
.code-line.clickable:hover {
  background: rgba(139, 92, 246, 0.1);
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
.mark {
  flex: none;
  width: 5px;
  height: 5px;
  margin: 11px 8px 0 0;
  border-radius: 50%;
  background: #8b5cf6;
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
  gap: 10px;
}
.notes-title {
  font-size: 11px;
  letter-spacing: 0.08em;
  text-transform: uppercase;
  color: #7c789f;
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
.what {
  margin: 0;
  color: #e6e4f7;
  font-size: 13px;
  line-height: 1.75;
}
.syntax-box,
.c-box {
  display: flex;
  gap: 8px;
  align-items: flex-start;
  font-size: 12.5px;
  line-height: 1.7;
  padding: 9px 11px;
  border-radius: 8px;
}
.syntax-box {
  background: #2c2745;
  color: #cfc9f0;
}
.c-box {
  background: #24283a;
  color: #b9c9e0;
}
.tag {
  flex: none;
  font-size: 10px;
  font-weight: 700;
  color: #b39cf8;
  background: rgba(139, 92, 246, 0.16);
  border-radius: 999px;
  padding: 1px 8px;
  margin-top: 1px;
}
.tag.c {
  color: #8ec7f0;
  background: rgba(56, 132, 191, 0.16);
}
.hint {
  margin: 0;
  font-size: 12.5px;
  color: #9d99bd;
  line-height: 1.8;
}
@media (min-width: 1100px) {
  .code-body {
    grid-template-columns: minmax(0, 1fr) 340px;
  }
  .notes {
    border-top: none;
    border-left: 1px solid #302d48;
    max-height: 560px;
    overflow-y: auto;
  }
}
</style>
