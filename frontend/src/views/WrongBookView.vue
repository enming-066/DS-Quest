<script setup>
import { computed, onMounted, ref } from 'vue'
import { RouterLink } from 'vue-router'
import Icon from '../components/Icon.vue'
import { api } from '../api'
import { refreshBootstrap, state, toast } from '../store'

const items = ref([])
const loading = ref(true)
const error = ref('')
const filter = ref('open')
const editing = ref('')
const noteText = ref('')
const saving = ref(false)

const shown = computed(() =>
  filter.value === 'open' ? items.value.filter((i) => !i.resolved) : items.value
)
const openCount = computed(() => items.value.filter((i) => !i.resolved).length)
const solvedCount = computed(() => items.value.filter((i) => i.resolved).length)

const VERDICT_TEXT = {
  WA: '答案错误',
  TLE: '运行超时',
  MLE: '内存超限',
  RE: '运行错误',
  CE: '编译错误'
}

async function load() {
  loading.value = true
  error.value = ''
  try {
    const data = await api.wrongbook()
    items.value = data.items || []
  } catch (err) {
    error.value = err.message
  } finally {
    loading.value = false
  }
}

onMounted(load)

function startNote(item) {
  editing.value = item.problem_id
  noteText.value = item.note || ''
}

async function saveNote(item) {
  saving.value = true
  try {
    await api.setNote(item.problem_id, noteText.value)
    item.note = noteText.value
    editing.value = ''
    toast('笔记已保存', 'success', 1600)
  } catch (err) {
    toast(err.message, 'error')
  } finally {
    saving.value = false
  }
}

async function resolve(item) {
  try {
    await api.resolveWrong(item.problem_id)
    item.resolved = 1
    toast('已标记为掌握', 'success', 1600)
    refreshBootstrap().catch(() => {})
  } catch (err) {
    toast(err.message, 'error')
  }
}

function shortTime(raw) {
  if (!raw) return ''
  return raw.slice(5, 16)
}
</script>

<template>
  <div class="page">
    <header class="head">
      <div>
        <h1>错题本</h1>
        <p>做错的题会自动进来。重做通过了，这里会自动标成"已掌握"。</p>
      </div>
      <div class="head-stats">
        <div class="hs">
          <strong>{{ openCount }}</strong>
          <em>待复习</em>
        </div>
        <div class="hs">
          <strong>{{ solvedCount }}</strong>
          <em>已掌握</em>
        </div>
        <div class="hs">
          <strong>{{ state.progress.problemsSolved.length }}</strong>
          <em>累计通过</em>
        </div>
      </div>
    </header>

    <div class="filter">
      <button class="fbtn" :class="{ on: filter === 'open' }" @click="filter = 'open'">
        待复习 <span>{{ openCount }}</span>
      </button>
      <button class="fbtn" :class="{ on: filter === 'all' }" @click="filter = 'all'">
        全部 <span>{{ items.length }}</span>
      </button>
    </div>

    <div v-if="loading" class="card card-pad muted">加载中…</div>
    <div v-else-if="error" class="card card-pad err">{{ error }}</div>

    <div v-else-if="!shown.length" class="card empty">
      <span class="empty-emoji">🎉</span>
      <p>{{ filter === 'open' ? '没有待复习的错题，保持住。' : '错题本还是空的，说明你还没做错过题。' }}</p>
      <RouterLink to="/" class="btn btn-sm">回学习地图</RouterLink>
    </div>

    <div v-else class="list">
      <article v-for="item in shown" :key="item.problem_id" class="item card" :class="{ done: item.resolved }">
        <div class="item-main">
          <div class="row wrap" style="gap: 8px">
            <span class="verdict" :class="item.last_verdict.toLowerCase()">
              {{ VERDICT_TEXT[item.last_verdict] || item.last_verdict }}
            </span>
            <h3>{{ item.title }}</h3>
            <span v-if="item.resolved" class="chip chip-success">
              <Icon name="check" :size="12" /> 已掌握
            </span>
          </div>
          <div class="meta">
            <span>错了 {{ item.attempts }} 次</span>
            <span>最近一次 {{ shortTime(item.last_failed_at) }}</span>
            <span v-for="tag in item.tags" :key="tag" class="chip">{{ tag }}</span>
          </div>

          <div v-if="editing === item.problem_id" class="editor">
            <textarea
              v-model="noteText"
              class="input textarea"
              rows="3"
              placeholder="写下你当时错在哪：是边界？是指针顺序？还是复杂度没想清楚？"
            ></textarea>
            <div class="editor-actions">
              <button class="btn btn-sm btn-primary" :disabled="saving" @click="saveNote(item)">
                保存笔记
              </button>
              <button class="btn btn-sm btn-ghost" @click="editing = ''">取消</button>
            </div>
          </div>
          <p v-else-if="item.note" class="note">
            <Icon name="bulb" :size="13" />
            <span>{{ item.note }}</span>
          </p>
        </div>

        <div class="item-actions">
          <RouterLink
            :to="`/module/${item.moduleId}/problem/${item.problem_id}`"
            class="btn btn-sm btn-primary"
          >
            再做一次
          </RouterLink>
          <button v-if="!item.resolved" class="btn btn-sm" @click="startNote(item)">
            {{ item.note ? '改笔记' : '记笔记' }}
          </button>
          <button v-if="!item.resolved" class="btn btn-sm btn-ghost" @click="resolve(item)">
            我已经会了
          </button>
        </div>
      </article>
    </div>
  </div>
