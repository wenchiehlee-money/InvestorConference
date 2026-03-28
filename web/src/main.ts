import './style.css'
import { loadAll } from './data/loader'
import { parseEntries } from './data/parser'
import { renderPlayerView } from './player/index'
import type { AudioEntry, ContentType } from './types'

const app = document.querySelector<HTMLDivElement>('#app')!

app.innerHTML = `<p class="loading">載入中…</p>`

loadAll()
  .then(data => {
    const entries = parseEntries(data)
    renderFileManager(entries)
  })
  .catch(err => {
    app.innerHTML = `<p class="error">資料載入失敗：${String(err)}</p>`
  })

// ── Routing ───────────────────────────────────────────────────────────────────

let playerCleanup: (() => void) | null = null

function navigateToPlayer(entry: AudioEntry): void {
  sessionStorage.setItem('fm-scroll', String(window.scrollY))
  history.pushState({ view: 'player' }, '', '#player')
  showPlayer(entry)
}

function showPlayer(entry: AudioEntry): void {
  playerCleanup?.()
  playerCleanup = null
  app.innerHTML = ''
  renderPlayerView(entry, app, goBack).then(cleanup => {
    playerCleanup = cleanup
  })
}

function goBack(): void {
  playerCleanup?.()
  playerCleanup = null
  history.back()
}

window.addEventListener('popstate', () => {
  if (!location.hash || location.hash === '#') {
    playerCleanup?.()
    playerCleanup = null
    renderFileManager(allEntries)
    requestAnimationFrame(() => {
      const scroll = sessionStorage.getItem('fm-scroll')
      if (scroll) window.scrollTo(0, Number(scroll))
    })
  }
})

// ── File Manager shell ────────────────────────────────────────────────────────

type ViewMode = '公司分組' | '法說日期' | '列表' | '搜尋'

let currentType: ContentType | 'all' = 'all'
let currentView: ViewMode = '公司分組'
let allEntries: AudioEntry[] = []

function renderFileManager(entries: AudioEntry[]): void {
  allEntries = entries

  app.innerHTML = `
    <header>
      <h1>InvestorConference Player</h1>
      <nav id="type-filter" class="filter-bar">
        <button data-type="all" class="active">全部</button>
        <button data-type="法說會">法說會</button>
        <button data-type="GTC大會">GTC 大會</button>
        <button data-type="Podcast">Podcast</button>
      </nav>
      <nav id="view-tabs" class="view-tabs">
        <button data-view="公司分組" class="active">公司分組</button>
        <button data-view="法說日期">法說日期</button>
        <button data-view="列表">列表</button>
        <button data-view="搜尋">🔍 搜尋</button>
      </nav>
    </header>
    <main id="content"></main>
  `

  document.getElementById('type-filter')!.addEventListener('click', e => {
    const btn = (e.target as HTMLElement).closest('button')
    if (!btn) return
    currentType = btn.dataset['type'] as ContentType | 'all'
    document.querySelectorAll('#type-filter button').forEach(b => b.classList.remove('active'))
    btn.classList.add('active')
    renderContent()
  })

  document.getElementById('view-tabs')!.addEventListener('click', e => {
    const btn = (e.target as HTMLElement).closest('button')
    if (!btn) return
    currentView = btn.dataset['view'] as ViewMode
    document.querySelectorAll('#view-tabs button').forEach(b => b.classList.remove('active'))
    btn.classList.add('active')
    renderContent()
  })

  // Entry click → navigate to player
  document.getElementById('content')!.addEventListener('click', e => {
    const row = (e.target as HTMLElement).closest<HTMLElement>('.entry-row')
    if (!row) return
    const id      = row.dataset['id'] ?? ''
    const quarter = row.dataset['quarter'] ?? ''
    const entry   = allEntries.find(en => en.id === id && en.quarterLabel === quarter)
    if (entry) navigateToPlayer(entry)
  })

  renderContent()
}

function filteredEntries(): AudioEntry[] {
  if (currentType === 'all') return allEntries
  return allEntries.filter(e => e.contentType === currentType)
}

