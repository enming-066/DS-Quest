// 全局状态：模块列表、进度、AI 额度、轻提示。
// 只用一个 reactive 对象，够简单，也不容易出"状态同步"的 bug。
import { reactive, computed } from 'vue'
import { api } from './api'

export const state = reactive({
  ready: false,
  error: '',
  modules: [],
  progress: { xp: 0, knowledgeRead: [], problemsSolved: [], moduleCleared: [] },
  ai: { enabled: false, used: 0, limit: 30, remaining: 30 },
  compiler: { cpp: false, c: false },
  wrongCount: 0,
  totalProblems: 0,
  level: 1,
  xpInLevel: 0,
  xpToNext: 200,
  toasts: []
})

export const xpPercent = computed(() =>
  Math.min(100, Math.round((state.xpInLevel / (state.xpToNext || 200)) * 100))
)

let toastId = 0
export function toast(message, type = 'info', timeout = 2600) {
  const id = ++toastId
  state.toasts.push({ id, message, type })
  setTimeout(() => {
    const index = state.toasts.findIndex((t) => t.id === id)
    if (index >= 0) state.toasts.splice(index, 1)
  }, timeout)
}

export async function refreshBootstrap() {
  try {
    const data = await api.bootstrap()
    Object.assign(state, {
      modules: data.modules,
      progress: data.progress,
      ai: data.ai,
      compiler: data.compiler,
      wrongCount: data.wrongCount,
      totalProblems: data.totalProblems,
      level: data.level,
      xpInLevel: data.xpInLevel,
      xpToNext: data.xpToNext,
      ready: true,
      error: ''
    })
    return data
  } catch (err) {
    state.error = err.message || '加载失败'
    state.ready = true
    throw err
  }
}

// 知识点读完：后端加经验，本地先乐观更新一下，界面不会卡
export async function markKnowledgeRead(moduleId, knowledgeId) {
  const key = `${moduleId}/${knowledgeId}`
  if (!state.progress.knowledgeRead.includes(key)) {
    state.progress.knowledgeRead.push(key)
  }
  try {
    const res = await api.markKnowledge(moduleId, knowledgeId)
    state.progress.xp = res.xp
    state.xpInLevel = res.xp % state.xpToNext
    state.level = 1 + Math.floor(res.xp / state.xpToNext)
    if (res.xpGained > 0) toast(`+${res.xpGained} XP · 知识点已标记完成`, 'success')
  } catch {
    /* 离线时忽略，下次进入会重新同步 */
  }
}

export function isKnowledgeRead(moduleId, knowledgeId) {
  return state.progress.knowledgeRead.includes(`${moduleId}/${knowledgeId}`)
}

export function applyJudgeProgress(result, problemId) {
  if (!result?.progress) return
  const { xp, solved } = result.progress
  if (typeof xp === 'number') {
    state.progress.xp = xp
    state.level = 1 + Math.floor(xp / state.xpToNext)
    state.xpInLevel = xp % state.xpToNext
  }
  if (solved && problemId && !state.progress.problemsSolved.includes(problemId)) {
    state.progress.problemsSolved.push(problemId)
  }
  if (result.xpGained > 0) toast(`+${result.xpGained} XP`, 'success')
}
