<script setup>
import { computed, onMounted, ref, watch } from 'vue'
import { RouterLink, useRoute } from 'vue-router'
import Icon from '../components/Icon.vue'
import CodeViewer from '../components/CodeViewer.vue'
import ProgressRing from '../components/ProgressRing.vue'
import VisualizerPanel from '../components/VisualizerPanel.vue'
import { api } from '../api'
import { state, isKnowledgeRead } from '../store'

const route = useRoute()
const moduleData = ref(null)
const loading = ref(true)
const error = ref('')
const tab = ref('knowledge')
const opened = ref('')

const VIZ_KEYS = {
  'linear-list': ['seqlist'],
  'stack-queue': ['stack', 'queue']
}

const solved = computed(() => new Set(state.progress.problemsSolved))
const moduleId = computed(() => route.params.moduleId)

async function load() {
  loading.value = true
  error.value = ''
  if (['knowledge', 'code', 'viz', 'problems'].includes(route.query.tab)) {
    tab.value = route.query.tab
  }
  try {
    moduleData.value = await api.module(moduleId.value)
    if (tab.value === 'knowledge' && !moduleData.value.knowledge.length) tab.value = 'problems'
  } catch (err) {
    error.value = err.message
  } finally {
    loading.value = false
  }
}

watch(moduleId, load)
onMounted(load)

const summary = computed(() => moduleData.value?.summary || {})
const vizKeys = computed(() => VIZ_KEYS[moduleId.value] || [])

function readCount() {
  if (!moduleData.value) return 0
  return moduleData.value.knowledge.filter((k) => isKnowledgeRead(moduleId.value, k.id)).length
}

function difficulty(n) {
  return '★'.repeat(n) + '☆'.repeat(Math.max(0, 5 - n))
}

function toggleTemplate(id) {
  opened.value = opened.value === id ? '' : id
}
</script>

