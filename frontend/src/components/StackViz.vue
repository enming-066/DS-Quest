<script setup>
import { computed, ref } from 'vue'
import StepControls from './StepControls.vue'
import { useStepper } from '../useStepper'

const CAP = 8
const stack = ref([10, 20, 30])
const value = ref('')
const message = ref('')

const { steps, index, playing, setSteps, next, prev, play, stop } = useStepper(760)

const current = computed(() => steps.value[index.value] || null)
const note = computed(() => current.value?.note || '栈顶在右边，只能从右边进、从右边出。')
const view = computed(() => current.value?.stack || stack.value)
const hl = computed(() => current.value?.hl ?? -1)

function push(v) {
  if (stack.value.length >= CAP) {
    message.value = '栈满了，再入栈就上溢（overflow）'
    return
  }
  const nextStack = [...stack.value, v]
  setSteps([
    { stack: [...stack.value], hl: -1, note: `准备把 ${v} 压入栈顶。` },
    {
      stack: [...nextStack],
      hl: nextStack.length - 1,
      note: `入栈：top 从 ${stack.value.length - 1} 变成 ${nextStack.length - 1}，新元素成为栈顶。`
    }
  ])
  stack.value = nextStack
  message.value = ''
}

function pop() {
  if (!stack.value.length) {
    message.value = '栈空了，再出栈就下溢（underflow）'
    return
  }
  const topValue = stack.value[stack.value.length - 1]
  const nextStack = stack.value.slice(0, -1)
  setSteps([
    { stack: [...stack.value], hl: stack.value.length - 1, note: `栈顶是 ${topValue}，准备弹出。` },
    {
      stack: [...nextStack],
      hl: -1,
      note: `出栈：弹出 ${topValue}，top 从 ${stack.value.length - 1} 变成 ${nextStack.length - 1}。后进先出。`
    }
  ])
  stack.value = nextStack
  message.value = ''
}

function doPush() {
  const raw = value.value === '' ? Math.floor(Math.random() * 90 + 10) : Number(value.value)
  if (!Number.isFinite(raw)) {
    message.value = '请输入一个整数'
    return
  }
  push(raw)
  value.value = ''
}

function reset() {
  stack.value = [10, 20, 30]
  setSteps([])
  message.value = ''
}

function demo() {
  reset()
  stack.value = []
  const list = []
  let arr = []
  const ops = [5, 8, 3, 9, 1]
  for (const v of ops) {
    arr = [...arr, v]
    list.push({ stack: [...arr], hl: arr.length - 1, note: `push(${v})：top → ${arr.length - 1}` })
  }
  for (let i = 0; i < 3; i++) {
    const top = arr[arr.length - 1]
    arr = arr.slice(0, -1)
    list.push({
      stack: [...arr],
      hl: arr.length - 1,
      note: `pop() 返回 ${top}。注意最后进的最先出：${ops.slice().reverse().slice(0, i + 1).join(' → ')}`
    })
  }
  stack.value = [...arr]
  setSteps(list)
}
</script>

<template>
  <div class="viz">
    <div class="viz-head">
      <div>
        <h4>栈：入栈与出栈</h4>
        <p>只有一个口，push 和 pop 都在右端发生。</p>
      </div>
      <div class="head-actions">
        <button class="btn btn-sm btn-ghost" @click="demo">自动演示</button>
        <button class="btn btn-sm btn-ghost" @click="reset">重置</button>
      </div>
    </div>

    <div class="viz-main">
      <div class="stack-area">
        <div class="slots">
          <div
            v-for="n in CAP"
            :key="n"
            class="slot"
            :class="{
              filled: CAP - n < view.length,
              top: CAP - n === view.length - 1,
              hl: hl >= 0 && hl === CAP - n
            }"
          >
            <span class="slot-idx">{{ CAP - n }}</span>
            <span class="slot-val">{{ CAP - n < view.length ? view[CAP - n] : '' }}</span>
            <span v-if="CAP - n === view.length - 1" class="top-tag">top</span>
          </div>
        </div>
        <div class="axis">
          <span>↑ 越往上越靠近栈顶，只有最上面那格能动</span>
        </div>
      </div>

      <aside class="viz-aside">
        <h5>记住这几个判断</h5>
        <ul>
          <li><code>top = -1</code> → 空栈</li>
          <li><code>top = MAXSIZE-1</code> → 满栈（上溢）</li>
          <li><code>S.data[++top] = e</code> 入栈</li>
          <li><code>e = S.data[top--]</code> 出栈</li>
          <li>栈里还剩 <code>top+1</code> 个元素</li>
        </ul>
        <p>所有操作只碰栈顶，所以都是 O(1)。</p>
      </aside>
    </div>

    <div class="note-box">
      <span class="note-tag">过程</span>
      <span>{{ note }}</span>
    </div>

    <StepControls
      :index="index"
      :total="steps.length"
      :playing="playing"
      @prev="prev"
      @next="next"
      @play="play"
      @pause="stop"
      @reset="reset"
    />

    <div class="form">
      <input v-model="value" class="input" type="number" placeholder="要压入的数（留空随机）" />
      <button class="btn btn-sm btn-primary" @click="doPush">push 入栈</button>
      <button class="btn btn-sm" @click="pop">pop 出栈</button>
      <span v-if="message" class="err">{{ message }}</span>
      <span v-else class="hint">当前元素个数：{{ view.length }} / {{ CAP }}</span>
    </div>
  </div>
