<script setup>
import { computed, ref } from 'vue'
import Icon from './Icon.vue'
import MarkdownView from './MarkdownView.vue'
import { api } from '../api'
import { state } from '../store'

const props = defineProps({
  problem: { type: Object, required: true },
  code: { type: String, default: '' },
  result: { type: Object, default: null },
  open: { type: Boolean, default: false }
})
const emit = defineEmits(['update:open'])

const level = ref(2)
const question = ref('')
const busy = ref(false)
const answer = ref('')
const meta = ref(null)
const failure = ref(null)

const LEVELS = [
  { value: 2, name: '给个方向', desc: '只提问，不指出具体位置' },
  { value: 3, name: '定位问题', desc: '指出哪段代码有问题' },
  { value: 4, name: '参考思路', desc: '给关键片段（题库有解则免费）' }
]

const hasApi = computed(() => state.ai.enabled)
const isLocalSolution = computed(() => level.value === 4 && Boolean(props.problem.solution))
const costNote = computed(() => {
  if (!hasApi.value) return '没有配置 API Key，只能使用免费功能'
  if (isLocalSolution.value) return '这一层直接用题库里的参考解，不消耗额度'
  return `本次会消耗 1 次额度，今日还剩 ${state.ai.remaining} 次`
})

async function ask() {
  busy.value = true
  answer.value = ''
  failure.value = null
  meta.value = null
  try {
    const res = await api.coach({
      problemId: props.problem.id,
      code: props.code,
      level: level.value,
      question: question.value,
      verdict: props.result?.verdict || null,
      result: props.result || null
    })
    if (!res.ok) {
      failure.value = res
      return
    }
    answer.value = res.content
    meta.value = res
    if (typeof res.remaining === 'number') state.ai.remaining = res.remaining
  } catch (err) {
    failure.value = { error: err.message, hint: '检查后端是否在运行。' }
  } finally {
    busy.value = false
  }
}
</script>

<template>
  <div v-if="open" class="drawer-mask" @click.self="emit('update:open', false)">
    <aside class="drawer">
      <header class="drawer-head">
        <div class="row">
          <span class="spark"><Icon name="sparkles" :size="17" /></span>
          <div>
            <h3>AI 助教</h3>
            <p>只在你点按钮时调用，不会偷偷花钱</p>
          </div>
        </div>
        <button class="close" @click="emit('update:open', false)">
          <Icon name="arrow-right" :size="17" />
        </button>
      </header>

      <div class="drawer-body">
        <div v-if="!hasApi" class="notice">
          <strong>AI 还没启用</strong>
          <p>
            在 <code>backend/.env</code> 里填上 <code>DEEPSEEK_API_KEY</code> 再重启后端就行。
          </p>
          <p>不填也能用：免费的题库提示、本地错因检查、参考解法都在页面上。</p>
        </div>

        <div class="field">
          <label>想要什么程度的帮助？</label>
          <div class="levels">
            <button
              v-for="item in LEVELS"
              :key="item.value"
              class="level"
              :class="{ on: level === item.value }"
              @click="level = item.value"
            >
              <strong>{{ item.name }}</strong>
              <span>{{ item.desc }}</span>
            </button>
          </div>
        </div>

        <div class="field">
          <label>补充说明（可选）</label>
          <textarea
            v-model="question"
            class="input textarea"
            rows="2"
            placeholder="比如：我理解不了为什么这里要从后往前挪"
          ></textarea>
        </div>

        <div class="cost" :class="{ warn: !isLocalSolution && hasApi }">
          <Icon name="bulb" :size="14" />
          <span>{{ costNote }}</span>
        </div>

        <button class="btn btn-primary btn-lg ask" :disabled="busy || !hasApi" @click="ask">
          <span v-if="busy" class="spinner"></span>
          <Icon v-else name="send" :size="16" />
          {{ busy ? '分析中…' : '让 AI 看看我的代码' }}
        </button>

        <div v-if="failure" class="failure">
          <strong>{{ failure.error }}</strong>
          <p v-if="failure.hint">{{ failure.hint }}</p>
        </div>

        <div v-if="answer" class="answer">
          <div class="answer-head">
            <span class="chip chip-accent">
              <Icon name="sparkles" :size="12" />
              {{ meta?.source === 'local' ? '题库参考解' : meta?.cached ? '来自缓存' : 'DeepSeek 生成' }}
            </span>
            <span v-if="meta?.usage?.total_tokens" class="tokens">
              {{ meta.usage.total_tokens }} tokens
            </span>
          </div>
          <MarkdownView :source="answer" />
          <p class="disclaimer">
            AI 的解释只作参考，最终以判题结果和课本定义为准。
          </p>
        </div>

        <div v-if="!answer && !failure" class="hint-box">
          <Icon name="bulb" :size="15" />
          <div>
            <strong>先试试免费的</strong>
            <p>
              「提示」标签页里有题库自带的分层提示；判题失败时，下方还会自动给出本地错因检查，
              这两样都不花钱，通常已经够用了。
            </p>
          </div>
        </div>
      </div>
    </aside>
  </div>
