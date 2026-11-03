<script setup>
import { computed, ref } from 'vue'
import StepControls from './StepControls.vue'
import { useStepper } from '../useStepper'

const M = 8 // 数组容量，实际最多存 7 个
const cells = ref(Array(M).fill(null))
const front = ref(0)
const rear = ref(0)
const value = ref('')
const message = ref('')

const { steps, index, playing, setSteps, next, prev, play, stop } = useStepper(760)

const current = computed(() => steps.value[index.value] || null)
const note = computed(
  () => current.value?.note || '容量 8 的数组，牺牲一个单元，最多能存 7 个元素。'
)
const viewCells = computed(() => current.value?.cells || cells.value)
const viewFront = computed(() => current.value?.front ?? front.value)
const viewRear = computed(() => current.value?.rear ?? rear.value)
const hl = computed(() => current.value?.hl ?? -1)
const count = computed(() => (viewRear.value - viewFront.value + M) % M)

function pushStep(cellsSnapshot, f, r, hlIndex, text) {
  return { cells: [...cellsSnapshot], front: f, rear: r, hl: hlIndex, note: text }
}

function doEnqueue() {
  const raw = value.value === '' ? Math.floor(Math.random() * 90 + 10) : Number(value.value)
  if (!Number.isFinite(raw)) {
    message.value = '请输入一个整数'
    return
  }
  if ((rear.value + 1) % M === front.value) {
    message.value = '队满了（(rear+1)%8 == front），入队会被拒绝'
    return
  }
  const nextCells = [...cells.value]
  const nextRear = (rear.value + 1) % M
  nextCells[rear.value] = raw
  setSteps([
    pushStep(
      cells.value,
      front.value,
      rear.value,
      -1,
      `准备入队 ${raw}：rear 指向下标 ${rear.value}，这就是新元素要放的位置。`
    ),
    pushStep(
      nextCells,
      front.value,
      nextRear,
      rear.value,
      `写入 data[${rear.value}] = ${raw}，然后 rear = (${rear.value} + 1) % 8 = ${nextRear}。`
    )
  ])
  cells.value = nextCells
  rear.value = nextRear
  value.value = ''
  message.value = ''
}

function doDequeue() {
  if (front.value === rear.value) {
    message.value = '队空了（front == rear），出队会下溢'
    return
  }
  const popped = cells.value[front.value]
  const nextCells = [...cells.value]
  nextCells[front.value] = null
  const nextFront = (front.value + 1) % M
  setSteps([
    pushStep(
      cells.value,
      front.value,
      rear.value,
      front.value,
      `准备出队：队头是下标 ${front.value} 的 ${popped}。`
    ),
    pushStep(
      nextCells,
      nextFront,
      rear.value,
      -1,
      `front = (${front.value} + 1) % 8 = ${nextFront}，元素 ${popped} 出队。先进先出。`
    )
  ])
  cells.value = nextCells
  front.value = nextFront
  message.value = ''
}

function reset() {
  cells.value = Array(M).fill(null)
  front.value = 0
  rear.value = 0
  setSteps([])
  message.value = ''
}

function demo() {
  reset()
  const list = []
  let arr = Array(M).fill(null)
  let f = 0
  let r = 0
  const ops = [
    ['enq', 1],
    ['enq', 2],
    ['enq', 3],
    ['deq'],
    ['deq'],
    ['enq', 4],
    ['enq', 5],
    ['enq', 6]
  ]
  for (const [op, v] of ops) {
    if (op === 'enq') {
      if ((r + 1) % M === f) {
        list.push(pushStep(arr, f, r, -1, `队满，(rear+1)%8 == front，入队 ${v} 被拒绝。`))
        continue
      }
      arr = [...arr]
      arr[r] = v
      const nr = (r + 1) % M
      list.push(pushStep(arr, f, nr, r, `入队 ${v} 到下标 ${r}，rear 移到 ${nr}。`))
      r = nr
    } else {
      if (f === r) {
        list.push(pushStep(arr, f, r, -1, '队空，出队失败。'))
        continue
      }
      const popped = arr[f]
      arr = [...arr]
      arr[f] = null
      const nf = (f + 1) % M
      list.push(pushStep(arr, nf, r, f, `出队 ${popped}，front 移到 ${nf}。`))
      f = nf
    }
  }
  cells.value = [...arr]
  front.value = f
  rear.value = r
  setSteps(list)
}
</script>

