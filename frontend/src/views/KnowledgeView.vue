<script setup>
import { computed, onMounted, ref, watch } from 'vue'
import { RouterLink, useRoute, useRouter } from 'vue-router'
import Icon from '../components/Icon.vue'
import MarkdownView from '../components/MarkdownView.vue'
import VisualizerPanel from '../components/VisualizerPanel.vue'
import { api } from '../api'
import { state, isKnowledgeRead, markKnowledgeRead } from '../store'

const route = useRoute()
const router = useRouter()
const moduleData = ref(null)
const loading = ref(true)
const error = ref('')

const moduleId = computed(() => route.params.moduleId)
const knowledgeId = computed(() => route.params.knowledgeId)

const article = computed(
  () => moduleData.value?.knowledge.find((k) => k.id === knowledgeId.value) || null
)
const index = computed(() =>
  moduleData.value?.knowledge.findIndex((k) => k.id === knowledgeId.value)
)
const prev = computed(() => (index.value > 0 ? moduleData.value.knowledge[index.value - 1] : null))
const next = computed(() => {
  const list = moduleData.value?.knowledge || []
  return index.value >= 0 && index.value < list.length - 1 ? list[index.value + 1] : null
})

const VIZ_BY_KNOWLEDGE = {
  'linear-list': {
    seqlist: ['seqlist']
  },
  'stack-queue': {
    'stack-concept': ['stack'],
    'seq-stack': ['stack'],
    'link-stack': ['stack'],
    'stack-apps': ['stack'],
    'queue-concept': ['queue'],
    'circular-queue': ['queue'],
    'link-queue': ['queue'],
    'queue-apps': ['queue']
  }
}

const vizKeys = computed(() => VIZ_BY_KNOWLEDGE[moduleId.value]?.[knowledgeId.value] || [])
const relatedProblems = computed(() =>
  (moduleData.value?.problemRefs || []).filter((p) =>
    (p.knowledgeIds || []).includes(knowledgeId.value)
  )
)

async function load() {
  loading.value = true
  error.value = ''
  try {
    moduleData.value = await api.module(moduleId.value)
  } catch (err) {
    error.value = err.message
  } finally {
    loading.value = false
  }
  window.scrollTo({ top: 0 })
}

watch(() => route.fullPath, load)
onMounted(load)

const read = computed(() => isKnowledgeRead(moduleId.value, knowledgeId.value))

async function finish() {
  if (!article.value) return
  await markKnowledgeRead(moduleId.value, article.value.id)
}
</script>

<template>
  <div class="page know-page">
    <div class="crumbs">
      <RouterLink to="/" class="crumb-link">学习地图</RouterLink>
      <span>/</span>
      <RouterLink :to="`/module/${moduleId}`" class="crumb-link">
        {{ moduleData?.title || '章节' }}
      </RouterLink>
      <span>/</span>
      <span class="crumb-now">{{ article?.title || '知识点' }}</span>
    </div>

    <div v-if="loading" class="card card-pad loading">加载中…</div>
    <div v-else-if="error" class="card card-pad err">{{ error }}</div>

    <div v-else-if="moduleData && article" class="know-layout">
      <aside class="toc card">
        <div class="toc-title">本关知识点</div>
        <RouterLink
          v-for="(k, i) in moduleData.knowledge"
          :key="k.id"
          :to="`/module/${moduleId}/knowledge/${k.id}`"
          class="toc-item"
          :class="{ on: k.id === knowledgeId, done: isKnowledgeRead(moduleId, k.id) }"
        >
          <span class="toc-num">{{ i + 1 }}</span>
          <span class="grow">{{ k.title }}</span>
          <Icon v-if="isKnowledgeRead(moduleId, k.id)" name="check" :size="13" />
        </RouterLink>
      </aside>

      <article class="article card">
        <header class="article-head">
          <div class="row wrap" style="gap: 8px">
            <span class="chip chip-accent">{{ moduleData.title }}</span>
            <span class="chip"><Icon name="clock" :size="12" />{{ article.minutes }} 分钟</span>
            <span v-if="read" class="chip chip-success"><Icon name="check" :size="12" />已读</span>
          </div>
          <h1>{{ article.title }}</h1>
          <p class="summary">{{ article.summary }}</p>
          <div v-if="article.exam?.length" class="exam-line">
            <Icon name="target" :size="15" />
            <span>对应考点：{{ article.exam.join(' · ') }}</span>
          </div>
        </header>

        <MarkdownView :source="article.body" class="article-body" />

        <div v-if="vizKeys.length" class="inline-viz">
          <div class="inline-viz-title">
            <Icon name="play" :size="16" />
            <span>动手看一眼</span>
          </div>
          <VisualizerPanel :keys="vizKeys" compact />
        </div>

        <footer class="article-foot">
          <button class="btn btn-primary" :disabled="read" @click="finish">
            <Icon :name="read ? 'check' : 'book'" :size="16" />
            {{ read ? '本节已完成' : '标记本节为已读（+10 XP）' }}
          </button>
          <div class="pager">
            <RouterLink
              v-if="prev"
              :to="`/module/${moduleId}/knowledge/${prev.id}`"
              class="pager-btn"
            >
              <Icon name="arrow-left" :size="15" />
              <span>{{ prev.title }}</span>
            </RouterLink>
            <RouterLink
              v-if="next"
              :to="`/module/${moduleId}/knowledge/${next.id}`"
              class="pager-btn next"
            >
              <span>{{ next.title }}</span>
              <Icon name="arrow-right" :size="15" />
            </RouterLink>
          </div>
        </footer>
      </article>

      <aside class="side">
        <section v-if="relatedProblems.length" class="card side-card">
          <h3><Icon name="target" :size="15" /> 学完就练</h3>
          <RouterLink
            v-for="p in relatedProblems"
            :key="p.id"
            :to="`/module/${moduleId}/problem/${p.id}`"
            class="side-prob"
          >
            <span class="grow">{{ p.title }}</span>
            <span class="stars">{{ '★'.repeat(p.difficulty) }}</span>
            <Icon name="arrow-right" :size="13" />
          </RouterLink>
        </section>

        <section class="card side-card">
          <h3><Icon name="code" :size="15" /> 相关代码</h3>
          <RouterLink :to="`/module/${moduleId}?tab=code`" class="side-link">
            去代码库看完整实现
            <Icon name="arrow-right" :size="13" />
          </RouterLink>
        </section>
      </aside>
    </div>
  </div>
