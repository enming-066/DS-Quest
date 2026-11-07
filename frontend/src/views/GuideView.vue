<script setup>
import { computed, onMounted, ref } from 'vue'
import { RouterLink, useRoute } from 'vue-router'
import Icon from '../components/Icon.vue'
import { api } from '../api'

const route = useRoute()
const tab = ref(route.query.tab === 'terms' ? 'terms' : 'cpp')
const keyword = ref('')
const loading = ref(true)
const error = ref('')
const cpp = ref([])
const terms = ref([])

const MODULE_NAMES = {
  intro: '绪论',
  'linear-list': '线性表',
  'stack-queue': '栈与队列',
  string: '串',
  matrix: '矩阵',
  hash: '散列',
  tree: '树',
  bst: '搜索树',
  graph: '图',
  sort: '排序'
}

onMounted(async () => {
  try {
    const data = await api.guide()
    cpp.value = data.cpp || []
    terms.value = data.terms || []
  } catch (err) {
    error.value = err.message
  } finally {
    loading.value = false
  }
})

const filteredCpp = computed(() => {
  const k = keyword.value.trim().toLowerCase()
  if (!k) return cpp.value
  return cpp.value.filter(
    (item) =>
      item.title.toLowerCase().includes(k) ||
      item.oneLiner.toLowerCase().includes(k) ||
      (item.example || '').toLowerCase().includes(k)
  )
})

const filteredTerms = computed(() => {
  const k = keyword.value.trim().toLowerCase()
  if (!k) return terms.value
  return terms.value.filter(
    (item) =>
      item.concept.toLowerCase().includes(k) ||
      item.difference.toLowerCase().includes(k) ||
      (item.familiar?.name || '').toLowerCase().includes(k) ||
      (item.ppt?.name || '').toLowerCase().includes(k)
  )
})

const warnCount = computed(() => terms.value.filter((t) => t.severity === 'warn').length)
</script>

