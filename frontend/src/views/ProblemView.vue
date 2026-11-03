<script setup>
import { computed, onMounted, ref, watch } from 'vue'
import { RouterLink, useRoute } from 'vue-router'
import Icon from '../components/Icon.vue'
import MarkdownView from '../components/MarkdownView.vue'
import CodeEditor from '../components/CodeEditor.vue'
import CodeViewer from '../components/CodeViewer.vue'
import VerdictPanel from '../components/VerdictPanel.vue'
import AiCoach from '../components/AiCoach.vue'
import { api } from '../api'
import { applyJudgeProgress, refreshBootstrap, state, toast } from '../store'

const route = useRoute()
const problem = ref(null)
const loading = ref(true)
const error = ref('')
const code = ref('')
const lang = ref('cpp')
const tab = ref('statement')
const submitting = ref(false)
const result = ref(null)
const coachOpen = ref(false)
const revealSolution = ref(false)
const hintShown = ref(1)

const problemId = computed(() => route.params.problemId)
const moduleId = computed(() => route.params.moduleId)
const draftKey = computed(() => `dsq:draft:${problemId.value}`)

const difficultyDots = computed(() => {
  const n = problem.value?.difficulty || 1
  return '★'.repeat(n) + '☆'.repeat(Math.max(0, 5 - n))
})

const visibleHints = computed(() => (problem.value?.hints || []).slice(0, hintShown.value))
const hasMoreHints = computed(
  () => (problem.value?.hints?.length || 0) > hintShown.value
)

async function load() {
  loading.value = true
  error.value = ''
  result.value = null
  try {
    const data = await api.problem(problemId.value)
    problem.value = data
    const draft = localStorage.getItem(draftKey.value)
    if (draft) {
      try {
        const parsed = JSON.parse(draft)
        code.value = parsed.code || data.starterCode
        lang.value = 'cpp'
      } catch {
        code.value = data.starterCode
      }
    } else if (data.savedCode?.code) {
      code.value = data.savedCode.code
      lang.value = 'cpp'
    } else {
      code.value = data.starterCode
    }
  } catch (err) {
    error.value = err.message
  } finally {
    loading.value = false
  }
}

onMounted(load)
watch(problemId, load)

watch([code, lang], () => {
  if (!problem.value) return
  localStorage.setItem(
    draftKey.value,
    JSON.stringify({ code: code.value, lang: 'cpp', at: Date.now() })
  )
})

function resetCode() {
  if (!problem.value) return
  code.value = problem.value.starterCode
  toast('已恢复成初始模板', 'info', 1600)
}

async function submit() {
  if (submitting.value || !problem.value) return
  if (!code.value.trim()) {
    toast('代码是空的', 'error')
    return
  }
  submitting.value = true
  result.value = null
  try {
    const res = await api.judge({ problemId: problemId.value, code: code.value, lang: 'cpp' })
    result.value = res
    applyJudgeProgress(res, problemId.value)
    if (res.verdict === 'AC') {
      refreshBootstrap().catch(() => {})
    }
    // 判题结果出来后把视线带到结果区
    if (window.innerWidth < 1000) {
      document.querySelector('.verdict')?.scrollIntoView({ behavior: 'smooth', block: 'start' })
    }
  } catch (err) {
    toast(err.message || '提交失败', 'error')
  } finally {
    submitting.value = false
  }
}
</script>

