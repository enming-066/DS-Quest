<script setup>
import { computed, reactive, ref } from 'vue'
import Icon from './Icon.vue'

const props = defineProps({
  code: { type: String, default: '' },
  blanks: { type: Array, default: () => [] },
  submitting: { type: Boolean, default: false },
  filename: { type: String, default: '' }
})
const emit = defineEmits(['submit'])

const answers = reactive({})
const showHints = ref(false)

// 把每一行拆成「普通文本」和「空位」两种片段
const parsed = computed(() => {
  const re = /\/\*BLANK(\d+)\*\//g
  return props.code.split('\n').map((line) => {
    const segments = []
    let last = 0
    let m
    re.lastIndex = 0
    while ((m = re.exec(line)) !== null) {
      if (m.index > last) segments.push({ type: 'text', value: line.slice(last, m.index) })
      segments.push({ type: 'blank', id: m[1] })
      last = m.index + m[0].length
    }
    if (last < line.length) segments.push({ type: 'text', value: line.slice(last) })
    return segments
  })
})

const filledCount = computed(
  () => props.blanks.filter((b) => (answers[b.id] || '').trim().length > 0).length
)

function blankInfo(id) {
  return props.blanks.find((b) => String(b.id) === String(id)) || {}
}

function submit() {
  const payload = {}
  for (const b of props.blanks) payload[String(b.id)] = (answers[b.id] || '').trim()
  emit('submit', payload)
}
</script>

<template>
  <div class="fill-editor">
    <div class="fill-head">
      <span class="file">
        <Icon name="code" :size="14" />
        {{ filename || 'fill.cpp' }}
      </span>
      <span class="progress">已填 {{ filledCount }} / {{ blanks.length }}</span>
    </div>

    <div class="code">
      <div v-for="(segments, index) in parsed" :key="index" class="line">
        <span class="ln">{{ index + 1 }}</span>
        <code class="src">
          <template v-for="(seg, i) in segments" :key="i">
            <span v-if="seg.type === 'text'">{{ seg.value }}</span>
            <input
              v-else
              v-model="answers[seg.id]"
              class="blank-input"
              :class="{ filled: (answers[seg.id] || '').trim() }"
              :placeholder="blankInfo(seg.id).placeholder || `空 ${seg.id}`"
              :title="blankInfo(seg.id).hint || ''"
              spellcheck="false"
              @keydown.enter.prevent="submit"
            />
          </template>
        </code>
      </div>
    </div>

    <div class="fill-foot">
      <button class="btn btn-sm btn-ghost" @click="showHints = !showHints">
        <Icon name="bulb" :size="14" />
        {{ showHints ? '收起提示' : '看提示' }}
      </button>
      <div class="grow"></div>
      <span class="tip">Ctrl / Enter 直接提交</span>
      <button class="btn btn-sm btn-primary" :disabled="submitting" @click="submit">
        <Icon name="play" :size="14" />
        {{ submitting ? '判题中…' : '提交填空' }}
      </button>
    </div>

    <ul v-if="showHints" class="hints">
      <li v-for="b in blanks" :key="b.id">
        <strong>空 {{ b.id }}</strong>（{{ b.placeholder }}）：{{ b.hint }}
      </li>
    </ul>
  </div>
</template>

<style scoped>
.fill-editor {
  border: 1px solid #302d48;
  border-radius: 14px;
  overflow: hidden;
  background: #1c1b2b;
}
.fill-head {
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
}
.progress {
  font-size: 11.5px;
  color: #8d89b3;
}
.code {
  padding: 12px 0;
  overflow-x: auto;
  max-height: 460px;
  overflow-y: auto;
}
.line {
  display: flex;
  align-items: center;
  font-family: var(--font-mono);
  font-size: 13px;
  line-height: 2.1;
  white-space: pre;
}
.ln {
  flex: none;
  width: 46px;
  padding-right: 14px;
  text-align: right;
  color: #5d5a7d;
  font-size: 12px;
  user-select: none;
}
.src {
  color: #e6e4f7;
  font-family: inherit;
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 2px;
}
.blank-input {
  width: 132px;
  height: 24px;
  padding: 0 8px;
  border-radius: 6px;
  border: 1px dashed #6d63b8;
  background: #2a2543;
  color: #efeafe;
  font-family: var(--font-mono);
  font-size: 12.5px;
  outline: none;
  transition: border-color 0.15s ease, background 0.15s ease;
}
.blank-input::placeholder {
  color: #7c789f;
  font-size: 11.5px;
}
.blank-input:focus {
  border-style: solid;
  border-color: #a78bfa;
  background: #322c52;
}
.blank-input.filled {
  border-style: solid;
  border-color: #7c5cf6;
  background: #322c52;
}
.fill-foot {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 10px 14px;
  border-top: 1px solid #302d48;
  background: #201e31;
}
.tip {
  font-size: 11px;
  color: #7c789f;
}
.hints {
  margin: 0;
  padding: 10px 18px 14px;
  background: #201e31;
  border-top: 1px solid #302d48;
  color: #c4c1dd;
  font-size: 12.5px;
  line-height: 1.8;
}
.hints li {
  margin: 4px 0;
}
.hints strong {
  color: #b39cf8;
}
</style>