<template>
  <div class="page">
    <RouterLink to="/" class="back">
      <Icon name="arrow-left" :size="15" /> 返回地图
    </RouterLink>

    <div v-if="loading" class="loading card card-pad">加载中…</div>
    <div v-else-if="error" class="card card-pad error-box">
      <strong>加载失败：</strong>{{ error }}
      <button class="btn btn-sm" @click="load">重试</button>
    </div>

    <template v-else-if="moduleData">
      <header class="mod-head card">
        <div class="mod-icon" :style="{ color: moduleData.color, background: moduleData.color + '14' }">
          <Icon :name="moduleData.icon" :size="26" />
        </div>
        <div class="grow">
          <span class="eyebrow">第 {{ moduleData.order }} 关</span>
          <h1>{{ moduleData.title }}</h1>
          <p class="sub">{{ moduleData.subtitle }}</p>
          <p class="goal">{{ moduleData.goal }}</p>
          <div class="mod-meta">
            <span v-if="moduleData.knowledge.length">
              <Icon name="book" :size="14" /> 知识点 {{ moduleData.knowledge.length }}
            </span>
            <span v-if="moduleData.templates.length">
              <Icon name="code" :size="14" /> 代码模板 {{ moduleData.templates.length }}
            </span>
            <span v-if="moduleData.problemRefs.length">
              <Icon name="target" :size="14" /> 练习 {{ moduleData.problemRefs.length }}
            </span>
            <span v-if="moduleData.estimatedMinutes">
              <Icon name="clock" :size="14" /> 约 {{ moduleData.estimatedMinutes }} 分钟
            </span>
          </div>
        </div>
        <div class="mod-progress">
          <ProgressRing :percent="summary.percent || 0" :size="88" :stroke="7" />
          <span class="mod-progress-text">{{ summary.percent || 0 }}% 完成</span>
        </div>
      </header>

      <nav class="tabs">
        <button
          v-if="moduleData.knowledge.length"
          class="tab"
          :class="{ on: tab === 'knowledge' }"
          @click="tab = 'knowledge'"
        >
          <Icon name="book" :size="15" /> 知识点
          <span class="count">{{ readCount() }}/{{ moduleData.knowledge.length }}</span>
        </button>
        <button
          v-if="moduleData.templates.length"
          class="tab"
          :class="{ on: tab === 'code' }"
          @click="tab = 'code'"
        >
          <Icon name="code" :size="15" /> 代码库
          <span class="count">{{ moduleData.templates.length }}</span>
        </button>
        <button v-if="vizKeys.length" class="tab" :class="{ on: tab === 'viz' }" @click="tab = 'viz'">
          <Icon name="play" :size="15" /> 可视化
        </button>
        <button class="tab" :class="{ on: tab === 'problems' }" @click="tab = 'problems'">
          <Icon name="target" :size="15" /> 练习
          <span class="count">{{ summary.problemDone || 0 }}/{{ moduleData.problemRefs.length }}</span>
        </button>
      </nav>

      <!-- 知识点 -->
      <section v-if="tab === 'knowledge'" class="list">
        <RouterLink
          v-for="(k, i) in moduleData.knowledge"
          :key="k.id"
          :to="`/module/${moduleData.id}/knowledge/${k.id}`"
          class="know-item card"
        >
          <span class="know-num">{{ String(i + 1).padStart(2, '0') }}</span>
          <div class="grow">
            <h3>{{ k.title }}</h3>
            <p>{{ k.summary }}</p>
            <div class="know-tags">
              <span class="chip"><Icon name="clock" :size="12" />{{ k.minutes }} 分钟</span>
              <span v-for="tag in k.tags" :key="tag" class="chip">{{ tag }}</span>
            </div>
          </div>
          <span v-if="isKnowledgeRead(moduleData.id, k.id)" class="read-mark">
            <Icon name="check" :size="14" /> 已读
          </span>
          <Icon v-else name="arrow-right" :size="18" class="arrow" />
        </RouterLink>

        <p class="footnote">
          内容是按课本顺序整理的。如果老师上课的 PPT 里有额外例题，把那几页发给我，我可以补成新的知识点。
        </p>
      </section>

      <!-- 代码库 -->
      <section v-else-if="tab === 'code'" class="tpl-list">
        <article v-for="tpl in moduleData.templates" :key="tpl.id" class="tpl card">
          <button class="tpl-head" @click="toggleTemplate(tpl.id)">
            <div class="grow">
              <div class="row wrap" style="gap: 8px">
                <h3>{{ tpl.title }}</h3>
                <span class="chip" :class="tpl.lang === 'c' ? 'chip-warn' : 'chip-accent'">
                  {{ tpl.lang === 'c' ? 'C 语言' : 'C++' }}
                </span>
                <span v-if="tpl.level === 'exam'" class="chip chip-success">考点模板</span>
                <span v-else class="chip">核心模板</span>
              </div>
              <p>{{ tpl.summary }}</p>
            </div>
            <Icon name="chevron" :size="18" class="chev" :class="{ open: opened === tpl.id }" />
          </button>

          <div v-if="opened === tpl.id" class="tpl-body">
            <p class="purpose"><strong>什么时候用：</strong>{{ tpl.purpose }}</p>
            <CodeViewer
              :code="tpl.code"
              :lang="tpl.lang"
              :explanations="tpl.explanations || []"
              :filename="(tpl.file || '').split('/').pop()"
            />
            <div v-if="tpl.pitfalls?.length" class="pitfalls">
              <h4><Icon name="warn" :size="15" /> 常见错误</h4>
              <ul>
                <li v-for="p in tpl.pitfalls" :key="p">{{ p }}</li>
              </ul>
            </div>
          </div>
        </article>
      </section>

      <!-- 可视化 -->
      <section v-else-if="tab === 'viz'">
        <VisualizerPanel :keys="vizKeys" />
      </section>

      <!-- 练习 -->
      <section v-else class="problems">
        <RouterLink
          v-for="p in moduleData.problemRefs"
          :key="p.id"
          :to="`/module/${moduleData.id}/problem/${p.id}`"
          class="prob card"
          :class="{ done: solved.has(p.id) }"
        >
          <span class="prob-state" :class="{ ok: solved.has(p.id) }">
            <Icon :name="solved.has(p.id) ? 'check' : 'code'" :size="16" />
          </span>
          <div class="grow">
            <div class="row wrap" style="gap: 8px">
              <h3>{{ p.title }}</h3>
              <span class="stars">{{ difficulty(p.difficulty) }}</span>
            </div>
            <p>{{ p.summary }}</p>
            <div class="know-tags">
              <span v-for="tag in p.tags" :key="tag" class="chip">{{ tag }}</span>
            </div>
          </div>
          <span v-if="solved.has(p.id)" class="chip chip-success">已通过</span>
          <span v-else class="go">去做 <Icon name="arrow-right" :size="14" /></span>
        </RouterLink>
      </section>
    </template>
  </div>
</template>