<template>
  <div class="page page-wide problem-page">
    <div v-if="loading" class="card card-pad loading">加载中…</div>
    <div v-else-if="error" class="card card-pad err">{{ error }}</div>

    <template v-else-if="problem">
      <header class="p-head">
        <RouterLink :to="`/module/${moduleId}`" class="back">
          <Icon name="arrow-left" :size="15" /> 返回章节
        </RouterLink>
        <div class="p-title-row">
          <h1>{{ problem.title }}</h1>
          <span class="stars">{{ difficultyDots }}</span>
          <span v-if="problem.optional" class="chip chip-lock" title="课件未涉及，不计入章节进度">
            拓展 · 考试不要求
          </span>
          <span v-if="problem.solved" class="chip chip-success">
            <Icon name="check" :size="12" /> 已通过
          </span>
          <span v-for="tag in problem.tags" :key="tag" class="chip">{{ tag }}</span>
        </div>
        <div class="p-actions">
          <button class="btn btn-sm" @click="coachOpen = true">
            <Icon name="sparkles" :size="15" /> 问 AI 助教
          </button>
        </div>
      </header>

      <div class="p-grid">
        <!-- 左：题目 -->
        <section class="statement card">
          <nav class="stmt-tabs">
            <button class="stmt-tab" :class="{ on: tab === 'statement' }" @click="tab = 'statement'">
              题目
            </button>
            <button class="stmt-tab" :class="{ on: tab === 'hints' }" @click="tab = 'hints'">
              提示
              <span class="badge">{{ problem.hints?.length || 0 }}</span>
            </button>
            <button class="stmt-tab" :class="{ on: tab === 'solution' }" @click="tab = 'solution'">
              题解
            </button>
          </nav>

          <div class="stmt-body">
            <template v-if="tab === 'statement'">
              <MarkdownView :source="problem.statement" />
              <div class="io-spec">
                <div class="spec">
                  <h4>输入格式</h4>
                  <p>{{ problem.inputFormat }}</p>
                </div>
                <div class="spec">
                  <h4>输出格式</h4>
                  <p>{{ problem.outputFormat }}</p>
                </div>
                <div v-if="problem.constraints" class="spec">
                  <h4>数据范围</h4>
                  <p>{{ problem.constraints }}</p>
                </div>
              </div>

              <div v-for="(s, i) in problem.samples" :key="i" class="sample">
                <div class="sample-head">样例 {{ i + 1 }}</div>
                <div class="sample-grid">
                  <div>
                    <span class="sample-label">输入</span>
                    <pre class="sample-pre">{{ s.input }}</pre>
                  </div>
                  <div>
                    <span class="sample-label">输出</span>
                    <pre class="sample-pre">{{ s.output }}</pre>
                  </div>
                </div>
                <p v-if="s.explain" class="sample-explain">{{ s.explain }}</p>
              </div>

              <div v-if="problem.knowledgeRefs?.length" class="krefs">
                <span class="krefs-label">涉及知识点</span>
                <RouterLink
                  v-for="k in problem.knowledgeRefs"
                  :key="k.id"
                  :to="`/module/${moduleId}/knowledge/${k.id}`"
                  class="chip chip-accent"
                >
                  {{ k.title }}
                </RouterLink>
              </div>
            </template>

            <template v-else-if="tab === 'hints'">
              <p class="hint-intro">
                提示是**免费**的，按"想不出来才看下一条"的节奏用。每条提示都比上一条更具体一点。
              </p>
              <div class="hint-list">
                <div v-for="(h, i) in visibleHints" :key="i" class="hint">
                  <span class="hint-idx">提示 {{ i + 1 }}</span>
                  <p>{{ h }}</p>
                </div>
              </div>
              <button v-if="hasMoreHints" class="btn btn-sm" @click="hintShown += 1">
                再看一条提示
              </button>
              <p v-else class="hint-done">提示都看完了，还是卡住的话可以问 AI 助教（会消耗额度）。</p>
            </template>

            <template v-else>
              <div v-if="!revealSolution" class="solution-gate">
                <Icon name="bulb" :size="22" />
                <h3>确定要看参考解吗？</h3>
                <p>
                  先自己写一遍再看，效果差三倍。也可以先去「提示」翻免费的思路，
                  或者让 AI 只给方向而不是完整代码。
                </p>
                <button class="btn btn-primary" @click="revealSolution = true">
                  我想好了，看参考解
                </button>
              </div>
              <template v-else>
                <CodeViewer
                  v-if="problem.solution"
                  :code="problem.solution"
                  lang="cpp"
                  filename="reference.cpp"
                />
                <p v-else class="muted">这道题还没有整理参考解。</p>
                <p class="solution-tip">
                  看完之后回到编辑器，把关键部分凭记忆写一遍——这才是它真正变成你的东西的时候。
                </p>
              </template>
            </template>
          </div>
        </section>

        <!-- 右：编辑器 + 结果 -->
        <section class="workspace">
          <div class="ws-bar">
            <span class="ws-tip">C++ · Ctrl + Enter 提交</span>
            <div class="grow"></div>
            <button class="btn btn-sm btn-ghost" @click="resetCode">
              <Icon name="refresh" :size="14" /> 恢复模板
            </button>
            <button class="btn btn-sm btn-primary" :disabled="submitting" @click="submit">
              <Icon name="play" :size="14" />
              {{ submitting ? '判题中…' : '提交判题' }}
            </button>
          </div>

          <CodeEditor
            v-model="code"
            language="cpp"
            :height="400"
            @submit="submit"
          />

          <VerdictPanel :result="result" :running="submitting" />
        </section>
      </div>
    </template>

    <AiCoach
      v-if="problem"
      v-model:open="coachOpen"
      :problem="problem"
      :code="code"
      :result="result"
    />
  </div>
</template>

