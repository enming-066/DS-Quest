<script setup>
import { computed, ref } from 'vue'
import Icon from './Icon.vue'

const props = defineProps({
  result: { type: Object, default: null },
  running: { type: Boolean, default: false }
})

const openRaw = ref(false)

const verdictMeta = {
  AC: { label: '答案正确', tone: 'ok', icon: 'check' },
  WA: { label: '答案错误', tone: 'bad', icon: 'warn' },
  CE: { label: '编译错误', tone: 'warn', icon: 'warn' },
  TLE: { label: '运行超时', tone: 'warn', icon: 'clock' },
  MLE: { label: '内存超限', tone: 'warn', icon: 'warn' },
  RE: { label: '运行错误', tone: 'bad', icon: 'warn' }
}

const meta = computed(() => verdictMeta[props.result?.verdict] || null)
const errors = computed(() =>
  (props.result?.compile?.issues || []).filter((i) => i.severity === 'error')
)
const warnings = computed(() =>
  (props.result?.compile?.issues || []).filter((i) => i.severity === 'warning')
)
const fail = computed(() => props.result?.firstFail || null)
const tests = computed(() => (props.result?.tests || []).filter((t) => !t.skipped))
</script>

<template>
  <div class="verdict card">
    <div v-if="running" class="verdict-empty">
      <span class="spinner"></span>
      正在编译并运行测试点……
    </div>

    <div v-else-if="!result" class="verdict-empty">
      <Icon name="play" :size="18" />
      写好代码后按 <kbd>Ctrl</kbd> + <kbd>Enter</kbd> 提交，这里会显示每个测试点的结果。
    </div>

    <template v-else>
      <div class="verdict-head" :class="meta?.tone">
        <span class="verdict-icon"><Icon :name="meta?.icon || 'warn'" :size="18" /></span>
        <div class="grow">
          <div class="verdict-line">
            <strong>{{ result.verdictText }}</strong>
            <span class="verdict-code">{{ result.verdict }}</span>
          </div>
          <p>{{ result.message }}</p>
        </div>
        <div class="verdict-stats">
          <span class="vs">
            <em>通过</em>
            <strong>{{ result.passed }}/{{ result.total }}</strong>
          </span>
          <span class="vs">
            <em>耗时</em>
            <strong>{{ result.runTimeMs ?? result.timeMs }} ms</strong>
          </span>
          <span class="vs">
            <em>峰值内存</em>
            <strong>{{ Math.round((result.maxMemoryKb || 0) / 1024) }} MB</strong>
          </span>
        </div>
      </div>

      <!-- 测试点总览 -->
      <div v-if="tests.length" class="test-strip">
        <span class="strip-label">测试点</span>
        <span
          v-for="t in tests"
          :key="t.index"
          class="test-dot"
          :class="t.verdict.toLowerCase()"
          :title="`#${t.index} ${t.verdict}`"
        >
          {{ t.index }}
        </span>
      </div>

      <!-- 编译错误 -->
      <div v-if="errors.length" class="block">
        <h4 class="block-title err-title">
          <Icon name="warn" :size="15" /> 编译没通过，先解决这些
        </h4>
        <div v-for="(e, i) in errors" :key="i" class="issue">
          <div class="issue-head">
            <span class="issue-line">第 {{ e.line }} 行</span>
            <strong>{{ e.title }}</strong>
          </div>
          <code class="issue-msg">{{ e.message }}</code>
          <p class="issue-hint"><Icon name="bulb" :size="13" /> {{ e.hint }}</p>
        </div>
        <button class="raw-toggle" @click="openRaw = !openRaw">
          {{ openRaw ? '收起' : '查看' }}编译器原始输出
        </button>
        <pre v-if="openRaw" class="raw">{{ result.compile.raw }}</pre>
      </div>

      <!-- 第一个出错测试点的详细对比 -->
      <div v-if="fail" class="block">
        <h4 class="block-title">
          <Icon name="target" :size="15" /> 第 {{ fail.index }} 个测试点{{ fail.name ? `（${fail.name}）` : '' }}没通过
        </h4>

        <div v-if="fail.verdict === 'RE'" class="re-box">
          <p>退出码：{{ fail.exitCode }}</p>
          <pre v-if="fail.stderr" class="raw">{{ fail.stderr }}</pre>
          <p v-else class="muted">程序没有输出错误信息，通常是数组越界或空指针。</p>
        </div>

        <div v-else class="io-grid">
          <div class="io-col">
            <div class="io-title">这组测试的输入</div>
            <pre class="io">{{ fail.input || '(空)' }}</pre>
          </div>
          <div class="io-col">
            <div class="io-title">标准答案</div>
            <pre class="io expected">{{ fail.expected || '(空)' }}</pre>
          </div>
          <div class="io-col">
            <div class="io-title">你的输出</div>
            <pre class="io actual">{{ fail.actual || '(空)' }}</pre>
          </div>
        </div>

        <div v-if="fail.diff?.rows?.length" class="diff">
          <div class="diff-head">
            <span>行</span>
            <span>标准答案</span>
            <span>你的输出</span>
          </div>
          <div
            v-for="row in fail.diff.rows"
            :key="row.line"
            class="diff-row"
            :class="{ same: row.same }"
          >
            <span class="diff-line">{{ row.line }}</span>
            <span class="diff-cell">{{ row.expected ?? '（没有这一行）' }}</span>
            <span class="diff-cell">{{ row.actual ?? '（没有这一行）' }}</span>
          </div>
        </div>
      </div>

      <!-- 本地静态检查：免费，不消耗 API -->
      <div v-if="result.staticReview?.length" class="block">
        <h4 class="block-title"><Icon name="bulb" :size="15" /> 本地检查发现的可疑点（免费）</h4>
        <div v-for="(n, i) in result.staticReview" :key="i" class="review">
          <strong>{{ n.title }}</strong>
          <p>{{ n.detail }}</p>
        </div>
      </div>

      <div v-if="warnings.length" class="block">
        <h4 class="block-title muted-title">编译警告（不影响判题）</h4>
        <div v-for="(w, i) in warnings.slice(0, 4)" :key="i" class="review warn">
          <strong>第 {{ w.line }} 行</strong>
          <p>{{ w.message }}</p>
        </div>
      </div>

      <div v-if="result.verdict === 'AC'" class="ac-tip">
        <Icon name="sparkles" :size="16" />
        <span>
          通过了。想再稳一点的话，回到知识点看看这道题对应的复杂度分析——期末笔试问的是"为什么"，不只是"能不能过"。
        </span>
      </div>
    </template>
  </div>
