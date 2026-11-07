// 与后端通信的唯一入口。所有请求都走 /api，开发时由 Vite 代理到 8000 端口。

class ApiError extends Error {
  constructor(message, status, payload) {
    super(message)
    this.status = status
    this.payload = payload
  }
}

async function request(path, options = {}) {
  let response
  try {
    response = await fetch(`/api${path}`, {
      headers: { 'Content-Type': 'application/json' },
      ...options
    })
  } catch (err) {
    throw new ApiError('连不上后端服务，确认它还在运行。', 0, err)
  }

  let data = null
  const text = await response.text()
  if (text) {
    try {
      data = JSON.parse(text)
    } catch {
      data = { detail: text }
    }
  }

  if (!response.ok) {
    const detail = data?.detail || data?.message || `请求失败（HTTP ${response.status}）`
    throw new ApiError(detail, response.status, data)
  }
  return data
}

const post = (path, body) => request(path, { method: 'POST', body: JSON.stringify(body) })

export const api = {
  bootstrap: () => request('/bootstrap'),
  guide: () => request('/guide'),
  module: (id) => request(`/modules/${encodeURIComponent(id)}`),
  problem: (id) => request(`/problems/${encodeURIComponent(id)}`),
  judge: (payload) => post('/judge', payload),
  coach: (payload) => post('/ai/coach', payload),
  budget: () => request('/ai/budget'),
  markKnowledge: (moduleId, knowledgeId) =>
    post('/progress/knowledge', { moduleId, knowledgeId }),
  wrongbook: () => request('/wrongbook'),
  setNote: (problemId, note) => post(`/wrongbook/${encodeURIComponent(problemId)}/note`, { note }),
  resolveWrong: (problemId) => post(`/wrongbook/${encodeURIComponent(problemId)}/resolve`, {}),
  stats: () => request('/stats'),
  health: () => request('/health')
}

export { ApiError }