</template>

<style scoped>
.know-page {
  max-width: 1240px;
}
.crumbs {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 12.5px;
  color: var(--muted);
  margin-bottom: 16px;
}
.crumb-link {
  color: var(--muted);
}
.crumb-link:hover {
  color: var(--accent);
  text-decoration: none;
}
.crumb-now {
  color: var(--ink-2);
}
.loading,
.err {
  color: var(--muted);
}
.err {
  color: var(--danger);
}
.know-layout {
  display: grid;
  grid-template-columns: 236px minmax(0, 1fr) 232px;
  gap: 20px;
  align-items: start;
}
.toc {
  position: sticky;
  top: 82px;
  padding: 14px 10px;
}
.toc-title {
  font-size: 11px;
  letter-spacing: 0.1em;
  text-transform: uppercase;
  color: var(--muted);
  padding: 0 8px 8px;
}
.toc-item {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px;
  border-radius: 8px;
  color: var(--ink-2);
  font-size: 13px;
  line-height: 1.45;
}
.toc-item:hover {
  background: var(--bg-soft);
  text-decoration: none;
}
.toc-item.on {
  background: var(--accent-soft);
  color: var(--accent);
  font-weight: 600;
}
.toc-item.done {
  color: var(--muted);
}
.toc-num {
  flex: none;
  width: 16px;
  font-size: 11px;
  color: #b9b6d6;
  font-family: var(--font-mono);
}
.article {
  padding: 30px 34px 24px;
}
.article-head h1 {
  font-size: 27px;
  margin: 14px 0 8px;
  letter-spacing: -0.015em;
}
.summary {
  margin: 0;
  color: var(--muted);
  font-size: 14px;
}
.exam-line {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-top: 14px;
  padding: 8px 12px;
  border-radius: 8px;
  background: #f7f3ff;
  color: #6d28d9;
  font-size: 12.5px;
}
.article-body {
  margin-top: 22px;
}
.inline-viz {
  margin-top: 30px;
  border-top: 1px dashed var(--line-strong);
  padding-top: 20px;
}
.inline-viz-title {
  display: flex;
  align-items: center;
  gap: 8px;
  font-weight: 650;
  font-size: 14px;
  margin-bottom: 12px;
  color: var(--ink);
}
.article-foot {
  margin-top: 30px;
  padding-top: 20px;
  border-top: 1px solid var(--line);
  display: flex;
  flex-direction: column;
  gap: 14px;
}
.pager {
  display: flex;
  justify-content: space-between;
  gap: 12px;
}
.pager-btn {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 9px 14px;
  border-radius: 10px;
  border: 1px solid var(--line);
  color: var(--ink-2);
  font-size: 13px;
  max-width: 47%;
}
.pager-btn span {
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
.pager-btn:hover {
  border-color: var(--accent);
  color: var(--accent);
  text-decoration: none;
}
.pager-btn.next {
  margin-left: auto;
}
.side {
  position: sticky;
  top: 82px;
  display: flex;
  flex-direction: column;
  gap: 14px;
}
.side-card {
  padding: 16px;
}
.side-card h3 {
  display: flex;
  align-items: center;
  gap: 7px;
  font-size: 13px;
  color: var(--ink);
  margin-bottom: 10px;
}
.side-prob {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 6px;
  border-radius: 8px;
  color: var(--ink-2);
  font-size: 12.5px;
}
.side-prob:hover {
  background: var(--bg-soft);
  text-decoration: none;
  color: var(--accent);
}
.stars {
  color: #f0b45a;
  font-size: 10px;
}
.side-link {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  font-size: 12.5px;
}
@media (max-width: 1180px) {
  .know-layout {
    grid-template-columns: 220px minmax(0, 1fr);
  }
  .side {
    display: none;
  }
}
@media (max-width: 860px) {
  .know-layout {
    grid-template-columns: 1fr;
  }
  .toc {
    position: static;
    display: flex;
    gap: 6px;
    overflow-x: auto;
    padding: 10px;
  }
  .toc-title {
    display: none;
  }
  .toc-item {
    flex: none;
    background: var(--surface-2);
    border: 1px solid var(--line);
  }
  .article {
    padding: 22px 18px;
  }
  .article-head h1 {
    font-size: 22px;
  }
}
</style>