</template>

<style scoped>
.drawer-mask {
  position: fixed;
  inset: 0;
  background: rgba(24, 22, 40, 0.28);
  backdrop-filter: blur(2px);
  z-index: 900;
  display: flex;
  justify-content: flex-end;
}
.drawer {
  width: min(440px, 100vw);
  height: 100%;
  background: var(--surface);
  box-shadow: -24px 0 60px -30px rgba(20, 20, 43, 0.45);
  display: flex;
  flex-direction: column;
  animation: slide-in 0.22s ease;
}
@keyframes slide-in {
  from {
    transform: translateX(24px);
    opacity: 0.6;
  }
  to {
    transform: translateX(0);
    opacity: 1;
  }
}
.drawer-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 16px 20px;
  border-bottom: 1px solid var(--line);
}
.drawer-head h3 {
  font-size: 15px;
}
.drawer-head p {
  margin: 1px 0 0;
  font-size: 11.5px;
  color: var(--muted);
}
.spark {
  width: 34px;
  height: 34px;
  border-radius: 10px;
  display: grid;
  place-items: center;
  color: #fff;
  background: linear-gradient(135deg, var(--accent), var(--accent-2));
}
.close {
  border: none;
  background: transparent;
  color: var(--muted);
  width: 30px;
  height: 30px;
  border-radius: 8px;
  display: grid;
  place-items: center;
}
.close:hover {
  background: var(--bg-soft);
}
.drawer-body {
  padding: 18px 20px 40px;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
  gap: 16px;
}
.field label {
  display: block;
  font-size: 12px;
  font-weight: 700;
  color: var(--ink-2);
  margin-bottom: 8px;
}
.levels {
  display: flex;
  flex-direction: column;
  gap: 8px;
}
.level {
  display: flex;
  flex-direction: column;
  gap: 2px;
  text-align: left;
  padding: 10px 13px;
  border-radius: 10px;
  border: 1px solid var(--line);
  background: var(--surface-2);
}
.level strong {
  font-size: 13px;
  color: var(--ink);
}
.level span {
  font-size: 11.5px;
  color: var(--muted);
}
.level.on {
  border-color: var(--accent);
  background: var(--accent-soft);
}
.level.on strong {
  color: var(--accent);
}
.cost {
  display: flex;
  gap: 8px;
  align-items: center;
  font-size: 12px;
  color: var(--success);
  background: var(--success-soft);
  border-radius: 8px;
  padding: 8px 12px;
}
.cost.warn {
  color: var(--warn);
  background: var(--warn-soft);
}
.ask {
  width: 100%;
}
.spinner {
  width: 14px;
  height: 14px;
  border-radius: 50%;
  border: 2px solid rgba(255, 255, 255, 0.4);
  border-top-color: #fff;
  animation: spin 0.8s linear infinite;
}
@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}
.notice {
  border-radius: 10px;
  background: var(--warn-soft);
  border: 1px solid #f5dcb4;
  padding: 12px 14px;
  color: #92400e;
}
.notice strong {
  font-size: 13px;
}
.notice p {
  margin: 4px 0 0;
  font-size: 12px;
  line-height: 1.7;
}
.notice code {
  background: rgba(255, 255, 255, 0.7);
  padding: 1px 5px;
  border-radius: 4px;
  font-family: var(--font-mono);
}
.failure {
  border-radius: 10px;
  background: var(--danger-soft);
  border: 1px solid #f3c6c6;
  padding: 11px 13px;
  color: #8f1d1d;
}
.failure strong {
  font-size: 13px;
}
.failure p {
  margin: 4px 0 0;
  font-size: 12px;
}
.answer {
  border-top: 1px dashed var(--line);
  padding-top: 14px;
}
.answer-head {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}
.tokens {
  font-size: 11px;
  color: var(--muted);
}
.disclaimer {
  margin-top: 14px;
  font-size: 11.5px;
  color: var(--muted);
}
.hint-box {
  display: flex;
  gap: 10px;
  background: var(--surface-2);
  border: 1px dashed var(--line-strong);
  border-radius: 10px;
  padding: 12px 14px;
  color: var(--ink-2);
}
.hint-box strong {
  font-size: 12.5px;
}
.hint-box p {
  margin: 4px 0 0;
  font-size: 12px;
  color: var(--muted);
  line-height: 1.7;
}
</style>