</template>

<style scoped>
.verdict {
  padding: 18px 20px;
  min-height: 120px;
}
.verdict-empty {
  display: flex;
  align-items: center;
  gap: 10px;
  color: var(--muted);
  font-size: 13.5px;
  padding: 24px 4px;
  justify-content: center;
  text-align: center;
}
kbd {
  border: 1px solid var(--line-strong);
  border-bottom-width: 2px;
  border-radius: 5px;
  padding: 0 5px;
  font-family: var(--font-mono);
  font-size: 11px;
  background: var(--surface-2);
}
.spinner {
  width: 16px;
  height: 16px;
  border-radius: 50%;
  border: 2px solid var(--line-strong);
  border-top-color: var(--accent);
  animation: spin 0.8s linear infinite;
}
@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}
.verdict-head {
  display: flex;
  align-items: flex-start;
  gap: 12px;
  padding: 14px 16px;
  border-radius: 12px;
  background: var(--surface-2);
}
.verdict-head.ok {
  background: var(--success-soft);
}
.verdict-head.bad {
  background: var(--danger-soft);
}
.verdict-head.warn {
  background: var(--warn-soft);
}
.verdict-icon {
  width: 32px;
  height: 32px;
  border-radius: 10px;
  display: grid;
  place-items: center;
  background: rgba(255, 255, 255, 0.7);
  flex: none;
}
.verdict-head.ok .verdict-icon {
  color: var(--success);
}
.verdict-head.bad .verdict-icon {
  color: var(--danger);
}
.verdict-head.warn .verdict-icon {
  color: var(--warn);
}
.verdict-line {
  display: flex;
  align-items: baseline;
  gap: 8px;
}
.verdict-line strong {
  font-size: 16px;
  color: var(--ink);
}
.verdict-code {
  font-family: var(--font-mono);
  font-size: 11px;
  color: var(--muted);
  background: rgba(255, 255, 255, 0.7);
  padding: 1px 6px;
  border-radius: 5px;
}
.verdict-head p {
  margin: 3px 0 0;
  font-size: 13px;
  color: var(--ink-2);
}
.verdict-stats {
  display: flex;
  gap: 16px;
  flex: none;
}
.vs {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  line-height: 1.3;
}
.vs em {
  font-style: normal;
  font-size: 10.5px;
  color: var(--muted);
}
.vs strong {
  font-size: 13px;
  color: var(--ink);
  font-variant-numeric: tabular-nums;
}
.test-strip {
  display: flex;
  align-items: center;
  gap: 6px;
  margin-top: 14px;
  flex-wrap: wrap;
}
.strip-label {
  font-size: 11px;
  color: var(--muted);
  margin-right: 2px;
}
.test-dot {
  min-width: 24px;
  height: 24px;
  padding: 0 6px;
  border-radius: 7px;
  display: grid;
  place-items: center;
  font-size: 11px;
  font-weight: 700;
  background: var(--bg-soft);
  color: var(--muted);
}
.test-dot.ac {
  background: var(--success-soft);
  color: var(--success);
}
.test-dot.wa,
.test-dot.re {
  background: var(--danger-soft);
  color: var(--danger);
}
.test-dot.tle,
.test-dot.mle {
  background: var(--warn-soft);
  color: var(--warn);
}
.block {
  margin-top: 18px;
  padding-top: 16px;
  border-top: 1px solid var(--line);
}
.block-title {
  display: flex;
  align-items: center;
  gap: 7px;
  font-size: 13.5px;
  color: var(--ink);
  margin-bottom: 12px;
}
.err-title {
  color: var(--danger);
}
.muted-title {
  color: var(--muted);
  font-weight: 600;
}
.issue {
  border: 1px solid #f3d3d3;
  background: #fffafa;
  border-radius: 10px;
  padding: 10px 12px;
  margin-bottom: 8px;
}
.issue-head {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 13px;
}
.issue-line {
  font-family: var(--font-mono);
  font-size: 11px;
  background: var(--danger-soft);
  color: var(--danger);
  padding: 1px 7px;
  border-radius: 5px;
}
.issue-msg {
  display: block;
  margin-top: 6px;
  font-family: var(--font-mono);
  font-size: 11.5px;
  color: var(--muted);
  white-space: pre-wrap;
  word-break: break-word;
}
.issue-hint {
  margin: 7px 0 0;
  font-size: 12.5px;
  color: var(--ink-2);
  display: flex;
  gap: 6px;
  align-items: flex-start;
}
.raw-toggle {
  border: none;
  background: transparent;
  color: var(--accent);
  font-size: 12px;
  padding: 4px 0;
}
.raw {
  margin: 8px 0 0;
  padding: 12px;
  background: #1c1b2b;
  color: #d9d6ee;
  border-radius: 8px;
  font-family: var(--font-mono);
  font-size: 11.5px;
  line-height: 1.6;
  white-space: pre-wrap;
  max-height: 260px;
  overflow: auto;
}
.io-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 10px;
}
.io-title {
  font-size: 11px;
  color: var(--muted);
  margin-bottom: 5px;
  letter-spacing: 0.04em;
}
.io {
  margin: 0;
  padding: 10px 12px;
  border-radius: 8px;
  background: var(--surface-2);
  border: 1px solid var(--line);
  font-family: var(--font-mono);
  font-size: 12px;
  white-space: pre-wrap;
  word-break: break-all;
  max-height: 180px;
  overflow: auto;
  color: var(--ink-2);
}
.io.expected {
  border-color: #cdeade;
  background: #f6fdfa;
}
.io.actual {
  border-color: #f3d3d3;
  background: #fffafa;
}
.diff {
  margin-top: 12px;
  border: 1px solid var(--line);
  border-radius: 8px;
  overflow: hidden;
  font-family: var(--font-mono);
  font-size: 12px;
}
.diff-head,
.diff-row {
  display: grid;
  grid-template-columns: 40px 1fr 1fr;
  gap: 1px;
}
.diff-head {
  background: var(--surface-2);
  color: var(--muted);
  font-size: 11px;
}
.diff-head span,
.diff-row span {
  padding: 5px 9px;
}
.diff-row {
  background: #fff5f5;
  border-top: 1px solid #f7e3e3;
}
.diff-row.same {
  background: #fbfbfe;
  border-top-color: var(--line);
}
.diff-line {
  color: var(--muted);
  text-align: right;
}
.diff-cell {
  white-space: pre-wrap;
  word-break: break-all;
  border-left: 1px solid #f1e6e6;
}
.review {
  border-left: 3px solid var(--warn);
  background: var(--warn-soft);
  border-radius: 0 8px 8px 0;
  padding: 9px 13px;
  margin-bottom: 8px;
}
.review strong {
  font-size: 13px;
  color: #92400e;
}
.review p {
  margin: 3px 0 0;
  font-size: 12.5px;
  color: #7c4a12;
  line-height: 1.7;
}
.review.warn {
  border-left-color: var(--line-strong);
  background: var(--surface-2);
}
.review.warn strong {
  color: var(--ink-2);
}
.review.warn p {
  color: var(--muted);
}
.re-box p {
  margin: 0 0 8px;
  font-size: 13px;
  color: var(--ink-2);
}
.muted {
  color: var(--muted);
  font-size: 12.5px;
}
.ac-tip {
  display: flex;
  gap: 10px;
  align-items: flex-start;
  margin-top: 16px;
  padding: 12px 14px;
  border-radius: 10px;
  background: linear-gradient(135deg, #eefbf5, #f2f0ff);
  color: #0b6b52;
  font-size: 13px;
}
@media (max-width: 720px) {
  .verdict-stats {
    display: none;
  }
  .diff-head,
  .diff-row {
    grid-template-columns: 30px 1fr 1fr;
  }
}
</style>