</template>

<style scoped>
.viz {
  padding: 20px;
}
.viz-head {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 12px;
}
.viz-head h4 {
  font-size: 16px;
}
.viz-head p {
  margin: 4px 0 0;
  color: var(--muted);
  font-size: 13px;
}
.head-actions {
  display: flex;
  gap: 4px;
}
.viz-main {
  display: flex;
  gap: 32px;
  align-items: flex-start;
  margin: 18px 0 6px;
  flex-wrap: wrap;
}
.stack-area {
  display: flex;
  flex-direction: column;
  gap: 6px;
  align-items: flex-start;
}
.slots {
  display: flex;
  flex-direction: column;
  gap: 6px;
}
.slot {
  position: relative;
  width: 210px;
  height: 38px;
  border-radius: 10px;
  border: 1.5px dashed var(--line-strong);
  background: var(--surface-2);
  display: flex;
  align-items: center;
  padding: 0 12px;
  gap: 10px;
  transition: all 0.28s ease;
}
.slot.filled {
  border-style: solid;
  border-color: #c9c6ec;
  background: #f2f0ff;
}
.slot.top {
  border-color: var(--accent);
  box-shadow: 0 0 0 3px rgba(91, 91, 214, 0.1);
}
.slot.hl {
  background: #e2ddff;
  transform: translateX(6px);
}
.slot-idx {
  font-size: 10px;
  color: #b7b4d4;
  width: 14px;
  font-variant-numeric: tabular-nums;
}
.slot-val {
  font-weight: 650;
  color: var(--ink);
}
.top-tag {
  margin-left: auto;
  font-size: 10px;
  font-weight: 700;
  color: var(--accent);
  background: var(--accent-soft);
  border-radius: 999px;
  padding: 1px 8px;
  letter-spacing: 0.04em;
}
.axis {
  font-size: 11px;
  color: var(--muted);
  margin-top: 2px;
}
.viz-aside {
  flex: 1;
  min-width: 240px;
  max-width: 340px;
  border: 1px dashed var(--line-strong);
  border-radius: 12px;
  padding: 14px 16px;
  background: var(--surface-2);
}
.viz-aside h5 {
  font-size: 12.5px;
  color: var(--ink);
  margin-bottom: 8px;
}
.viz-aside ul {
  margin: 0;
  padding-left: 18px;
  font-size: 12.5px;
  color: var(--ink-2);
  line-height: 1.9;
}
.viz-aside code {
  font-family: var(--font-mono);
  font-size: 11.5px;
  background: #eceaf8;
  color: #4a3fd0;
  padding: 1px 5px;
  border-radius: 4px;
}
.viz-aside p {
  margin: 10px 0 0;
  font-size: 12px;
  color: var(--muted);
}
.note-box {
  display: flex;
  gap: 10px;
  align-items: flex-start;
  margin-top: 14px;
  padding: 11px 14px;
  border-radius: 10px;
  background: var(--surface-2);
  border: 1px solid var(--line);
  font-size: 13.5px;
  color: var(--ink-2);
  min-height: 46px;
}
.note-tag {
  flex: none;
  font-size: 11px;
  font-weight: 700;
  color: var(--accent);
  background: var(--accent-soft);
  border-radius: 999px;
  padding: 1px 8px;
  margin-top: 1px;
}
.form {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-top: 14px;
  flex-wrap: wrap;
}
.form .input {
  width: 170px;
}
.hint {
  font-size: 12px;
  color: var(--muted);
}
.err {
  font-size: 12px;
  color: var(--danger);
}
</style>
