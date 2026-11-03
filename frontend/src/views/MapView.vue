<script setup>
import { computed } from 'vue'
import { RouterLink } from 'vue-router'
import Icon from '../components/Icon.vue'
import ProgressRing from '../components/ProgressRing.vue'
import { state } from '../store'

const openModules = computed(() => state.modules.filter((m) => m.status === 'open'))

const overall = computed(() => {
  const units = state.modules.reduce(
    (sum, m) => sum + m.knowledgeTotal + m.problemTotal,
    0
  )
  const done = state.modules.reduce((sum, m) => sum + m.knowledgeDone + m.problemDone, 0)
  return units ? Math.round((done / units) * 100) : 0
})

const totalKnowledge = computed(() =>
  state.modules.reduce((sum, m) => sum + m.knowledgeTotal, 0)
)
const doneKnowledge = computed(() => state.modules.reduce((sum, m) => sum + m.knowledgeDone, 0))
const doneProblems = computed(() => state.modules.reduce((sum, m) => sum + m.problemDone, 0))

const continueTarget = computed(() => {
  const unfinished = openModules.value.find((m) => m.percent < 100)
  return unfinished || openModules.value[0] || null
})
</script>

<template>
  <div class="page">
    <section class="hero card">
      <div class="hero-main">
        <span class="eyebrow">数据结构 · 期末冲刺</span>
        <h1>从线性表开始，<br />一关一关把代码写通。</h1>
        <p class="lede">
          每关都有知识点、能直接抄的代码模板、可视化演示，以及会告诉你"错在哪一行"的判题。
          AI 助教只在你点它的时候出现，不烧钱。
        </p>
        <div class="hero-actions">
          <RouterLink
            v-if="continueTarget"
            :to="`/module/${continueTarget.id}`"
            class="btn btn-primary btn-lg"
          >
            <Icon name="play" :size="16" />
            {{ continueTarget.percent > 0 ? '继续' : '开始' }} · {{ continueTarget.title }}
          </RouterLink>
          <RouterLink to="/wrongbook" class="btn btn-lg">
            <Icon name="target" :size="16" />
            错题本
            <span v-if="state.wrongCount" class="chip chip-danger">{{ state.wrongCount }}</span>
          </RouterLink>
        </div>
      </div>

      <div class="hero-side">
        <ProgressRing :percent="overall" :size="112" :stroke="9" />
        <div class="hero-stats">
          <div class="stat">
            <strong>{{ doneKnowledge }}<span>/{{ totalKnowledge }}</span></strong>
            <em>知识点</em>
          </div>
          <div class="stat">
            <strong>{{ doneProblems }}<span>/{{ state.totalProblems }}</span></strong>
            <em>已通过题目</em>
          </div>
          <div class="stat">
            <strong>{{ state.level }}</strong>
            <em>当前等级</em>
          </div>
        </div>
      </div>
    </section>

    <div class="map-head">
      <h2>关卡地图</h2>
      <p>前两关已开放，后面的章节等前面打通了再补内容。</p>
    </div>

    <div class="levels">
      <component
        :is="m.status === 'open' ? RouterLink : 'div'"
        v-for="m in state.modules"
        :key="m.id"
        :to="m.status === 'open' ? `/module/${m.id}` : undefined"
        class="level"
        :class="{ locked: m.status !== 'open', cleared: m.cleared }"
      >
        <div class="level-top">
          <span class="level-num">{{ String(m.order).padStart(2, '0') }}</span>
          <span class="level-icon" :style="{ color: m.color, background: m.color + '14' }">
            <Icon :name="m.icon" :size="20" />
          </span>
          <span class="level-state">
            <template v-if="m.status !== 'open'">
              <span class="chip chip-lock"><Icon name="lock" :size="12" />未解锁</span>
            </template>
            <template v-else-if="m.cleared">
              <span class="chip chip-success"><Icon name="check" :size="12" />已通关</span>
            </template>
            <template v-else-if="m.percent > 0">
              <span class="chip chip-accent">进行中</span>
            </template>
            <template v-else>
              <span class="chip">未开始</span>
            </template>
          </span>
        </div>

        <h3>{{ m.title }}</h3>
        <p class="level-sub">{{ m.subtitle }}</p>

        <template v-if="m.status === 'open'">
          <div class="level-meta">
            <span><Icon name="book" :size="13" /> 知识点 {{ m.knowledgeDone }}/{{ m.knowledgeTotal }}</span>
            <span><Icon name="code" :size="13" /> 题目 {{ m.problemDone }}/{{ m.problemTotal }}</span>
            <span><Icon name="clock" :size="13" /> {{ m.estimatedMinutes }} 分钟</span>
          </div>
          <div class="bar level-bar"><i :style="{ width: m.percent + '%' }"></i></div>
          <div class="level-foot">
            <span>{{ m.percent }}%</span>
            <span class="enter">进入本关 <Icon name="arrow-right" :size="14" /></span>
          </div>
        </template>
        <p v-else class="level-locked-note">{{ m.description }}</p>
      </component>
    </div>

    <section class="tips card">
      <div class="tips-head">
        <Icon name="bulb" :size="18" />
        <h3>怎么用这个工具最有效</h3>
      </div>
      <ol class="tips-list">
        <li><strong>先读知识点，别急着写代码。</strong>每节末尾的"考点"和"易错点"是期末选择题的原题来源。</li>
        <li><strong>看代码时点右边的解释。</strong>会高亮对应行，比从头读快得多。看懂之后自己默写一遍。</li>
        <li><strong>做题先自己卡 15 分钟。</strong>卡住了先用免费的分层提示和本地错因检查，实在不行再点 AI。</li>
        <li><strong>判题失败时看具体的测试点。</strong>会给出错在哪组输入、期望什么、你输出了什么——这是比 OJ 好用的地方。</li>
      </ol>
    </section>
  </div>