function renderContent(): void {
  const content = document.getElementById('content')!
  const entries = filteredEntries()

  if (entries.length === 0) {
    content.innerHTML = '<p class="empty">目前沒有資料。</p>'
    return
  }

  switch (currentView) {
    case '公司分組':   content.innerHTML = renderGroupedByCompany(entries); break
    case '法說日期':   content.innerHTML = renderGroupedByDate(entries);    break
    case '列表':       content.innerHTML = renderFlatList(entries);         break
    case '搜尋':       renderSearchView(content);                           break
  }
}

// ── duration formatting ───────────────────────────────────────────────────────

function fmtDuration(sec?: number): string {
  if (!sec) return ''
  const h = Math.floor(sec / 3600)
  const m = Math.floor((sec % 3600) / 60)
  const s = sec % 60
  if (h > 0) return `${h}:${String(m).padStart(2, '0')}:${String(s).padStart(2, '0')}`
  return `${m}:${String(s).padStart(2, '0')}`
}

// ── entry row HTML ────────────────────────────────────────────────────────────

function entryRowHtml(entry: AudioEntry): string {
  const srtBadges = entry.srts
    .map(s => `<span class="badge badge-${s.badge.toLowerCase()}">${s.badge}</span>`)
    .join(' ')
  const pdfCount = entry.pdfs.length
    ? `<span class="pdf-count">📄×${entry.pdfs.length}</span>`
    : ''
  const duration = entry.durationSec
    ? `<span class="duration">${fmtDuration(entry.durationSec)}</span>`
    : ''
  const date = entry.irDate ? `<span class="ir-date">${entry.irDate}</span>` : ''
  const quarter = entry.quarterLabel
    ? `<span class="quarter">${entry.quarterLabel}</span>`
    : ''

  return `
    <div class="entry-row" data-id="${entry.id}" data-quarter="${entry.quarterLabel}" data-date="${entry.irDate}">
      <span class="entry-meta">${quarter} ${date}</span>
      <span class="entry-badges">${srtBadges} ${pdfCount} ${duration}</span>
    </div>
  `
}

// ── 公司分組 view ─────────────────────────────────────────────────────────────

function renderGroupedByCompany(entries: AudioEntry[]): string {
  const groups = new Map<string, AudioEntry[]>()
  for (const e of entries) {
    const key = e.id
    if (!groups.has(key)) groups.set(key, [])
    groups.get(key)!.push(e)
  }

  let html = ''
  for (const [id, group] of groups) {
    const first = group[0]
    const name = first.companyName !== id ? `${first.companyName} ${id}` : id
    html += `
      <details class="company-group" open>
        <summary class="company-header">
          <span class="company-name">${name}</span>
          <span class="company-desc">${first.businessDesc}</span>
        </summary>
        <div class="company-entries">
          ${group.map(entryRowHtml).join('')}
        </div>
      </details>
    `
  }
  return html
}

// ── 法說日期分組 view ─────────────────────────────────────────────────────────

function renderGroupedByDate(entries: AudioEntry[]): string {
  const groups = new Map<string, AudioEntry[]>()
  for (const e of entries) {
    const key = e.irDate || '日期未知'
    if (!groups.has(key)) groups.set(key, [])
    groups.get(key)!.push(e)
  }

  // Sorted date keys (desc)
  const sortedKeys = [...groups.keys()].sort((a, b) => b.localeCompare(a))

  let html = ''
  for (const date of sortedKeys) {
    const group = groups.get(date)!
    html += `
      <details class="date-group" open>
        <summary class="date-header">${date}</summary>
        <div class="date-entries">
          ${group.map(e => `
            <div class="date-entry-row">
              <span class="company-name">${e.companyName !== e.id ? `${e.companyName} ${e.id}` : e.id}</span>
              ${entryRowHtml(e)}
            </div>
          `).join('')}
        </div>
      </details>
    `
  }
  return html
}

// ── 平鋪列表 view ─────────────────────────────────────────────────────────────