<style scoped>
.back {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  font-size: 13px;
  color: var(--muted);
  margin-bottom: 14px;
}
.back:hover {
  color: var(--accent);
  text-decoration: none;
}
.loading,
.error-box {
  color: var(--muted);
}
.error-box {
  color: var(--danger);
  display: flex;
  gap: 10px;
  align-items: center;
}
.mod-head {
  display: flex;
  gap: 20px;
  padding: 26px 28px;
  align-items: flex-start;
  background: linear-gradient(135deg, #ffffff, #fbfaff);
}
.mod-icon {
  width: 56px;
  height: 56px;
  border-radius: 16px;
  display: grid;
  place-items: center;
  flex: none;
}
.eyebrow {
  font-size: 11.5px;
  font-weight: 700;
  letter-spacing: 0.12em;
  color: var(--accent);
}
.mod-head h1 {
  font-size: 26px;
  margin: 4px 0 2px;
  letter-spacing: -0.01em;
}
.sub {
  margin: 0;
  color: var(--muted);
  font-size: 13px;
}
.goal {
  margin: 12px 0 0;
  color: var(--ink-2);
  font-size: 13.5px;
  max-width: 70ch;
}
.mod-meta {
  display: flex;
  gap: 16px;
  flex-wrap: wrap;
  margin-top: 14px;
  font-size: 12px;
  color: var(--muted);
}
.mod-meta span {
  display: inline-flex;
  align-items: center;
  gap: 5px;
}
.mod-progress {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 6px;
  flex: none;
}
.mod-progress-text {
  font-size: 11px;
  color: var(--muted);
}
.tabs {
  display: flex;
  gap: 6px;
  margin: 22px 0 18px;
  flex-wrap: wrap;
}
.tab {
  display: inline-flex;
  align-items: center;
  gap: 7px;
  padding: 9px 16px;
  border-radius: 999px;
  border: 1px solid transparent;
  background: transparent;
  color: var(--ink-2);
  font-size: 13.5px;
  font-weight: 600;
}
.tab:hover {
  background: var(--bg-soft);
}
.tab.on {
  background: var(--surface);
  border-color: var(--line);
  color: var(--accent);
  box-shadow: var(--shadow-sm);
}
.tab .count {
  font-size: 11px;
  color: var(--muted);
  font-variant-numeric: tabular-nums;
}
.tab.on .count {
  color: var(--accent);
}
.list,
.problems,
.tpl-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}
.know-item,
.prob {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 18px 20px;
  color: inherit;
  transition: transform 0.16s ease, box-shadow 0.2s ease, border-color 0.2s ease;
}
.know-item:hover,
.prob:hover {
  text-decoration: none;
  transform: translateY(-2px);
  box-shadow: var(--shadow);
  border-color: #dcd9f2;
}
.know-num {
  font-family: var(--font-mono);
  font-size: 13px;
  font-weight: 700;
  color: #c3c0dd;
  flex: none;
}
.know-item h3,
.prob h3 {
  font-size: 15.5px;
  margin-bottom: 2px;
}
.know-item p,
.prob p {
  margin: 0;
  color: var(--muted);
  font-size: 13px;
}
.know-tags {
  display: flex;
  gap: 6px;
  flex-wrap: wrap;
  margin-top: 9px;
}
.read-mark {
  display: inline-flex;
  align-items: center;
  gap: 5px;
  font-size: 12px;
  font-weight: 600;
  color: var(--success);
  flex: none;
}
.arrow {
  color: #c9c6de;
  flex: none;
}
.prob-state {
  width: 36px;
  height: 36px;
  border-radius: 10px;
  display: grid;
  place-items: center;
  background: var(--bg-soft);
  color: var(--muted);
  flex: none;
}
.prob-state.ok {
  background: var(--success-soft);
  color: var(--success);
}
.stars {
  color: #f0b45a;
  font-size: 12px;
  letter-spacing: 1px;
}
.go {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  font-size: 12.5px;
  color: var(--accent);
  font-weight: 600;
  flex: none;
}
.footnote {
  margin: 10px 2px 0;
  font-size: 12.5px;
  color: var(--muted);
}
.tpl {
  overflow: hidden;
}
.tpl-head {
  width: 100%;
  display: flex;
  align-items: center;
  gap: 14px;
  padding: 18px 20px;
  background: transparent;
  border: none;
  text-align: left;
}
.tpl-head h3 {
  font-size: 15.5px;
}
.tpl-head p {
  margin: 4px 0 0;
  color: var(--muted);
  font-size: 13px;
}
.chev {
  color: #bdbad4;
  transition: transform 0.2s ease;
  flex: none;
}
.chev.open {
  transform: rotate(180deg);
}
.tpl-body {
  padding: 0 20px 20px;
  display: flex;
  flex-direction: column;
  gap: 12px;
}
.purpose {
  margin: 0;
  font-size: 13px;
  color: var(--ink-2);
  background: var(--surface-2);
  border: 1px dashed var(--line);
  border-radius: 10px;
  padding: 10px 14px;
}
.pitfalls h4 {
  display: flex;
  align-items: center;
  gap: 7px;
  font-size: 13px;
  color: var(--warn);
  margin-bottom: 6px;
}
.pitfalls ul {
  margin: 0;
  padding-left: 20px;
  font-size: 13px;
  color: var(--ink-2);
}
.pitfalls li {
  margin: 4px 0;
}
@media (max-width: 720px) {
  .mod-head {
    flex-wrap: wrap;
    padding: 20px;
  }
  .mod-progress {
    display: none;
  }
}
</style>
