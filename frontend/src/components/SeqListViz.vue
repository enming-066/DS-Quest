<script setup>
import { computed, ref } from 'vue'
import StepControls from './StepControls.vue'
import { useStepper } from '../useStepper'

const CAP = 9
const initial = [12, 25, 37, 49, 58]
const cells = ref([...initial])
const pos = ref(4)
const value = ref(66)
const error = ref('')

const { steps, index, playing, setSteps, next, prev, play, stop } = useStepper(820)

const current = computed(() => steps.value[index.value] || null)
const note = computed(() => current.value?.note || '选一个操作，看元素是怎么挪的。')
const hl = computed(() => current.value?.hl || [])
const view = computed(() => current.value?.cells || cells.value)

function reset() {
  cells.value = [...initial]
  setSteps([])
  error.value = ''
}

function doInsert() {
  error.value = ''
  const p = Number(pos.value)
  if (!Number.isInteger(p) || p < 1 || p > cells.value.length + 1) {
    error.value = `位序要在 1 ~ ${cells.value.length + 1} 之间`
    return
  }
  if (cells.value.length >= CAP) {
    error.value = '顺序表满了（容量 9），再插入就上溢了'
    return
  }
  const v = Number(value.value)
  const arr = [...cells.value]
  const list = [
    {
      cells: [...arr],
      note: `要在第 ${p} 个位置插入 ${v}，对应下标 ${p - 1}。先把下标 ${p - 1} 到 ${arr.length - 1} 的元素整体后移一格。`,
      hl: [p - 1]
    }
  ]
  for (let j = arr.length; j >= p; j--) {
    arr[j] = arr[j - 1]
    list.push({
      cells: [...arr],
      note: `下标 ${j - 1} 的 ${arr[j]} → 下标 ${j}。注意是从后往前挪，反过来会覆盖数据。`,
      hl: [j, j - 1]
    })
  }
  arr[p - 1] = v
  list.push({
    cells: [...arr],
    note: `把 ${v} 放进下标 ${p - 1}，length 从 ${arr.length - 1} 变成 ${arr.length}。插入完成。`,
    hl: [p - 1]
  })
  cells.value = [...arr]
  setSteps(list)
}

function doDelete() {
  error.value = ''
  const p = Number(pos.value)
  if (!Number.isInteger(p) || p < 1 || p > cells.value.length) {
    error.value = `位序要在 1 ~ ${cells.value.length} 之间`
    return
  }
  const arr = [...cells.value]
  const saved = arr[p - 1]
  const list = [
    {
      cells: [...arr],
      note: `要删除第 ${p} 个元素（下标 ${p - 1}，值是 ${saved}），后面的元素整体前移一格。`,
      hl: [p - 1]
    }
  ]
  for (let j = p; j < arr.length; j++) {
    arr[j - 1] = arr[j]
    list.push({
      cells: [...arr],
      note: `下标 ${j} 的 ${arr[j]} → 下标 ${j - 1}。删除是从前往后挪。`,
      hl: [j - 1]
    })
  }
  arr.pop()
  list.push({
    cells: [...arr],
    note: `末尾的空位去掉，length 变成 ${arr.length}。删除完成，被删的值是 ${saved}。`,
    hl: []
  })
  cells.value = [...arr]
  setSteps(list)
}

const posLabel = computed(() =>
  Number(pos.value) >= 1 ? `下标 ${Number(pos.value) - 1}` : '非法'
)
</script>