function renderFlatList(entries: AudioEntry[]): string {
  const rows = entries.map(e => `
    <tr class="entry-row" data-id="${e.id}" data-quarter="${e.quarterLabel}" data-date="${e.irDate}">
      <td>${e.companyName !== e.id ? `${e.companyName} ${e.id}` : e.id}</td>
      <td>${e.quarterLabel}</td>
      <td>${e.irDate}</td>
      <td>
        ${e.srts.map(s => `<span class="badge badge-${s.badge.toLowerCase()}">${s.badge}</span>`).join(' ')}
      </td>
      <td>${e.pdfs.length ? `📄×${e.pdfs.length}` : ''}</td>
      <td>${fmtDuration(e.durationSec)}</td>
    </tr>
  `).join('')

  return `
    <table class="flat-list">
      <thead>
        <tr>
          <th>公司</th><th>季度</th><th>法說日期</th><th>字幕</th><th>PDF</th><th>時長</th>
        </tr>
      </thead>
      <tbody>${rows}</tbody>
    </table>
  `
}

// ── 全文搜尋 view ─────────────────────────────────────────────────────────────

function renderSearchView(container: HTMLElement): void {
  container.innerHTML = `
    <div class="search-bar">
      <input id="search-input" type="search" placeholder="搜尋字幕內容…" autofocus />
    </div>
    <div id="search-results"></div>
  `

  const input = document.getElementById('search-input') as HTMLInputElement
  input.addEventListener('input', () => {
    const q = input.value.trim()
    if (q.length < 2) {
      document.getElementById('search-results')!.innerHTML = ''
      return
    }
    runSearch(q)
  })
}

function runSearch(query: string): void {
  const resultsEl = document.getElementById('search-results')!
  resultsEl.innerHTML = '<p class="loading">搜尋中…</p>'

  const entries = filteredEntries()
  const srtUrls: { entry: AudioEntry; srt: { url: string; badge: string } }[] = []
  for (const entry of entries) {
    for (const srt of entry.srts) {
      srtUrls.push({ entry, srt })
    }
  }

  if (srtUrls.length === 0) {
    resultsEl.innerHTML = '<p class="empty">沒有可搜尋的字幕檔。</p>'
    return
  }

  const matches: { entry: AudioEntry; badge: string; lines: string[] }[] = []
  let pending = srtUrls.length

  resultsEl.innerHTML = `<p class="loading">搜尋中 (0/${srtUrls.length})…</p>`

  let completed = 0
  for (const { entry, srt } of srtUrls) {
    fetch(srt.url)
      .then(r => r.text())
      .then(text => {
        const q = query.toLowerCase()
        const lines = text.split('\n').filter(l => l.toLowerCase().includes(q))
        if (lines.length > 0) {
          matches.push({ entry, badge: srt.badge, lines })
          // Progressive render
          renderSearchResults(resultsEl, matches, query, completed, srtUrls.length)
        }
      })
      .catch(() => { /* skip failed SRT */ })
      .finally(() => {
        completed++
        pending--
        if (pending === 0) {
          renderSearchResults(resultsEl, matches, query, completed, srtUrls.length)
        }
      })
  }
}

function renderSearchResults(
  container: HTMLElement,
  matches: { entry: AudioEntry; badge: string; lines: string[] }[],
  query: string,
  completed: number,
  total: number,
): void {
  const progress = completed < total ? `<p class="loading">搜尋中 (${completed}/${total})…</p>` : ''
  if (matches.length === 0) {
    container.innerHTML = progress + (completed === total ? '<p class="empty">無符合結果。</p>' : '')
    return
  }

  const hl = (text: string) => {
    const re = new RegExp(query.replace(/[.*+?^${}()|[\]\\]/g, '\\$&'), 'gi')
    return text.replace(re, m => `<mark>${m}</mark>`)
  }

  const rows = matches.map(({ entry, badge, lines }) => `
    <div class="search-match entry-row" data-id="${entry.id}" data-quarter="${entry.quarterLabel}">
      <div class="match-header">
        <span class="company-name">${entry.companyName !== entry.id ? `${entry.companyName} ${entry.id}` : entry.id}</span>
        <span class="quarter">${entry.quarterLabel}</span>
        <span class="badge badge-${badge.toLowerCase()}">${badge}</span>
      </div>
      <ul class="match-lines">
        ${lines.slice(0, 5).map(l => `<li>${hl(l)}</li>`).join('')}
        ${lines.length > 5 ? `<li class="more">…還有 ${lines.length - 5} 行</li>` : ''}
      </ul>
    </div>
  `).join('')

  container.innerHTML = progress + rows
}
