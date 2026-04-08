import type { AudioEntry } from '../types'
import { parseSrt, fmtTime, type SrtCue } from './srt'
import { diffWords, renderSpansHtml } from './diff'

const esc = (s: string) =>
  s.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;')
const escAttr = (s: string) => esc(s).replace(/"/g, '&quot;')

/**
 * Length of the longest common substring shared by a and b.
 * Much more precise than character-overlap for alignment: it requires characters
 * to appear *consecutively* in both strings, so "年成長也是24%" correctly matches
 * the GT cue containing "年成長也是24%" rather than one that merely shares the
 * same individual characters in a different order/context.
 */
function longestCommonSubstringLen(a: string, b: string): number {
  const m = a.length, n = b.length
  if (m === 0 || n === 0) return 0
  let maxLen = 0
  let prev = new Array(n + 1).fill(0)
  for (let i = 1; i <= m; i++) {
    const curr = new Array(n + 1).fill(0)
    for (let j = 1; j <= n; j++) {
      curr[j] = a[i - 1] === b[j - 1] ? prev[j - 1] + 1 : 0
      if (curr[j] > maxLen) maxLen = curr[j]
    }
    prev = curr
  }
  return maxLen
}

/**
 * Render the SRT player into `container`.
 * Returns a cleanup function to call before navigating away.
 */
export async function renderPlayerView(
  entry: AudioEntry,
  container: HTMLElement,
  onBack: () => void,
): Promise<() => void> {
  const hasBothSrts =
    entry.srts.some(s => s.badge === 'GT') && entry.srts.some(s => s.badge === 'FIN')

  const titleParts = [
    entry.companyName !== entry.id ? `${entry.companyName} ${entry.id}` : entry.id,
    entry.quarterLabel,
    entry.irDate,
  ].filter(Boolean)

  const pdfLinksHtml = entry.pdfs
    .map(p => `<a class="pdf-link" href="${escAttr(p.url)}" target="_blank" rel="noopener">📄 ${esc(p.label)} ↗</a>`)
    .join('')

  const controlsHtml = entry.audioUrl
    ? `<div class="audio-controls">
        <button class="play-pause-btn">▶ 播放</button>
        <button class="stop-btn">■ 停止</button>
        <select class="speed-select">
          <option value="0.75">0.75x</option>
          <option value="1" selected>1x</option>
          <option value="1.25">1.25x</option>
          <option value="1.5">1.5x</option>
          <option value="2">2x</option>
        </select>
        <span class="current-time">0:00</span>
      </div>`
    : `<div class="audio-controls no-audio">（無音訊檔）</div>`

  container.innerHTML = `
    <div class="player-page">
      <header class="player-header">
        <button class="back-btn">← 返回</button>
        <div class="player-meta">
          <div class="player-title">${esc(titleParts.join('  ·  '))}</div>
          ${entry.businessDesc ? `<div class="player-desc">${esc(entry.businessDesc)}</div>` : ''}
          <div class="player-links">
            ${pdfLinksHtml}
            ${hasBothSrts
              ? `<label class="diff-toggle-label">
                   <input type="checkbox" id="diff-mode" checked>
                   Diff 模式（GT <span class="badge badge-gt">GT</span> vs FIN <span class="badge badge-fin">FIN</span>）
                 </label>`
              : ''}
          </div>
        </div>
      </header>
      <div class="subtitle-window"><p class="loading">載入字幕中…</p></div>
      <footer class="player-footer">${controlsHtml}</footer>
    </div>
  `

  // ── back button ────────────────────────────────────────────────────────────
  container.querySelector('.back-btn')!.addEventListener('click', onBack)

  // ── audio setup ───────────────────────────────────────────────────────────
  let audio: HTMLAudioElement | null = null
  if (entry.audioUrl) {
    audio = new Audio(entry.audioUrl)
    const playPauseBtn = container.querySelector<HTMLButtonElement>('.play-pause-btn')!
    const stopBtn      = container.querySelector<HTMLButtonElement>('.stop-btn')!
    const speedSelect  = container.querySelector<HTMLSelectElement>('.speed-select')!
    const currentTimeEl = container.querySelector<HTMLElement>('.current-time')!

    playPauseBtn.addEventListener('click', () => {
      if (audio!.paused) {
        audio!.play().catch(err => {
          console.error('Audio play failed:', err)
          playPauseBtn.textContent = '▶ 播放（載入失敗）'
        })
      } else {
        audio!.pause()
      }
    })
    stopBtn.addEventListener('click', () => {
      audio!.pause()
      audio!.currentTime = 0
    })
    speedSelect.addEventListener('change', () => {
      audio!.playbackRate = parseFloat(speedSelect.value)
    })
    audio.addEventListener('play',  () => { playPauseBtn.textContent = '⏸ 暫停' })
    audio.addEventListener('pause', () => { playPauseBtn.textContent = '▶ 播放' })
    audio.addEventListener('ended', () => { playPauseBtn.textContent = '▶ 播放' })
    audio.addEventListener('timeupdate', () => {
      currentTimeEl.textContent = fmtTime(audio!.currentTime, false)
    })
  }

  // ── fetch SRTs ─────────────────────────────────────────────────────────────
  const gtSrt  = entry.srts.find(s => s.badge === 'GT')
  const finSrt = entry.srts.find(s => s.badge === 'FIN')

  let gtCues:  SrtCue[] = []
  let finCues: SrtCue[] = []

  const [gtResult, finResult] = await Promise.allSettled([
    gtSrt  ? fetch(gtSrt.url).then(r => r.text())  : Promise.resolve(''),
    finSrt ? fetch(finSrt.url).then(r => r.text()) : Promise.resolve(''),
  ])
  
  if (gtResult.status === 'fulfilled' && gtResult.value) {
    gtCues = parseSrt(gtResult.value)
  } else if (gtResult.status === 'rejected') {
    console.error('Failed to fetch GT SRT:', gtResult.reason)
  }

  if (finResult.status === 'fulfilled' && finResult.value) {
    finCues = parseSrt(finResult.value)
  } else if (finResult.status === 'rejected') {
    console.error('Failed to fetch FIN SRT:', finResult.reason)
  }

  const hasAnySrt = gtCues.length > 0 || finCues.length > 0
  const subtitleWindow = container.querySelector<HTMLElement>('.subtitle-window')!

  if (!hasAnySrt) {
    subtitleWindow.innerHTML = '<p class="empty">尚無字幕檔。</p>'
    return () => { audio?.pause() }
  }

  let diffMode = hasBothSrts

  // ── diff toggle ───────────────────────────────────────────────────────────
  container.querySelector<HTMLInputElement>('#diff-mode')
    ?.addEventListener('change', e => {
      diffMode = (e.target as HTMLInputElement).checked
      renderSubtitles()
    })

  // ── subtitle render ───────────────────────────────────────────────────────
  function renderSubtitles() {
    // If not in diff mode, or if we only have one SRT, just show the primary one
    if (!diffMode || gtCues.length === 0 || finCues.length === 0) {
      const primary = gtCues.length > 0 ? gtCues : finCues
      subtitleWindow.innerHTML = primary.map(cue => `
        <div class="cue" id="cue-${cue.index}" data-start="${cue.startSec}">
          <span class="cue-time">[${fmtTime(cue.startSec, true)}]</span>
          <span class="cue-text">${esc(cue.text)}</span>
        </div>
      `).join('')
      return
    }

    // DIFF MODE: GT-anchored alignment
    // Key by GT array index (not startSec) so multiple GT cues sharing the same
    // timestamp don't collide in the map. Within a ±30s window, prefer the GT cue
    // whose text has the longest common substring with the FIN cue text.
    const finByGt = new Map<number, string>() // GT index → concatenated FIN text
    for (let gi = 0; gi < gtCues.length; gi++) finByGt.set(gi, '')

    for (const finCue of finCues) {
      const WINDOW = 30
      const pool = gtCues
        .map((gt, gi) => ({ gt, gi, dist: Math.abs(gt.startSec - finCue.startSec) }))
        .filter(e => e.dist <= WINDOW)
      const candidates = pool.length > 0
        ? pool
        : [gtCues.reduce<{ gt: typeof gtCues[0]; gi: number; dist: number }>(
            (b, gt, gi) => {
              const d = Math.abs(gt.startSec - finCue.startSec)
              return d < b.dist ? { gt, gi, dist: d } : b
            },
            { gt: gtCues[0], gi: 0, dist: Infinity }
          )]

      let bestGi   = candidates[0].gi
      let bestSim  = longestCommonSubstringLen(finCue.text, candidates[0].gt.text)
      let bestDist = candidates[0].dist
      for (const { gt, gi, dist } of candidates.slice(1)) {
        const sim = longestCommonSubstringLen(finCue.text, gt.text)
        if (sim > bestSim || (sim === bestSim && dist < bestDist)) {
          bestSim = sim; bestDist = dist; bestGi = gi
        }
      }
      const prev = finByGt.get(bestGi) ?? ''
      finByGt.set(bestGi, prev ? prev + ' ' + finCue.text : finCue.text)
    }

    subtitleWindow.innerHTML = gtCues.map((gtCue, i) => {
      const finText = finByGt.get(i) ?? ''
      let displayHtml: string
      if (!finText) {
        displayHtml = renderSpansHtml([{ text: gtCue.text, type: 'gt' }])
      } else {
        const spans = diffWords(gtCue.text, finText)
        displayHtml = renderSpansHtml(spans)
      }
      return `<div class="cue" id="cue-d-${i}" data-start="${gtCue.startSec}">
        <span class="cue-time">[${fmtTime(gtCue.startSec, true)}]</span>
        <span class="cue-text">${displayHtml}</span>
      </div>`
    }).join('')
  }

  renderSubtitles()

  // ── click to seek ─────────────────────────────────────────────────────────
  function onCueClick(e: MouseEvent) {
    if (!audio) return
    const cueEl = (e.target as HTMLElement).closest<HTMLElement>('.cue')
    if (!cueEl) return
    audio.currentTime = parseFloat(cueEl.dataset['start'] ?? '0')
    if (audio.paused) audio.play()
  }
  subtitleWindow.addEventListener('click', onCueClick)

  // ── audio ↔ subtitle sync ──────────────────────────────────────────────────
  let activeCueEl: HTMLElement | null = null

  function onTimeUpdate() {
    const t = audio!.currentTime
    
    // In diff mode, we need to search our synthesized union timestamps
    let activeId = ''
    if (diffMode && gtCues.length > 0 && finCues.length > 0) {
      let index = -1
      for (let i = 0; i < gtCues.length; i++) {
        if (t >= gtCues[i].startSec) index = i
        else break
      }
      if (index !== -1) activeId = `cue-d-${index}`
    } else {
      const primary = gtCues.length > 0 ? gtCues : finCues
      const active = primary.find(c => t >= c.startSec && t <= c.endSec)
      if (active) activeId = `cue-${active.index}`
    }

    const newEl = activeId ? document.getElementById(activeId) : null
    if (newEl === activeCueEl) return
    activeCueEl?.classList.remove('cue-active')
    activeCueEl = newEl
    if (newEl) {
      newEl.classList.add('cue-active')
      newEl.scrollIntoView({ behavior: 'smooth', block: 'nearest' })
    }
  }

  audio?.addEventListener('timeupdate', onTimeUpdate)

  // ── cleanup ────────────────────────────────────────────────────────────────
  return () => {
    audio?.pause()
    audio?.removeEventListener('timeupdate', onTimeUpdate)
    subtitleWindow.removeEventListener('click', onCueClick)
  }
}
