// 一个"够用就好"的 Markdown 渲染器。
// 为什么要自己写：这台电脑上不装 marked/markdown-it 也能跑，依赖越少越不容易坏。
// 支持：标题、段落、列表、任务清单、引用、表格、代码块、分割线、
//       以及 :::tip / :::warning 这类自定义提示块。

const ESCAPES = { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }

function escapeHtml(text) {
  return String(text ?? '').replace(/[&<>"']/g, (c) => ESCAPES[c])
}

function renderInline(text) {
  const codes = []
  let s = escapeHtml(text)

  // 先把行内代码抠出来，避免里面的 ** 或 * 被当成强调
  s = s.replace(/`([^`]+)`/g, (_, code) => {
    codes.push(`<code>${code}</code>`)
    return `\u0000${codes.length - 1}\u0000`
  })

  s = s.replace(/\[([^\]]+)\]\(([^)\s]+)\)/g,
    '<a href="$2" target="_blank" rel="noopener noreferrer">$1</a>')
  s = s.replace(/\*\*([^*]+)\*\*/g, '<strong>$1</strong>')
  s = s.replace(/(^|[^*])\*([^*\n]+)\*/g, '$1<em>$2</em>')
  s = s.replace(/~~([^~]+)~~/g, '<del>$1</del>')

  s = s.replace(/\u0000(\d+)\u0000/g, (_, index) => codes[Number(index)])
  return s
}

const CALLOUT_META = {
  tip: { label: '提示', icon: '💡' },
  note: { label: '说明', icon: '📌' },
  warning: { label: '注意', icon: '⚠️' },
  exam: { label: '考点', icon: '🎯' },
  pitfall: { label: '易错点', icon: '🕳️' }
}

function isTableSeparator(line) {
  return /^\s*\|?[\s:-]*-[\s:|-]*\|?\s*$/.test(line) && line.includes('-')
}

function splitRow(line) {
  let s = line.trim()
  if (s.startsWith('|')) s = s.slice(1)
  if (s.endsWith('|')) s = s.slice(0, -1)
  return s.split('|').map((cell) => cell.trim())
}

export function renderMarkdown(source) {
  const lines = String(source ?? '').replace(/\r\n?/g, '\n').split('\n')
  const out = []
  let i = 0

  while (i < lines.length) {
    const line = lines[i]

    // 空行
    if (!line.trim()) {
      i += 1
      continue
    }

    // 代码块
    const fence = line.match(/^```\s*([\w+#-]*)\s*$/)
    if (fence) {
      const lang = fence[1] || 'text'
      const buffer = []
      i += 1
      while (i < lines.length && !/^```/.test(lines[i])) {
        buffer.push(lines[i])
        i += 1
      }
      i += 1 // 跳过结尾的 ```
      out.push(
        `<pre class="md-code" data-lang="${escapeHtml(lang)}"><code>${escapeHtml(
          buffer.join('\n')
        )}</code></pre>`
      )
      continue
    }

    // 自定义提示块 :::type 标题
    const callout = line.match(/^:::\s*([a-z]+)\s*(.*)$/)
    if (callout) {
      const type = CALLOUT_META[callout[1]] ? callout[1] : 'note'
      const meta = CALLOUT_META[type]
      const title = callout[2]?.trim() || meta.label
      const buffer = []
      i += 1
      while (i < lines.length && !/^:::\s*$/.test(lines[i])) {
        buffer.push(lines[i])
        i += 1
      }
      i += 1
      out.push(
        `<div class="md-callout md-callout-${type}">` +
          `<div class="md-callout-head"><span class="md-callout-icon">${meta.icon}</span>` +
          `<span>${escapeHtml(title)}</span></div>` +
          `<div class="md-callout-body">${renderMarkdown(buffer.join('\n'))}</div>` +
          `</div>`
      )
      continue
    }

    // 标题
    const heading = line.match(/^(#{1,6})\s+(.*)$/)
    if (heading) {
      const level = heading[1].length
      out.push(`<h${level} class="md-h${level}">${renderInline(heading[2])}</h${level}>`)
      i += 1
      continue
    }

    // 分割线
    if (/^\s*([-*_])\1{2,}\s*$/.test(line)) {
      out.push('<hr class="md-hr" />')
      i += 1
      continue
    }

    // 表格
    if (line.includes('|') && i + 1 < lines.length && isTableSeparator(lines[i + 1])) {
      const header = splitRow(line)
      i += 2
      const rows = []
      while (i < lines.length && lines[i].includes('|') && lines[i].trim()) {
        rows.push(splitRow(lines[i]))
        i += 1
      }
      const thead = header.map((c) => `<th>${renderInline(c)}</th>`).join('')
      const tbody = rows
        .map((row) => `<tr>${row.map((c) => `<td>${renderInline(c)}</td>`).join('')}</tr>`)
        .join('')
      out.push(
        `<div class="md-table-wrap"><table class="md-table"><thead><tr>${thead}</tr></thead>` +
          `<tbody>${tbody}</tbody></table></div>`
      )
      continue
    }

    // 引用
    if (/^>\s?/.test(line)) {
      const buffer = []
      while (i < lines.length && /^>\s?/.test(lines[i])) {
        buffer.push(lines[i].replace(/^>\s?/, ''))
        i += 1
      }
      out.push(`<blockquote class="md-quote">${renderMarkdown(buffer.join('\n'))}</blockquote>`)
      continue
    }

    // 列表（无序 / 有序 / 任务清单）
    const listMatch = line.match(/^(\s*)([-*+]|\d+\.)\s+(.*)$/)
    if (listMatch) {
      const ordered = /\d/.test(listMatch[2])
      const items = []
      while (i < lines.length) {
        const m = lines[i].match(/^(\s*)([-*+]|\d+\.)\s+(.*)$/)
        if (!m) break
        let content = m[3]
        let cls = ''
        if (/^\[[ xX]\]\s+/.test(content)) {
          const checked = /^\[[xX]\]/.test(content)
          content = content.replace(/^\[[ xX]\]\s+/, '')
          cls = ' class="task-item"'
          content = `<span class="task-box${checked ? ' checked' : ''}">${
            checked ? '✓' : ''
          }</span><span>${renderInline(content)}</span>`
          items.push(`<li${cls}>${content}</li>`)
        } else {
          items.push(`<li>${renderInline(content)}</li>`)
        }
        i += 1
      }
      const tag = ordered ? 'ol' : 'ul'
      out.push(`<${tag} class="md-list">${items.join('')}</${tag}>`)
      continue
    }

    // 段落：一直吃到空行或下一个块级元素
    const paragraph = []
    while (i < lines.length && lines[i].trim()) {
      if (/^(#{1,6}\s|```|:::|>\s?|\s*([-*+]|\d+\.)\s)/.test(lines[i])) break
      if (lines[i].includes('|') && i + 1 < lines.length && isTableSeparator(lines[i + 1])) break
      paragraph.push(lines[i])
      i += 1
    }
    if (paragraph.length) {
      out.push(`<p class="md-p">${renderInline(paragraph.join(' '))}</p>`)
    } else {
      // 兜底：认不出来的行也要消费掉，否则会死循环
      out.push(`<p class="md-p">${renderInline(lines[i])}</p>`)
      i += 1
    }
  }

  return out.join('\n')
}

export function plainText(source, limit = 160) {
  const text = String(source ?? '')
    .replace(/```[\s\S]*?```/g, ' ')
    .replace(/[#>*`|\-]/g, ' ')
    .replace(/\s+/g, ' ')
    .trim()
  return text.length > limit ? `${text.slice(0, limit)}…` : text
}