<template>
  <div class="viz">
    <div class="viz-head">
      <div>
        <h4>顺序表：插入与删除</h4>
        <p>连续存储的代价就藏在这几帧动画里——插入和删除都要挪元素。</p>
      </div>
      <button class="btn btn-sm btn-ghost" @click="reset">重置</button>
    </div>

    <div class="viz-main">
      <div class="board">
        <div class="ruler">
          <span class="ruler-label">位序</span>
          <div class="ruler-cells">
            <span v-for="n in CAP" :key="n" class="ruler-cell">{{ n <= view.length ? n : '' }}</span>
          </div>
        </div>

        <div class="cells">
          <div
            v-for="n in CAP"
            :key="n"
            class="cell"
            :class="{ filled: n - 1 < view.length, hl: hl.includes(n - 1) }"
          >
            <span class="value">{{ n - 1 < view.length ? view[n - 1] : '' }}</span>
          </div>
        </div>

        <div class="ruler">
          <span class="ruler-label">下标</span>
          <div class="ruler-cells">
            <span v-for="n in CAP" :key="n" class="ruler-cell idx">{{ n - 1 < view.length ? n - 1 : '' }}</span>
          </div>
        </div>
      </div>

      <aside class="viz-aside">
        <h5>两个必须记牢的结论</h5>
        <ul>
          <li>插入：从后往前挪，平均移动 <code>n/2</code> 个元素</li>
          <li>删除：从前往后挪，平均移动 <code>(n-1)/2</code> 个元素</li>
          <li>位序 <code>i</code> ↔ 下标 <code>i-1</code></li>
          <li>插入范围是 <code>1 ~ n+1</code>，删除是 <code>1 ~ n</code></li>
        </ul>
        <p>挪元素是 O(n) 的根源。想避免它，就换成链表——代价是失去随机访问。</p>
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
      <label class="field">
        <span>位序</span>
        <input v-model="pos" class="input" type="number" min="1" :max="CAP" />
      </label>
      <label class="field">
        <span>值</span>
        <input v-model="value" class="input" type="number" />
      </label>
      <div class="field-actions">
        <button class="btn btn-sm btn-primary" @click="doInsert">插入</button>
        <button class="btn btn-sm" @click="doDelete">删除</button>
      </div>
      <span v-if="error" class="err">{{ error }}</span>
      <span v-else class="hint">你输入的位序 {{ pos }} 对应 {{ posLabel }}</span>
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
.viz-main {
  display: flex;
  gap: 30px;
  align-items: flex-start;
  margin: 18px 0 6px;
  flex-wrap: wrap;
}
.board {
  overflow-x: auto;
  padding-bottom: 4px;
}
.viz-aside {
  flex: 1;
  min-width: 240px;
  max-width: 300px;
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
.ruler {
  display: flex;
  align-items: center;
  gap: 10px;
}
.ruler-label {
  width: 34px;
  flex: none;
  font-size: 11px;
  color: var(--muted);
  letter-spacing: 0.06em;
}
.ruler-cells {
  display: flex;
  gap: 8px;
}
.ruler-cell {
  width: 52px;
  text-align: center;
  font-size: 11px;
  color: var(--muted);
  font-variant-numeric: tabular-nums;
}
.ruler-cell.idx {
  color: #b9b6d6;
}
.cells {
  display: flex;
  gap: 8px;
  margin: 4px 0;
}
.cell {
  width: 52px;
  height: 52px;
  border-radius: 12px;
  border: 1.5px dashed var(--line-strong);
  background: var(--surface-2);
  display: grid;
  place-items: center;
  transition: all 0.28s ease;
}
.cell.filled {
  border-style: solid;
  border-color: #c9c6ec;
  background: #f2f0ff;
  color: var(--ink);
  font-weight: 650;
}
.cell.hl {
  border-color: var(--accent);
  background: #e4e1ff;
  transform: translateY(-4px);
  box-shadow: 0 10px 18px -14px rgba(91, 91, 214, 0.9);
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
  align-items: flex-end;
  gap: 12px;
  margin-top: 14px;
  flex-wrap: wrap;
}
.field {
  display: flex;
  flex-direction: column;
  gap: 4px;
  width: 92px;
}
.field span {
  font-size: 11px;
  color: var(--muted);
  letter-spacing: 0.05em;
}
.field-actions {
  display: flex;
  gap: 8px;
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