</template>

<style scoped>
.hero {
  display: grid;
  grid-template-columns: minmax(0, 1.55fr) minmax(280px, 0.9fr);
  gap: 24px;
  padding: 38px 38px 34px;
  background: linear-gradient(135deg, #ffffff 0%, #fbfaff 45%, #f4f2ff 100%);
  border-color: #e6e3f7;
  box-shadow: var(--shadow-lg);
  overflow: hidden;
  position: relative;
}
.hero::after {
  content: '';
  position: absolute;
  right: -120px;
  top: -140px;
  width: 340px;
  height: 340px;
  border-radius: 50%;
  background: radial-gradient(circle, rgba(139, 92, 246, 0.16), transparent 65%);
}
.eyebrow {
  display: inline-block;
  font-size: 12px;
  font-weight: 700;
  letter-spacing: 0.14em;
  color: var(--accent);
  background: var(--accent-soft);
  padding: 4px 12px;
  border-radius: 999px;
  margin-bottom: 16px;
}
.hero h1 {
  font-size: clamp(24px, 3vw, 34px);
  letter-spacing: -0.02em;
  line-height: 1.28;
}
.lede {
  margin: 14px 0 0;
  color: var(--ink-2);
  font-size: 14.5px;
  max-width: 52ch;
}
.hero-actions {
  display: flex;
  gap: 10px;
  margin-top: 26px;
  flex-wrap: wrap;
}
.hero-actions .chip {
  margin-left: 2px;
}
.hero-side {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 20px;
  position: relative;
  z-index: 1;
}
.hero-stats {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 14px;
  width: 100%;
  text-align: center;
}
.stat strong {
  display: block;
  font-size: 19px;
  color: var(--ink);
  font-variant-numeric: tabular-nums;
}
.stat strong span {
  font-size: 12px;
  color: var(--muted);
  font-weight: 500;
}
.stat em {
  font-style: normal;
  font-size: 11.5px;
  color: var(--muted);
}
.map-head {
  margin: 40px 0 18px;
  display: flex;
  align-items: baseline;
  gap: 12px;
  flex-wrap: wrap;
}
.map-head h2 {
  font-size: 19px;
}
.map-head p {
  margin: 0;
  color: var(--muted);
  font-size: 13px;
}
.levels {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
  gap: 16px;
}
.level {
  display: block;
  padding: 20px 20px 16px;
  background: var(--surface);
  border: 1px solid var(--line);
  border-radius: var(--radius);
  color: inherit;
  text-decoration: none;
  transition: transform 0.18s ease, box-shadow 0.2s ease, border-color 0.2s ease;
  position: relative;
}
.level:hover {
  text-decoration: none;
  transform: translateY(-3px);
  box-shadow: var(--shadow);
  border-color: #d9d6f0;
}
.level.cleared {
  background: linear-gradient(180deg, #ffffff, #f7fdfa);
  border-color: #cdeade;
}
.level.locked {
  background: var(--surface-2);
  border-style: dashed;
  opacity: 0.72;
  cursor: default;
}
.level.locked:hover {
  transform: none;
  box-shadow: none;
}
.level-top {
  display: flex;
  align-items: center;
  gap: 12px;
}
.level-num {
  font-family: var(--font-mono);
  font-size: 12px;
  font-weight: 700;
  color: #b9b6d6;
  letter-spacing: 0.06em;
}
.level-icon {
  width: 38px;
  height: 38px;
  border-radius: 11px;
  display: grid;
  place-items: center;
}
.level-state {
  margin-left: auto;
}
.level h3 {
  margin: 14px 0 2px;
  font-size: 17px;
}
.level-sub {
  margin: 0;
  color: var(--muted);
  font-size: 12.5px;
}
.level-meta {
  display: flex;
  gap: 14px;
  flex-wrap: wrap;
  margin: 18px 0 10px;
  font-size: 12px;
  color: var(--ink-2);
}
.level-meta span {
  display: inline-flex;
  align-items: center;
  gap: 5px;
}
.level-bar {
  height: 6px;
}
.level-foot {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 10px;
  font-size: 12px;
  color: var(--muted);
}
.level-foot .enter {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  color: var(--accent);
  font-weight: 600;
}
.level-locked-note {
  margin: 14px 0 0;
  font-size: 12.5px;
  color: var(--muted);
  line-height: 1.7;
}
.tips {
  margin-top: 32px;
  padding: 24px 26px;
  background: linear-gradient(180deg, #ffffff, #fbfbff);
}
.tips-head {
  display: flex;
  align-items: center;
  gap: 9px;
  color: var(--accent);
}
.tips-head h3 {
  font-size: 15px;
  color: var(--ink);
}
.tips-list {
  margin: 14px 0 0;
  padding-left: 20px;
  color: var(--ink-2);
  font-size: 14px;
}
.tips-list li {
  margin: 8px 0;
}
@media (max-width: 860px) {
  .hero {
    grid-template-columns: 1fr;
    padding: 26px 22px;
  }
  .hero-side {
    flex-direction: row;
    justify-content: space-between;
  }
  .hero-stats {
    width: auto;
    flex: 1;
  }
}
@media (max-width: 560px) {
  .hero-stats {
    grid-template-columns: repeat(3, auto);
  }
  .levels {
    grid-template-columns: 1fr;
  }
}
</style>