</template>

<style scoped>
.head {
  display: flex;
  justify-content: space-between;
  align-items: flex-end;
  gap: 20px;
  flex-wrap: wrap;
  margin-bottom: 22px;
}
.head h1 {
  font-size: 26px;
}
.head p {
  margin: 6px 0 0;
  color: var(--muted);
  font-size: 13.5px;
}
.head-stats {
  display: flex;
  gap: 24px;
}
.hs {
  text-align: right;
}
.hs strong {
  display: block;
  font-size: 22px;
  font-variant-numeric: tabular-nums;
}
.hs em {
  font-style: normal;
  font-size: 11.5px;
  color: var(--muted);
}
.filter {
  display: flex;
  gap: 6px;
  margin-bottom: 16px;
}
.fbtn {
  border: 1px solid transparent;
  background: transparent;
  padding: 7px 14px;
  border-radius: 999px;
  font-size: 13px;
  font-weight: 600;
  color: var(--muted);
}
.fbtn.on {
  background: var(--surface);
  border-color: var(--line);
  color: var(--ink);
  box-shadow: var(--shadow-sm);
}
.fbtn span {
  color: var(--accent);
  font-size: 11px;
  margin-left: 4px;
}
.list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}
.item {
  display: flex;
  gap: 18px;
  padding: 18px 20px;
  align-items: flex-start;
}
.item.done {
  background: var(--surface-2);
  opacity: 0.85;
}
.item-main {
  flex: 1;
  min-width: 0;
}
.item h3 {
  font-size: 15.5px;
}
.verdict {
  font-size: 11px;
  font-weight: 700;
  border-radius: 999px;
  padding: 2px 9px;
}
.verdict.wa,
.verdict.re {
  background: var(--danger-soft);
  color: var(--danger);
}
.verdict.ce {
  background: var(--warn-soft);
  color: var(--warn);
}
.verdict.tle,
.verdict.mle {
  background: var(--info-soft);
  color: var(--info);
}
.meta {
  display: flex;
  gap: 14px;
  flex-wrap: wrap;
  align-items: center;
  margin-top: 8px;
  font-size: 12px;
  color: var(--muted);
}
.note {
  display: flex;
  gap: 8px;
  align-items: flex-start;
  margin: 12px 0 0;
  padding: 9px 12px;
  border-radius: 8px;
  background: #fbf7ff;
  border-left: 3px solid var(--accent-2);
  font-size: 12.5px;
  color: var(--ink-2);
}
.editor {
  margin-top: 12px;
  display: flex;
  flex-direction: column;
  gap: 8px;
}
.editor-actions {
  display: flex;
  gap: 8px;
}
.item-actions {
  display: flex;
  flex-direction: column;
  gap: 8px;
  flex: none;
}
.muted {
  color: var(--muted);
}
.err {
  color: var(--danger);
}
@media (max-width: 720px) {
  .item {
    flex-direction: column;
  }
  .item-actions {
    flex-direction: row;
    flex-wrap: wrap;
  }
  .head-stats {
    gap: 16px;
  }
}
</style>