<style scoped>
.problem-page {
  max-width: 1340px;
}
.loading {
  color: var(--muted);
}
.err {
  color: var(--danger);
}
.back {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  font-size: 13px;
  color: var(--muted);
}
.back:hover {
  color: var(--accent);
  text-decoration: none;
}
.p-head {
  margin-bottom: 16px;
}
.p-title-row {
  display: flex;
  align-items: center;
  gap: 10px;
  flex-wrap: wrap;
  margin-top: 8px;
}
.p-title-row h1 {
  font-size: 22px;
  letter-spacing: -0.01em;
}
.stars {
  color: #f0b45a;
  font-size: 13px;
  letter-spacing: 1px;
}
.p-actions {
  margin-top: 12px;
}
.p-grid {
  display: grid;
  grid-template-columns: minmax(0, 430px) minmax(0, 1fr);
  gap: 18px;
  align-items: start;
}
.statement {
  position: sticky;
  top: 78px;
  max-height: calc(100vh - 100px);
  display: flex;
  flex-direction: column;
  overflow: hidden;
}
.stmt-tabs {
  display: flex;
  gap: 4px;
  padding: 10px 12px;
  border-bottom: 1px solid var(--line);
  background: var(--surface-2);
}
.stmt-tab {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  border: none;
  background: transparent;
  padding: 7px 14px;
  border-radius: 8px;
  font-size: 13px;
  font-weight: 600;
  color: var(--muted);
}
.stmt-tab:hover {
  background: var(--bg-soft);
}
.stmt-tab.on {
  background: var(--surface);
  color: var(--accent);
  box-shadow: var(--shadow-sm);
}
.badge {
  font-size: 10px;
  background: var(--bg-soft);
  color: var(--muted);
  border-radius: 999px;
  padding: 0 6px;
}
.stmt-tab.on .badge {
  background: var(--accent-soft);
  color: var(--accent);
}
.stmt-body {
  padding: 20px 22px 26px;
  overflow-y: auto;
}
.io-spec {
  display: flex;
  flex-direction: column;
  gap: 12px;
  margin-top: 20px;
}
.spec h4 {
  font-size: 12.5px;
  color: var(--ink);
  margin-bottom: 3px;
}
.spec p {
  margin: 0;
  font-size: 13px;
  color: var(--ink-2);
  white-space: pre-wrap;
}
.sample {
  margin-top: 18px;
  border: 1px solid var(--line);
  border-radius: 10px;
  overflow: hidden;
}
.sample-head {
  padding: 7px 12px;
  background: var(--surface-2);
  border-bottom: 1px solid var(--line);
  font-size: 11.5px;
  font-weight: 700;
  color: var(--muted);
  letter-spacing: 0.06em;
}
.sample-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
}
.sample-grid > div {
  padding: 10px 12px;
}
.sample-grid > div + div {
  border-left: 1px solid var(--line);
}
.sample-label {
  font-size: 10.5px;
  color: var(--muted);
  letter-spacing: 0.06em;
}
.sample-pre {
  margin: 4px 0 0;
  font-family: var(--font-mono);
  font-size: 12.5px;
  white-space: pre-wrap;
  word-break: break-all;
  color: var(--ink);
}
.sample-explain {
  margin: 0;
  padding: 9px 12px;
  border-top: 1px solid var(--line);
  background: #fbfaff;
  font-size: 12.5px;
  color: var(--ink-2);
}
.krefs {
  display: flex;
  align-items: center;
  gap: 8px;
  flex-wrap: wrap;
  margin-top: 22px;
  padding-top: 16px;
  border-top: 1px dashed var(--line-strong);
}
.krefs-label {
  font-size: 11.5px;
  color: var(--muted);
}
.hint-intro {
  font-size: 13px;
  color: var(--muted);
  margin-top: 0;
}
.hint-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
  margin: 14px 0;
}
.hint {
  border-left: 3px solid var(--accent);
  background: var(--surface-2);
  border-radius: 0 8px 8px 0;
  padding: 10px 14px;
}
.hint-idx {
  font-size: 11px;
  font-weight: 700;
  color: var(--accent);
}
.hint p {
  margin: 4px 0 0;
  font-size: 13.5px;
  color: var(--ink-2);
}
.hint-done {
  font-size: 12.5px;
  color: var(--muted);
}
.solution-gate {
  text-align: center;
  padding: 40px 20px;
  color: var(--muted);
}
.solution-gate h3 {
  margin: 12px 0 8px;
  color: var(--ink);
}
.solution-gate p {
  margin: 0 auto 18px;
  font-size: 13px;
  max-width: 42ch;
  line-height: 1.8;
}
.solution-tip {
  margin-top: 14px;
  font-size: 12.5px;
  color: var(--muted);
}
.muted {
  color: var(--muted);
  font-size: 13px;
}
.workspace {
  display: flex;
  flex-direction: column;
  gap: 12px;
  min-width: 0;
}
.ws-bar {
  display: flex;
  align-items: center;
  gap: 12px;
}
.lang-switch {
  display: inline-flex;
  background: var(--bg-soft);
  border-radius: 9px;
  padding: 3px;
}
.lang-switch button {
  border: none;
  background: transparent;
  padding: 4px 12px;
  border-radius: 7px;
  font-size: 12px;
  font-weight: 600;
  color: var(--muted);
}
.lang-switch button.on {
  background: var(--surface);
  color: var(--ink);
  box-shadow: var(--shadow-sm);
}
.ws-tip {
  font-size: 11.5px;
  color: var(--muted);
}
@media (max-width: 1000px) {
  .p-grid {
    grid-template-columns: 1fr;
  }
  .statement {
    position: static;
    max-height: none;
  }
  .stmt-body {
    max-height: 60vh;
  }
}
</style>