<template>
  <div class="viz">
    <div class="viz-head">
      <div>
        <h4>循环队列：front 与 rear 怎么绕圈</h4>
        <p>数组当环用，rear 走到头就取模回到 0。</p>
      </div>
      <div class="head-actions">
        <button class="btn btn-sm btn-ghost" @click="demo">自动演示</button>
        <button class="btn btn-sm btn-ghost" @click="reset">重置</button>
      </div>
    </div>

    <div class="viz-main">
      <div class="board">
        <div class="markers top">
          <span v-for="n in M" :key="n" class="marker">
            <template v-if="n - 1 === viewFront">
              <span class="tag front">front</span>
            </template>
            <template v-else-if="n - 1 === viewRear && viewRear !== viewFront">
              <span class="tag rear">rear</span>
            </template>
            <template v-else-if="n - 1 === viewRear && viewRear === viewFront">
              <span class="tag both">front · rear</span>
            </template>
          </span>
        </div>

        <div class="cells">
          <div
            v-for="n in M"
            :key="n"
            class="cell"
            :class="{
              filled: viewCells[n - 1] !== null,
              hl: hl === n - 1,
              edge: n - 1 === viewFront || n - 1 === viewRear
            }"
          >
            <span class="val">{{ viewCells[n - 1] === null ? '' : viewCells[n - 1] }}</span>
            <span class="idx">{{ n - 1 }}</span>
          </div>
        </div>

        <div class="formula">
          <span>size = (rear − front + {{ M }}) % {{ M }} = </span>
          <strong>{{ count }}</strong>
          <span class="sep">·</span>
          <span>最多容纳 {{ M - 1 }} 个（牺牲一个单元）</span>
        </div>
      </div>

      <aside class="viz-aside">
        <h5>循环队列的三个公式</h5>
        <ul>
          <li>空：<code>front == rear</code></li>
          <li>满：<code>(rear+1) % M == front</code></li>
          <li>长度：<code>(rear-front+M) % M</code></li>
        </ul>
        <p>rear 到了数组末尾不会溢出，而是取模绕回 0——这就是"循环"的全部含义。</p>
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
      <input v-model="value" class="input" type="number" placeholder="要入队的数（留空随机）" />
      <button class="btn btn-sm btn-primary" @click="doEnqueue">enqueue 入队</button>
      <button class="btn btn-sm" @click="doDequeue">dequeue 出队</button>
      <span v-if="message" class="err">{{ message }}</span>
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
  gap: 30px;
  align-items: flex-start;
  margin: 18px 0 6px;
  flex-wrap: wrap;
}
.board {
  overflow-x: auto;
  padding-bottom: 6px;
}
.viz-aside {
  flex: 1;
  min-width: 240px;
  max-width: 320px;
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
  line-height: 1.95;
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
.markers {
  display: flex;
  gap: 6px;
  height: 20px;
  margin-left: 2px;
}
.marker {
  width: 48px;
  display: flex;
  justify-content: center;
}
.tag {
  font-size: 10px;
  font-weight: 700;
  border-radius: 999px;
  padding: 1px 7px;
  white-space: nowrap;
}
.tag.front {
  color: #0f766e;
  background: #d7f5ee;
}
.tag.rear {
  color: #9a3412;
  background: #fde8d7;
}
.tag.both {
  color: #4c1d95;
  background: #ebe4ff;
}
.cells {
  display: flex;
  gap: 6px;
}
.cell {
  position: relative;
  width: 48px;
  height: 54px;
  border-radius: 10px;
  border: 1.5px dashed var(--line-strong);
  background: var(--surface-2);
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  transition: all 0.26s ease;
}
.cell.filled {
  border-style: solid;
  border-color: #c9c6ec;
  background: #f2f0ff;
}
.cell.edge {
  border-color: #b9b4ef;
}
.cell.hl {
  background: #e2ddff;
  transform: translateY(-4px);
  box-shadow: 0 10px 18px -14px rgba(91, 91, 214, 0.9);
}
.val {
  font-weight: 650;
  font-size: 14px;
}
.idx {
  position: absolute;
  bottom: -17px;
  font-size: 10px;
  color: #b7b4d4;
}
.formula {
  margin-top: 26px;
  font-size: 12.5px;
  color: var(--muted);
  font-family: var(--font-mono);
}
.formula strong {
  color: var(--accent);
  font-size: 14px;
}
.sep {
  margin: 0 8px;
  color: var(--line-strong);
}
.note-box {
  display: flex;
  gap: 10px;
  align-items: flex-start;
  margin-top: 10px;
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
  width: 180px;
}
.err {
  font-size: 12px;
  color: var(--danger);
}
</style>