<template>
  <div class="page guide-page">
    <header class="head card">
      <div class="grow">
        <span class="eyebrow">写给「懂原理、但看不懂老师代码」的人</span>
        <h1>语法急救</h1>
        <p>
          这里不讲数据结构，只解决一件事：<strong>老师 PPT 里的 C++ 代码到底在说什么</strong>。
          左边是你熟悉的（网课 / C 课本），右边是老师课件里的写法，差异都标出来了。
        </p>
      </div>
      <div class="head-stats">
        <div class="hs"><strong>{{ cpp.length }}</strong><em>个语法点</em></div>
        <div class="hs"><strong>{{ terms.length }}</strong><em>组术语对照</em></div>
        <div class="hs warn"><strong>{{ warnCount }}</strong><em>处容易踩坑</em></div>
      </div>
    </header>

    <div class="toolbar">
      <div class="tabs">
        <button class="tab" :class="{ on: tab === 'cpp' }" @click="tab = 'cpp'">
          <Icon name="code" :size="15" /> C++ 路标
        </button>
        <button class="tab" :class="{ on: tab === 'terms' }" @click="tab = 'terms'">
          <Icon name="book" :size="15" /> 术语罗盘
        </button>
      </div>
      <input v-model="keyword" class="input search" placeholder="搜索：指针、引用、front、插入……" />
    </div>

    <div v-if="loading" class="card card-pad muted">加载中…</div>
    <div v-else-if="error" class="card card-pad err">{{ error }}</div>

    <!-- C++ 路标 -->
    <div v-else-if="tab === 'cpp'" class="grid">
      <article v-for="(item, index) in filteredCpp" :key="item.id" class="card cpp-card">
        <div class="cpp-head">
          <span class="num">{{ String(index + 1).padStart(2, '0') }}</span>
          <h3>{{ item.title }}</h3>
        </div>
        <p class="one-liner">{{ item.oneLiner }}</p>
        <p class="why"><strong>为什么数据结构里要用它：</strong>{{ item.why }}</p>

        <pre class="code">{{ item.example }}</pre>

        <div v-if="item.cEquiv" class="c-equiv">
          <span class="c-tag">C 里怎么写</span>
          <p>{{ item.cEquiv }}</p>
        </div>

        <ul v-if="item.pitfalls?.length" class="pitfalls">
          <li v-for="p in item.pitfalls" :key="p">{{ p }}</li>
        </ul>

        <div v-if="item.related?.length" class="related">
          <span>用得到它的模板：</span>
          <code v-for="r in item.related" :key="r">{{ r }}</code>
        </div>
      </article>
    </div>

    <!-- 术语罗盘 -->
    <div v-else class="terms">
      <article
        v-for="item in filteredTerms"
        :key="item.id"
        class="card term"
        :class="{ warn: item.severity === 'warn' }"
      >
        <div class="term-head">
          <h3>{{ item.concept }}</h3>
          <span class="chip" :class="item.severity === 'warn' ? 'chip-danger' : ''">
            {{ item.severity === 'warn' ? '易错' : '说明' }}
          </span>
          <RouterLink
            v-if="item.moduleId && MODULE_NAMES[item.moduleId]"
            :to="`/module/${item.moduleId}`"
            class="chip chip-accent"
          >
            {{ MODULE_NAMES[item.moduleId] }}
          </RouterLink>
        </div>

        <div class="compare">
          <div class="side">
            <div class="side-title familiar">你熟悉的（网课 / C）</div>
            <div class="side-name">{{ item.familiar?.name }}</div>
            <pre v-if="item.familiar?.code" class="code small">{{ item.familiar.code }}</pre>
          </div>
          <div class="arrow">→</div>
          <div class="side">
            <div class="side-title ppt">老师 PPT（C++）</div>
            <div class="side-name">{{ item.ppt?.name }}</div>
            <pre v-if="item.ppt?.code" class="code small">{{ item.ppt.code }}</pre>
          </div>
        </div>

        <p class="difference" :class="{ strong: item.severity === 'warn' }">
          <Icon :name="item.severity === 'warn' ? 'warn' : 'bulb'" :size="14" />
          <span>{{ item.difference }}</span>
        </p>
      </article>

      <div v-if="!filteredTerms.length" class="card empty">
        <span class="empty-emoji">🔍</span>
        <p>没找到相关术语，换个关键词试试。</p>
      </div>
    </div>
  </div>
</template>

