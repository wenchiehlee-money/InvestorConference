import type { AudioEntry } from '../types'
import { parseSrt, fmtTime, type SrtCue } from './srt'
import { diffWords, renderSpansHtml } from './diff'
import * as pdfjsLib from 'pdfjs-dist'
import pdfjsWorker from 'pdfjs-dist/build/pdf.worker.min.mjs?url'
pdfjsLib.GlobalWorkerOptions.workerSrc = pdfjsWorker

const esc = (s: string) =>
  s.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;')
const escAttr = (s: string) => esc(s).replace(/"/g, '&quot;')

/**
 * Alignment similarity between a FIN cue and a GT cue.
 * Only the first len(gtText) characters of finText are compared; this ensures
 * that when a FIN cue has merged multiple GT segments into one, it aligns to
 * the GT cue matching its *beginning* rather than one matching a later portion.
 */
function alignSim(finText: string, gtText: string): number {
  return longestCommonSubstringLen(finText.slice(0, gtText.length), gtText)
}

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

  const hasPdfs = entry.pdfs.length > 0
  const primaryPdf = entry.pdfs.find(p => p.label === 'ir') ?? entry.pdfs[0]

  const pdfLinksHtml = entry.pdfs
    .map(p => `<a class="pdf-link" href="${escAttr(p.url)}" target="_blank" rel="noopener">📄 ${esc(p.label)} ↗</a>`)
    .join('')

  const pdfTabsHtml = entry.pdfs
    .map((p, i) => `<button class="pdf-tab${i === 0 ? ' active' : ''}" data-raw-url="${escAttr(p.url)}">${esc(p.label)}</button>`)
    .join('')

  const pdfPanelHtml = hasPdfs
    ? `<div class="pdf-panel" id="pdf-panel">
        <div class="pdf-panel-header">
          <button class="pdf-toggle-btn" title="隱藏簡報">‹</button>
          <div class="pdf-tabs">${pdfTabsHtml}</div>
          <a class="pdf-open-link" href="${escAttr(primaryPdf.url)}" target="_blank" rel="noopener" title="在新分頁開啟">↗</a>
        </div>
        <div class="pdf-canvas-wrap" id="pdf-canvas-wrap">
          <canvas id="pdf-canvas"></canvas>
        </div>
        <div class="pdf-panel-footer">
          <button class="pdf-nav-btn" id="pdf-prev" title="上一頁">&#8249;</button>
          <span class="pdf-page-info">
            <select id="pdf-page-select" class="pdf-page-select" title="選擇頁碼">
              <option value="1">1</option>
            </select>
            <span class="pdf-page-sep">/</span>
            <span id="pdf-page-total">?</span>
          </span>
          <button class="pdf-nav-btn" id="pdf-next" title="下一頁">&#8250;</button>
        </div>
      </div>`
    : ''

  const controlsHtml = entry.audioUrl
    ? `<div class="audio-controls">
        ${hasPdfs ? `<button class="pdf-show-btn" id="pdf-show-btn" style="display:none" title="顯示簡報">📄</button>` : ''}
        <button class="ctrl-btn play-pause-btn" title="播放/暫停">
          <svg class="ctrl-icon" viewBox="0 0 24 24"><path d="M5 3l14 9-14 9V3z"/></svg>
        </button>
        <button class="ctrl-btn mute-btn" title="靜音">
          <svg class="ctrl-icon mute-icon" viewBox="0 0 24 24">
            <path d="M11 5L6 9H2v6h4l5 4V5z"/>
            <path class="volume-wave" d="M15.54 8.46a5 5 0 0 1 0 7.07"/>
            <path class="mute-x" d="M23 9l-6 6m0-6l6 6"/>
          </svg>
        </button>
        <input type="range" class="volume-slider" min="0" max="1" step="0.05" value="1" title="音量">
        <div class="progress-wrap">
          <input type="range" class="progress-bar" min="0" max="100" step="0.1" value="0">
        </div>
        <span class="time-display"><span class="current-time">0:00</span><span class="time-sep"> / </span><span class="total-time">--:--</span></span>
        <select class="speed-select">
          <option value="0.75">0.75x</option>
          <option value="1" selected>1x</option>
          <option value="1.25">1.25x</option>
          <option value="1.5">1.5x</option>
          <option value="2">2x</option>
        </select>
      </div>`
    : `<div class="audio-controls no-audio">
        ${hasPdfs ? `<button class="pdf-show-btn" id="pdf-show-btn" style="display:none" title="顯示簡報">📄</button>` : ''}
        （無音訊檔）
      </div>`

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
              ? `<div class="mode-selector">
                   <label title="僅顯示 Ground Truth 字幕"><input type="radio" name="play-mode" value="GT"> GT</label>
                   <label title="僅顯示轉錄最終版本"><input type="radio" name="play-mode" value="FIN"> FIN</label>
                   <label title="比對 GT 與 FIN 的差異"><input type="radio" name="play-mode" value="DIFF" checked> Diff</label>
                 </div>`
              : ''}
          </div>
        </div>
      </header>
      <div class="player-body">
        <div class="transcript-panel">
          <div class="subtitle-window"><p class="loading">載入字幕中…</p></div>
          <div class="player-footer">${controlsHtml}</div>
        </div>
        ${pdfPanelHtml}
      </div>
    </div>
  `

  // ── back button ────────────────────────────────────────────────────────────
  container.querySelector('.back-btn')!.addEventListener('click', onBack)

  // ── PDF panel (PDF.js canvas renderer) ───────────────────────────────────
  if (hasPdfs) {
    const pdfPanel    = container.querySelector<HTMLElement>('#pdf-panel')!
    const canvasEl    = container.querySelector<HTMLCanvasElement>('#pdf-canvas')!
    const canvasWrap  = container.querySelector<HTMLElement>('#pdf-canvas-wrap')!
    const toggleBtn   = container.querySelector<HTMLButtonElement>('.pdf-toggle-btn')!
    const showBtn     = container.querySelector<HTMLButtonElement>('#pdf-show-btn')
    const openLink    = container.querySelector<HTMLAnchorElement>('.pdf-open-link')
    const prevBtn      = container.querySelector<HTMLButtonElement>('#pdf-prev')!
    const nextBtn      = container.querySelector<HTMLButtonElement>('#pdf-next')!
    const pageSelectEl = container.querySelector<HTMLSelectElement>('#pdf-page-select')!
    const pageTotalEl  = container.querySelector<HTMLElement>('#pdf-page-total')!

    let pdfDoc: import('pdfjs-dist').PDFDocumentProxy | null = null
    let currentPage = 1
    let totalPages = 0
    let renderTask: import('pdfjs-dist').RenderTask | null = null

    async function renderPage(pageNum: number) {
      if (!pdfDoc) return
      if (renderTask) { renderTask.cancel(); renderTask = null }
      const page = await pdfDoc.getPage(pageNum)
      const dpr = window.devicePixelRatio || 1
      const wrapWidth = canvasWrap.clientWidth - 16
      const baseVP = page.getViewport({ scale: 1 })
      const cssScale = Math.max(0.5, Math.min(wrapWidth / baseVP.width, 2.5))
      const renderScale = cssScale * dpr
      const vp = page.getViewport({ scale: renderScale })
      canvasEl.width  = vp.width
      canvasEl.height = vp.height
      canvasEl.style.width  = `${Math.round(vp.width / dpr)}px`
      canvasEl.style.height = `${Math.round(vp.height / dpr)}px`
      const ctx = canvasEl.getContext('2d')!
      renderTask = page.render({ canvasContext: ctx, canvas: canvasEl, viewport: vp })
      try { await renderTask.promise } catch { /* cancelled */ }
      currentPage = pageNum
      pageSelectEl.value = String(pageNum)
      prevBtn.disabled = pageNum <= 1
      nextBtn.disabled = pageNum >= totalPages
    }

    async function loadPdf(url: string) {
      pdfDoc = null
      pageSelectEl.innerHTML = '<option>…</option>'
      pageTotalEl.textContent = '?'
      const ctx = canvasEl.getContext('2d')!
      ctx.clearRect(0, 0, canvasEl.width, canvasEl.height)
      try {
        pdfDoc = await pdfjsLib.getDocument({ url, withCredentials: false }).promise
        totalPages = pdfDoc.numPages
        pageTotalEl.textContent = String(totalPages)
        // Populate select options
        pageSelectEl.innerHTML = Array.from({ length: totalPages }, (_, i) =>
          `<option value="${i + 1}">${i + 1}</option>`
        ).join('')
        await renderPage(1)
      } catch (e) {
        console.error('PDF load error:', e)
        pageSelectEl.innerHTML = '<option>!</option>'
      }
    }

    prevBtn.addEventListener('click', () => { if (currentPage > 1) renderPage(currentPage - 1) })
    nextBtn.addEventListener('click', () => { if (currentPage < totalPages) renderPage(currentPage + 1) })

    pageSelectEl.addEventListener('change', () => {
      const n = parseInt(pageSelectEl.value, 10)
      if (!isNaN(n)) renderPage(n)
    })


    toggleBtn.addEventListener('click', () => {
      pdfPanel.classList.add('hidden')
      if (showBtn) showBtn.style.display = ''
    })
    showBtn?.addEventListener('click', () => {
      pdfPanel.classList.remove('hidden')
      showBtn.style.display = 'none'
    })

    // PDF tab switching
    container.querySelectorAll<HTMLButtonElement>('.pdf-tab').forEach(tab => {
      tab.addEventListener('click', () => {
        container.querySelectorAll('.pdf-tab').forEach(t => t.classList.remove('active'))
        tab.classList.add('active')
        const rawUrl = tab.dataset['rawUrl'] ?? ''
        if (openLink) openLink.href = rawUrl
        loadPdf(rawUrl)
      })
    })

    // Load initial PDF
    loadPdf(primaryPdf.url)
  }

  // ── audio setup ───────────────────────────────────────────────────────────
  const PLAY_ICON = `<svg class="ctrl-icon" viewBox="0 0 24 24"><path d="M5 3l14 9-14 9V3z"/></svg>`
  const PAUSE_ICON = `<svg class="ctrl-icon" viewBox="0 0 24 24"><rect x="6" y="4" width="4" height="16"/><rect x="14" y="4" width="4" height="16"/></svg>`

  let audio: HTMLAudioElement | null = null
  if (entry.audioUrl) {
    audio = new Audio()
    audio.preload = 'metadata'
    // Use <source> with explicit MIME type so iOS doesn't reject application/octet-stream
    const src = document.createElement('source')
    src.src = entry.audioUrl
    const ext = entry.audioUrl.split('?')[0].split('.').pop()?.toLowerCase()
    if (ext === 'm4a' || ext === 'mp4') src.type = 'audio/mp4'
    else if (ext === 'mp3')             src.type = 'audio/mpeg'
    else if (ext === 'wav')             src.type = 'audio/wav'
    audio.appendChild(src)
    audio.load()
    const playPauseBtn  = container.querySelector<HTMLButtonElement>('.play-pause-btn')!
    const muteBtn       = container.querySelector<HTMLButtonElement>('.mute-btn')!
    const volumeSlider  = container.querySelector<HTMLInputElement>('.volume-slider')!
    const progressBar   = container.querySelector<HTMLInputElement>('.progress-bar')!
    const speedSelect   = container.querySelector<HTMLSelectElement>('.speed-select')!
    const currentTimeEl = container.querySelector<HTMLElement>('.current-time')!
    const totalTimeEl   = container.querySelector<HTMLElement>('.total-time')!

    // Show pre-computed duration immediately (iOS ignores preload before user gesture)
    if (entry.durationSec) totalTimeEl.textContent = fmtTime(entry.durationSec, false)

    // Play / Pause — touchend for iOS (fires before click, avoids 300ms delay + gesture recognition)
    const togglePlay = () => {
      if (audio!.paused) audio!.play().catch(err => { console.error('play failed:', err) })
      else audio!.pause()
    }
    playPauseBtn.addEventListener('click', togglePlay)
    playPauseBtn.addEventListener('touchend', (e) => { e.preventDefault(); togglePlay() })

    // Show audio load errors visibly (code: 1=aborted 2=network 3=decode 4=unsupported)
    audio.addEventListener('error', () => {
      const code = audio!.error?.code ?? '?'
      totalTimeEl.textContent = `err${code}`
      console.error('audio error', code, audio!.error?.message, entry.audioUrl)
    })

    // Mute
    muteBtn.addEventListener('click', () => {
      audio!.muted = !audio!.muted
      muteBtn.classList.toggle('muted', audio!.muted)
    })

    // Volume
    volumeSlider.addEventListener('input', () => {
      audio!.volume = parseFloat(volumeSlider.value)
      audio!.muted = false
      muteBtn.classList.remove('muted')
    })

    // Seek
    let isSeeking = false
    progressBar.addEventListener('mousedown', () => { isSeeking = true })
    progressBar.addEventListener('mouseup',   () => {
      isSeeking = false
      if (audio!.duration) audio!.currentTime = (parseFloat(progressBar.value) / 100) * audio!.duration
    })
    progressBar.addEventListener('input', () => {
      if (audio!.duration) audio!.currentTime = (parseFloat(progressBar.value) / 100) * audio!.duration
    })

    // Speed
    speedSelect.addEventListener('change', () => {
      audio!.playbackRate = parseFloat(speedSelect.value)
    })

    // State → UI
    audio.addEventListener('play',  () => { playPauseBtn.innerHTML = PAUSE_ICON })
    audio.addEventListener('pause', () => { playPauseBtn.innerHTML = PLAY_ICON })
    audio.addEventListener('ended', () => { playPauseBtn.innerHTML = PLAY_ICON })
    audio.addEventListener('loadedmetadata', () => {
      totalTimeEl.textContent = fmtTime(audio!.duration, false)
    })
    audio.addEventListener('timeupdate', () => {
      currentTimeEl.textContent = fmtTime(audio!.currentTime, false)
      if (!isSeeking && audio!.duration) {
        progressBar.value = String((audio!.currentTime / audio!.duration) * 100)
      }
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

  let playerMode: 'GT' | 'FIN' | 'DIFF' = hasBothSrts ? 'DIFF' : (gtCues.length > 0 ? 'GT' : 'FIN')

  // ── mode selector ────────────────────────────────────────────────────────
  container.querySelectorAll<HTMLInputElement>('input[name="play-mode"]').forEach(input => {
    input.addEventListener('change', e => {
      playerMode = (e.target as HTMLInputElement).value as any
      renderSubtitles()
    })
  })

  // ── subtitle render ───────────────────────────────────────────────────────
  function renderSubtitles() {
    // 1. GT Only Mode
    if (playerMode === 'GT') {
      subtitleWindow.innerHTML = gtCues.map(cue => `
        <div class="cue" id="cue-${cue.index}" data-start="${cue.startSec}">
          <span class="cue-time">[${fmtTime(cue.startSec, true)}]</span>
          <span class="badge badge-gt">GT</span>
          <span class="cue-text">${esc(cue.text)}</span>
        </div>
      `).join('')
      return
    }

    // 2. FIN Only Mode
    if (playerMode === 'FIN') {
      subtitleWindow.innerHTML = finCues.map(cue => `
        <div class="cue" id="cue-${cue.index}" data-start="${cue.startSec}">
          <span class="cue-time">[${fmtTime(cue.startSec, true)}]</span>
          <span class="badge badge-fin">FIN</span>
          <span class="cue-text">${esc(cue.text)}</span>
        </div>
      `).join('')
      return
    }

    // 3. DIFF MODE (GT-anchored alignment)
    if (playerMode === 'DIFF') {
      if (gtCues.length === 0 || finCues.length === 0) {
        playerMode = gtCues.length > 0 ? 'GT' : 'FIN'
        renderSubtitles()
        return
      }
    // Use Disjoint Set Union (DSU) to group GT cues that are linked by shared FIN cues.
    const parent = new Array(gtCues.length).fill(0).map((_, i) => i)
    function find(i: number): number {
      let r = i
      while (parent[r] !== r) r = parent[r]
      while (parent[i] !== r) { const p = parent[i]; parent[i] = r; i = p }
      return r
    }
    function union(i: number, j: number) {
      const rootI = find(i); const rootJ = find(j)
      if (rootI !== rootJ) parent[rootI] = rootJ
    }

    const norm = (s: string) => s.replace(/\s+/g, '').replace(/[，,、。.!！?？；;：:""''「」（）()【】\[\]—–\-…·～~]/g, '')
    const giToFis = new Map<number, Set<number>>()
    for (let gi = 0; gi < gtCues.length; gi++) giToFis.set(gi, new Set())

    for (let fi = 0; fi < finCues.length; fi++) {
      const finCue = finCues[fi]
      const finNorm = norm(finCue.text)
      if (!finNorm) continue

      const WINDOW = 30
      const candidates = gtCues
        .map((gt, gi) => ({ gt, gi, dist: Math.abs(gt.startSec - finCue.startSec) }))
        .filter(e => e.dist <= WINDOW)
      
      if (candidates.length === 0) continue

      // Primary selection: alignSim trims finText to len(GT) before LCS,
      // so a FIN cue that merges multiple GT segments matches the GT whose
      // text appears at the *start* of the FIN cue, not the longest overall match.
      let best = candidates[0]
      let bestSim = alignSim(finNorm, norm(best.gt.text))
      for (const cand of candidates.slice(1)) {
        const sim = alignSim(finNorm, norm(cand.gt.text))
        if (sim > bestSim || (sim === bestSim && cand.dist < best.dist)) {
          bestSim = sim; best = cand
        }
      }

      const coveredGis = [best.gi]
      for (const cand of candidates) {
        if (cand.gi === best.gi) continue
        const gtNorm = norm(cand.gt.text)
        const sim = longestCommonSubstringLen(finNorm, gtNorm)
        // Only link if FIN covers a substantial fraction of the GT cue AND enough chars
        if (sim >= gtNorm.length * 0.6 && sim >= 6) {
          coveredGis.push(cand.gi)
        }
      }

      for (const gi of coveredGis) {
        giToFis.get(gi)!.add(fi)
        union(coveredGis[0], gi)
      }
    }

    const giToGroupId = new Map<number, number>()
    const groupHtml: string[] = []
    const processedGis = new Set<number>()

    for (let i = 0; i < gtCues.length; i++) {
      if (processedGis.has(i)) continue
      
      const startI = i
      const root = find(i)
      // Group consecutive cues belonging to the same component
      while (i + 1 < gtCues.length && find(i + 1) === root) {
        i++
      }
      const endI = i

      const groupGtText = gtCues.slice(startI, endI + 1).map(c => c.text).join('')
      const finIdSet = new Set<number>()
      for (let k = startI; k <= endI; k++) {
        giToGroupId.set(k, startI)
        processedGis.add(k)
        for (const fi of giToFis.get(k)!) finIdSet.add(fi)
      }

      const groupFinText = Array.from(finIdSet)
        .sort((a, b) => finCues[a].startSec - finCues[b].startSec)
        .map(fid => finCues[fid].text)
        .join(' ')

      let displayHtml: string
      if (!groupFinText) {
        displayHtml = renderSpansHtml([{ text: groupGtText, type: 'gt' }])
      } else {
        displayHtml = renderSpansHtml(diffWords(groupGtText, groupFinText))
      }

      groupHtml.push(`
        <div class="cue" id="cue-d-${startI}" data-start="${gtCues[startI].startSec}">
          <span class="cue-time">[${fmtTime(gtCues[startI].startSec, true)}]</span>
          <span class="cue-text">${displayHtml}</span>
        </div>
      `)
    }

    subtitleWindow.innerHTML = groupHtml.join('')
    ;(subtitleWindow as any)._giToGroupId = giToGroupId
  }

  renderSubtitles()

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
    if (!audio) return
    const t = audio.currentTime
    
    // In DIFF mode, we use the mapping to find the merged cue
    let activeId = ''
    if (playerMode === 'DIFF' && gtCues.length > 0 && finCues.length > 0) {
      let index = -1
      for (let i = 0; i < gtCues.length; i++) {
        if (t >= gtCues[i].startSec) index = i
        else break
      }
      if (index !== -1) {
        const groupId = ((subtitleWindow as any)._giToGroupId as Map<number, number>)?.get(index)
        activeId = `cue-d-${groupId ?? index}`
      }
    } else {
      const primary = playerMode === 'GT' ? gtCues : finCues
      // If the selected mode is missing its cues, use whatever is available
      const cuesToUse = primary.length > 0 ? primary : (gtCues.length > 0 ? gtCues : finCues)
      
      const active = cuesToUse.find(c => t >= c.startSec && t <= c.endSec)
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
