<script setup>
import { onMounted } from 'vue'
import { RouterLink, RouterView } from 'vue-router'
import { state, refreshBootstrap, xpPercent } from './store'

onMounted(() => {
  refreshBootstrap().catch(() => {})
})
</script>

<template>
  <div class="shell">
    <header class="topbar">
      <div class="topbar-inner">
        <RouterLink to="/" class="brand">
          <span class="brand-mark">
            <svg viewBox="0 0 24 24" width="18" height="18" aria-hidden="true">
              <path
                d="M12 2.6 21 7v10l-9 4.4L3 17V7l9-4.4Z"
                fill="none"
                stroke="currentColor"
                stroke-width="1.7"
                stroke-linejoin="round"
              />
              <path d="M8 12.2l2.6 2.6L16 9.4" fill="none" stroke="currentColor"
                stroke-width="1.9" stroke-linecap="round" stroke-linejoin="round" />
            </svg>
          </span>
          <span class="brand-text">
            <strong>DS Quest</strong>
            <em>数据结构闯关</em>
          </span>
        </RouterLink>

        <nav class="nav">
          <RouterLink to="/" class="nav-link" active-class="active" exact-active-class="active">
            学习地图
          </RouterLink>
          <RouterLink to="/wrongbook" class="nav-link" active-class="active">
            错题本
            <span v-if="state.wrongCount" class="nav-badge">{{ state.wrongCount }}</span>
          </RouterLink>
        </nav>

        <div class="stats">
          <div class="xp" :title="`${state.progress.xp} / ${state.level * state.xpToNext} XP`">
            <span class="xp-level">Lv.{{ state.level }}</span>
            <span class="xp-bar"><i :style="{ width: xpPercent + '%' }"></i></span>
            <span class="xp-num">{{ state.progress.xp }} XP</span>
          </div>
          <span
            class="chip"
            :class="state.ai.enabled ? 'chip-accent' : 'chip-lock'"
            :title="state.ai.enabled ? 'AI 只在点击按钮时调用' : '没有配置 API Key，AI 助教不可用'"
          >
            <span class="dot"></span>
            AI {{ state.ai.enabled ? `${state.ai.remaining}/${state.ai.limit}` : '未启用' }}
          </span>
        </div>
      </div>
    </header>

    <div v-if="state.error" class="banner">
      <strong>连不上后端。</strong>
      {{ state.error }} —— 确认 <code>backend/run.py</code> 正在运行。
      <button class="btn btn-sm" @click="refreshBootstrap().catch(() => {})">重试</button>
    </div>

    <main>
      <RouterView v-slot="{ Component }">
        <transition name="fade" mode="out-in">
          <component :is="Component" />
        </transition>
      </RouterView>
    </main>

    <div class="toast-wrap">
      <div v-for="t in state.toasts" :key="t.id" class="toast" :class="`toast-${t.type}`">
        {{ t.message }}
      </div>
    </div>
  </div>
</template>

<style scoped>
.topbar {
  position: sticky;
  top: 0;
  z-index: 100;
  background: rgba(255, 255, 255, 0.82);
  backdrop-filter: saturate(180%) blur(14px);
  border-bottom: 1px solid rgba(230, 230, 240, 0.9);
}
.topbar-inner {
  max-width: 1440px;
  margin: 0 auto;
  height: 62px;
  padding: 0 24px;
  display: flex;
  align-items: center;
  gap: 24px;
}
.brand {
  display: flex;
  align-items: center;
  gap: 10px;
  color: var(--ink);
  text-decoration: none;
}
.brand:hover {
  text-decoration: none;
}
.brand-mark {
  width: 32px;
  height: 32px;
  border-radius: 10px;
  display: grid;
  place-items: center;
  color: #fff;
  background: linear-gradient(135deg, var(--accent), var(--accent-2));
  box-shadow: 0 8px 18px -10px rgba(91, 91, 214, 0.9);
}
.brand-text {
  display: flex;
  flex-direction: column;
  line-height: 1.15;
}
.brand-text strong {
  font-size: 15px;
  letter-spacing: 0.01em;
}
.brand-text em {
  font-style: normal;
  font-size: 11px;
  color: var(--muted);
  letter-spacing: 0.08em;
}
.nav {
  display: flex;
  gap: 4px;
  margin-left: 6px;
}
.nav-link {
  position: relative;
  padding: 8px 14px;
  border-radius: 999px;
  color: var(--ink-2);
  font-size: 14px;
  font-weight: 600;
}
.nav-link:hover {
  background: var(--bg-soft);
  text-decoration: none;
}
.nav-link.active {
  background: var(--accent-soft);
  color: var(--accent);
}
.nav-badge {
  display: inline-block;
  min-width: 18px;
  height: 18px;
  margin-left: 6px;
  padding: 0 5px;
  border-radius: 9px;
  background: var(--danger);
  color: #fff;
  font-size: 11px;
  line-height: 18px;
  text-align: center;
}
.stats {
  margin-left: auto;
  display: flex;
  align-items: center;
  gap: 14px;
}
.xp {
  display: flex;
  align-items: center;
  gap: 8px;
}
.xp-level {
  font-size: 12px;
  font-weight: 700;
  color: var(--accent);
}
.xp-bar {
  display: block;
  width: 78px;
  height: 6px;
  border-radius: 999px;
  background: var(--bg-soft);
  overflow: hidden;
}
.xp-bar i {
  display: block;
  height: 100%;
  background: linear-gradient(90deg, var(--accent), var(--accent-2));
  transition: width 0.5s ease;
}
.xp-num {
  font-size: 12px;
  color: var(--muted);
  font-variant-numeric: tabular-nums;
}
.banner {
  max-width: 1180px;
  margin: 16px auto 0;
  padding: 12px 18px;
  border-radius: 12px;
  background: var(--danger-soft);
  border: 1px solid #f3c6c6;
  color: #8f1d1d;
  font-size: 13.5px;
  display: flex;
  align-items: center;
  gap: 10px;
  flex-wrap: wrap;
}
.banner code {
  background: rgba(255, 255, 255, 0.6);
  padding: 1px 6px;
  border-radius: 6px;
  font-family: var(--font-mono);
}
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.16s ease;
}
.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}
@media (max-width: 860px) {
  .topbar-inner {
    padding: 0 14px;
    gap: 12px;
  }
  .brand-text em,
  .xp-num {
    display: none;
  }
  .nav-link {
    padding: 7px 10px;
    font-size: 13px;
  }
}
@media (max-width: 620px) {
  .xp {
    display: none;
  }
}
</style>