<style scoped>
.guide-page {
  max-width: 1120px;
}
.head {
  display: flex;
  gap: 26px;
  padding: 30px 32px;
  background: linear-gradient(135deg, #ffffff, #f7f5ff);
}
.eyebrow {
  font-size: 11.5px;
  font-weight: 700;
  letter-spacing: 0.1em;
  color: var(--accent);
  background: var(--accent-soft);
  padding: 3px 11px;
  border-radius: 999px;
}
.head h1 {
  font-size: 27px;
  margin: 12px 0 8px;
}
.head p {
  margin: 0;
  color: var(--ink-2);
  font-size: 14px;
  max-width: 62ch;
  line-height: 1.8;
}
.head-stats {
  display: flex;
  gap: 20px;
  align-items: center;
  flex: none;
}
.hs {
  text-align: center;
}
.hs strong {
  display: block;
  font-size: 22px;
  color: var(--ink);
}
.hs em {
  font-style: normal;
  font-size: 11px;
  color: var(--muted);
}
.hs.warn strong {
  color: var(--danger);
}
.toolbar {
  display: flex;
  align-items: center;
  gap: 14px;
  margin: 22px 0 16px;
  flex-wrap: wrap;
}
.tabs {
  display: flex;
  gap: 6px;
}
.tab {
  display: inline-flex;
  align-items: center;
  gap: 7px;
  padding: 8px 16px;
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
.search {
  max-width: 320px;
  margin-left: auto;
}
.grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(340px, 1fr));
  gap: 14px;
}
.cpp-card {
  padding: 20px;
  display: flex;
  flex-direction: column;
  gap: 10px;
}
.cpp-head {
  display: flex;
  align-items: baseline;
  gap: 10px;
}
.num {
  font-family: var(--font-mono);
  font-size: 12px;
  color: #b9b6d6;
}
.cpp-head h3 {
  font-size: 15.5px;
}
.one-liner {
  margin: 0;
  color: var(--ink);
  font-size: 13.5px;
  font-weight: 500;
}
.why {
  margin: 0;
  font-size: 12.5px;
  color: var(--muted);
  line-height: 1.7;
}
.code {
  margin: 0;
  padding: 12px 14px;
  border-radius: 10px;
  background: #1c1b2b;
  color: #e6e4f7;
  font-family: var(--font-mono);
  font-size: 12px;
  line-height: 1.65;
  overflow-x: auto;
  white-space: pre;
}
.code.small {
  font-size: 11.5px;
}
.c-equiv {
  display: flex;
  gap: 8px;
  align-items: flex-start;
  padding: 9px 12px;
  border-radius: 8px;
  background: var(--surface-2);
  border: 1px dashed var(--line-strong);
}
.c-tag {
  flex: none;
  font-size: 10.5px;
  font-weight: 700;
  color: var(--muted);
  background: var(--bg-soft);
  border-radius: 999px;
  padding: 1px 8px;
}
.c-equiv p {
  margin: 0;
  font-size: 12px;
  color: var(--ink-2);
  line-height: 1.7;
}
.pitfalls {
  margin: 0;
  padding-left: 18px;
  font-size: 12px;
  color: var(--warn);
}
.pitfalls li {
  margin: 3px 0;
}
.related {
  display: flex;
  gap: 6px;
  align-items: center;
  flex-wrap: wrap;
  font-size: 11px;
  color: var(--muted);
}
.related code {
  font-family: var(--font-mono);
  background: var(--bg-soft);
  padding: 1px 6px;
  border-radius: 4px;
  color: var(--ink-2);
}
.terms {
  display: flex;
  flex-direction: column;
  gap: 12px;
}
.term {
  padding: 18px 20px;
}
.term.warn {
  border-left: 3px solid var(--danger);
}
.term-head {
  display: flex;
  align-items: center;
  gap: 10px;
  flex-wrap: wrap;
  margin-bottom: 12px;
}
.term-head h3 {
  font-size: 15px;
}
.compare {
  display: grid;
  grid-template-columns: 1fr 24px 1fr;
  gap: 10px;
  align-items: stretch;
}
.side {
  padding: 12px;
  border-radius: 10px;
  background: var(--surface-2);
  border: 1px solid var(--line);
  min-width: 0;
}
.side-title {
  font-size: 10.5px;
  font-weight: 700;
  letter-spacing: 0.06em;
  margin-bottom: 6px;
}
.side-title.familiar {
  color: var(--muted);
}
.side-title.ppt {
  color: var(--accent);
}
.side-name {
  font-family: var(--font-mono);
  font-size: 12.5px;
  color: var(--ink);
  margin-bottom: 6px;
}
.arrow {
  display: grid;
  place-items: center;
  color: var(--line-strong);
  font-size: 16px;
}
.difference {
  display: flex;
  gap: 8px;
  align-items: flex-start;
  margin: 12px 0 0;
  font-size: 12.5px;
  color: var(--ink-2);
  line-height: 1.75;
}
.difference.strong {
  color: #9a3412;
  background: var(--warn-soft);
  border-radius: 8px;
  padding: 9px 12px;
}
.muted {
  color: var(--muted);
}
.err {
  color: var(--danger);
}
@media (max-width: 860px) {
  .head {
    flex-direction: column;
    padding: 22px;
  }
  .compare {
    grid-template-columns: 1fr;
  }
  .arrow {
    transform: rotate(90deg);
  }
  .grid {
    grid-template-columns: 1fr;
  }
}
</style>
