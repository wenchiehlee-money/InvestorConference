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

// ── HTML escaping ─────────────────────────────────────────────────────────────

const esc = (s: string) =>
  s.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;')
const escAttr = (s: string) => esc(s).replace(/"/g, '&quot;')

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

// ── File Manager state ────────────────────────────────────────────────────────

type ViewMode = '列表' | '公司分組' | '法說日期' | '搜尋'

let currentType: ContentType | 'all' = 'all'
let currentView: ViewMode = '列表'
let quickSearch = ''
let allEntries: AudioEntry[] = []

// ── File Manager render ───────────────────────────────────────────────────────

function renderFileManager(entries: AudioEntry[]): void {
  allEntries = entries

  app.innerHTML = `
    <div class="fm-page">
      <div class="fm-page-header">
        <h1 class="fm-page-title">法說會逐字稿 Player</h1>
        <p class="fm-page-subtitle">公開法說會音訊、字幕、投影片一站瀏覽</p>
      </div>

      <div class="fm-toolbar">
        <div class="fm-search-wrap">
          <span class="fm-search-icon">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
              <circle cx="11" cy="11" r="8"/><path d="m21 21-4.35-4.35"/>
            </svg>
          </span>
          <input id="quick-search" type="search" class="fm-search-input"
            placeholder="搜尋股號／股名" value="${escAttr(quickSearch)}">
        </div>
        <select id="type-select" class="fm-select">
          <option value="all"${currentType === 'all'     ? ' selected' : ''}>全類型</option>
          <option value="法說會"${currentType === '法說會'  ? ' selected' : ''}>法說會</option>
          <option value="GTC大會"${currentType === 'GTC大會' ? ' selected' : ''}>GTC 大會</option>
          <option value="Podcast"${currentType === 'Podcast' ? ' selected' : ''}>Podcast</option>
        </select>
      </div>

      <div class="fm-view-tabs" id="view-tabs">
        ${(['列表', '公司分組', '法說日期', '搜尋'] as ViewMode[]).map(v => `
          <button data-view="${v}"${currentView === v ? ' class="active"' : ''}>
            ${v === '搜尋' ? '🔍 全文搜尋' : v}
          </button>
        `).join('')}
      </div>

      <div id="content" class="fm-content"></div>
    </div>
  `

  document.getElementById('quick-search')!.addEventListener('input', e => {
    quickSearch = (e.target as HTMLInputElement).value.trim()
    renderContent()
  })

  document.getElementById('type-select')!.addEventListener('change', e => {
    currentType = (e.target as HTMLSelectElement).value as ContentType | 'all'
    renderContent()
  })

  document.getElementById('view-tabs')!.addEventListener('click', e => {
    const btn = (e.target as HTMLElement).closest('button')
    if (!btn?.dataset['view']) return
    currentView = btn.dataset['view'] as ViewMode
    document.querySelectorAll('#view-tabs button').forEach(b => b.classList.remove('active'))
    btn.classList.add('active')
    renderContent()
  })

  document.getElementById('content')!.addEventListener('click', e => {
    const target = e.target as HTMLElement
    // Let PDF links and checkboxes handle their own events
    if (target.closest('a') || target.closest('input')) return
    const row = target.closest<HTMLElement>('.fm-data-row, .entry-row, .search-match')
    if (!row || row.classList.contains('no-srt')) return
    const id      = row.dataset['id'] ?? ''
    const quarter = row.dataset['quarter'] ?? ''
    const entry   = allEntries.find(en => en.id === id && en.quarterLabel === quarter)
    if (entry && entry.srts.length > 0) navigateToPlayer(entry)
  })

  renderContent()
}

function filteredEntries(): AudioEntry[] {
  let entries = currentType === 'all'
    ? allEntries
    : allEntries.filter(e => e.contentType === currentType)
  if (quickSearch) {
    const q = quickSearch.toLowerCase()
    entries = entries.filter(e =>
      e.id.toLowerCase().includes(q) ||
      e.companyName.toLowerCase().includes(q)
    )
  }
  return entries
}

function renderContent(): void {
  const content = document.getElementById('content')!
  const entries = filteredEntries()

  if (entries.length === 0 && currentView !== '搜尋') {
    content.innerHTML = '<p class="empty">目前沒有符合的資料。</p>'
    return
  }

  switch (currentView) {
    case '列表':     content.innerHTML = renderFlatList(entries);         break
    case '公司分組': content.innerHTML = renderGroupedByCompany(entries); break
    case '法說日期': content.innerHTML = renderGroupedByDate(entries);    break
    case '搜尋':     renderSearchView(content);                           break
  }
}

// ── Duration formatting ───────────────────────────────────────────────────────

function fmtDuration(sec?: number): string {
  if (!sec) return ''
  const h = Math.floor(sec / 3600)
  const m = Math.floor((sec % 3600) / 60)
  const s = sec % 60
  if (h > 0) return `${h}:${String(m).padStart(2, '0')}:${String(s).padStart(2, '0')}`
  return `${m}:${String(s).padStart(2, '0')}`
}

function fmtDurationHHMMSS(sec: number): string {
  const h = Math.floor(sec / 3600)
  const m = Math.floor((sec % 3600) / 60)
  const s = sec % 60
  return `${String(h).padStart(2, '0')}:${String(m).padStart(2, '0')}:${String(s).padStart(2, '0')}`
}

// ── SVG icons ─────────────────────────────────────────────────────────────────

const ICON_DOC = `<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
  <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/>
</svg>`

const ICON_CAL = `<svg class="cell-icon" width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
  <rect x="3" y="4" width="18" height="18" rx="2" ry="2"/><line x1="16" y1="2" x2="16" y2="6"/><line x1="8" y1="2" x2="8" y2="6"/><line x1="3" y1="10" x2="21" y2="10"/>
</svg>`

const ICON_CLOCK = `<svg class="cell-icon" width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
  <circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/>
</svg>`

const ICON_LINK = `<svg width="10" height="10" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
  <path d="M18 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h6"/><polyline points="15 3 21 3 21 9"/><line x1="10" y1="14" x2="21" y2="3"/>
</svg>`

// ── Flat List (AlphaMemo style) ───────────────────────────────────────────────

function renderFlatList(entries: AudioEntry[]): string {
  const rows = entries.map(e => {
    const irPdf   = e.pdfs.find(p => p.label === 'ir')
    const irEnPdf = e.pdfs.find(p => p.label === 'ir_en')
    const noSrt   = e.srts.length === 0
    const name    = e.companyName !== e.id ? e.companyName : ''

    const srtBadgesHtml = e.srts
      .map(s => `<span class="badge badge-${s.badge.toLowerCase()}">${s.badge}</span>`)
      .join('')

    const zhPdf = irPdf
      ? `<a class="pdf-pill" href="${escAttr(irPdf.url)}" target="_blank" rel="noopener">${ICON_LINK} 簡報</a>`
      : `<span class="pdf-pill empty">-</span>`

    const enPdf = irEnPdf
      ? `<a class="pdf-pill" href="${escAttr(irEnPdf.url)}" target="_blank" rel="noopener">${ICON_LINK} Deck</a>`
      : `<span class="pdf-pill empty">-</span>`

    return `
      <div class="fm-data-row${noSrt ? ' no-srt' : ''}"
           data-id="${escAttr(e.id)}"
           data-quarter="${escAttr(e.quarterLabel)}"
           data-date="${escAttr(e.irDate)}">
        <div class="fm-col-center">
          <input type="checkbox" class="row-checkbox"${noSrt ? ' disabled' : ''}>
        </div>
        <div class="stock-cell">
          <div class="stock-icon-wrap">${ICON_DOC}</div>
          <div class="stock-info">
            <span class="stock-name">${esc(name || e.id)}</span>
            ${name ? `<span class="stock-code">${esc(e.id)}</span>` : ''}
            ${srtBadgesHtml ? `<div class="srt-badges">${srtBadgesHtml}</div>` : ''}
          </div>
        </div>
        <div class="date-cell">
          ${ICON_CAL}
          ${esc(e.irDate || e.quarterLabel || '-')}
        </div>
        <div class="dur-cell">
          ${e.durationSec
            ? `${ICON_CLOCK} ${fmtDurationHHMMSS(e.durationSec)}`
            : '-'}
        </div>
        <div class="fm-col-center">${zhPdf}</div>
        <div class="fm-col-center">${enPdf}</div>
      </div>
    `
  }).join('')

  return `
    <div class="fm-list-wrap">
      <div class="fm-header-row">
        <div class="fm-col-center">AI 討論</div>
        <div style="padding-left:54px">股名</div>
        <div class="fm-col-center">日期</div>
        <div class="fm-col-center">時長</div>
        <div class="fm-col-center">中文簡報</div>
        <div class="fm-col-center">英文簡報</div>
      </div>
      ${rows || '<p class="empty">目前沒有資料。</p>'}
    </div>
  `
}

// ── Entry row for grouped views ───────────────────────────────────────────────

function entryRowHtml(entry: AudioEntry): string {
  const irPdf   = entry.pdfs.find(p => p.label === 'ir')
  const irEnPdf = entry.pdfs.find(p => p.label === 'ir_en')
  const noSrt   = entry.srts.length === 0

  const srtBadges = entry.srts
    .map(s => `<span class="badge badge-${s.badge.toLowerCase()}">${s.badge}</span>`)
    .join('')

  const pdfLinks = [
    irPdf   ? `<a class="pdf-pill" href="${escAttr(irPdf.url)}"   target="_blank" rel="noopener">${ICON_LINK} 簡報</a>` : '',
    irEnPdf ? `<a class="pdf-pill" href="${escAttr(irEnPdf.url)}" target="_blank" rel="noopener">${ICON_LINK} Deck</a>`  : '',
  ].filter(Boolean).join('')

  return `
    <div class="entry-row${noSrt ? ' no-srt' : ''}"
         data-id="${escAttr(entry.id)}"
         data-quarter="${escAttr(entry.quarterLabel)}"
         data-date="${escAttr(entry.irDate)}">
      <span class="entry-quarter">
        ${entry.quarterLabel ? `<span class="quarter">${esc(entry.quarterLabel)}</span>` : ''}
        ${entry.irDate       ? `<span class="ir-date">${esc(entry.irDate)}</span>`       : ''}
      </span>
      <span class="entry-srt">${srtBadges}</span>
      <span class="entry-pdfs">${pdfLinks}</span>
      <span class="entry-dur">
        ${entry.durationSec ? `${ICON_CLOCK} ${fmtDuration(entry.durationSec)}` : ''}
      </span>
    </div>
  `
}

// ── 公司分組 view ─────────────────────────────────────────────────────────────

function renderGroupedByCompany(entries: AudioEntry[]): string {
  const groups = new Map<string, AudioEntry[]>()
  for (const e of entries) {
    if (!groups.has(e.id)) groups.set(e.id, [])
    groups.get(e.id)!.push(e)
  }

  let html = ''
  for (const [id, group] of groups) {
    const first = group[0]
    const name = first.companyName !== id ? `${first.companyName} ${id}` : id
    html += `
      <details class="company-group" open>
        <summary class="company-header">
          <span class="company-name">${esc(name)}</span>
          <span class="company-desc">${esc(first.businessDesc)}</span>
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
    const key = e.irDate || e.quarterLabel || '日期未知'
    if (!groups.has(key)) groups.set(key, [])
    groups.get(key)!.push(e)
  }

  const sortedKeys = [...groups.keys()].sort((a, b) => b.localeCompare(a))

  let html = ''
  for (const date of sortedKeys) {
    const group = groups.get(date)!
    html += `
      <details class="date-group" open>
        <summary class="date-header">${esc(date)}</summary>
        <div class="date-entries">
          ${group.map(e => `
            <div class="date-entry-row">
              <span class="date-company-name">
                ${esc(e.companyName !== e.id ? `${e.companyName} ${e.id}` : e.id)}
              </span>
              ${entryRowHtml(e)}
            </div>
          `).join('')}
        </div>
      </details>
    `
  }
  return html
}

// ── 全文搜尋 view ─────────────────────────────────────────────────────────────

function renderSearchView(container: HTMLElement): void {
  container.innerHTML = `
    <div class="search-bar">
      <input id="search-input" type="search" placeholder="搜尋逐字稿關鍵字…" autofocus>
    </div>
    <div id="search-results"></div>
  `

  const input = document.getElementById('search-input') as HTMLInputElement
  let debounceTimer = 0
  input.addEventListener('input', () => {
    clearTimeout(debounceTimer)
    debounceTimer = window.setTimeout(() => {
      const q = input.value.trim()
      if (q.length < 2) {
        document.getElementById('search-results')!.innerHTML = ''
        return
      }
      runSearch(q)
    }, 300)
  })
}

function runSearch(query: string): void {
  const resultsEl = document.getElementById('search-results')!

  const entries = filteredEntries()
  const srtUrls: { entry: AudioEntry; srt: { url: string; badge: string } }[] = []
  for (const entry of entries) {
    for (const srt of entry.srts) srtUrls.push({ entry, srt })
  }

  if (srtUrls.length === 0) {
    resultsEl.innerHTML = '<p class="empty">沒有可搜尋的字幕檔。</p>'
    return
  }

  const matches: { entry: AudioEntry; badge: string; lines: string[] }[] = []
  let pending = srtUrls.length
  let completed = 0

  resultsEl.innerHTML = `<p class="loading">搜尋中 (0/${srtUrls.length})…</p>`

  for (const { entry, srt } of srtUrls) {
    fetch(srt.url)
      .then(r => r.text())
      .then(text => {
        const q = query.toLowerCase()
        const lines = text.split('\n').filter(l => l.toLowerCase().includes(q))
        if (lines.length > 0) {
          matches.push({ entry, badge: srt.badge, lines })
          renderSearchResults(resultsEl, matches, query, completed, srtUrls.length)
        }
      })
      .catch(() => {})
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
  const progress = completed < total
    ? `<p class="loading">搜尋中 (${completed}/${total})…</p>`
    : ''

  if (matches.length === 0) {
    container.innerHTML = progress + (completed === total ? '<p class="empty">無符合結果。</p>' : '')
    return
  }

  const hl = (text: string) => {
    const re = new RegExp(query.replace(/[.*+?^${}()|[\]\\]/g, '\\$&'), 'gi')
    return text.replace(re, m => `<mark>${m}</mark>`)
  }

  const rows = matches.map(({ entry, badge, lines }) => `
    <div class="search-match"
         data-id="${escAttr(entry.id)}"
         data-quarter="${escAttr(entry.quarterLabel)}">
      <div class="match-header">
        <span class="company-name">${esc(entry.companyName !== entry.id ? `${entry.companyName} ${entry.id}` : entry.id)}</span>
        <span class="quarter">${esc(entry.quarterLabel)}</span>
        <span class="badge badge-${badge.toLowerCase()}">${esc(badge)}</span>
      </div>
      <ul class="match-lines">
        ${lines.slice(0, 5).map(l => `<li>${hl(esc(l))}</li>`).join('')}
        ${lines.length > 5 ? `<li class="more">…還有 ${lines.length - 5} 行</li>` : ''}
      </ul>
    </div>
  `).join('')

  container.innerHTML = progress + rows
}
