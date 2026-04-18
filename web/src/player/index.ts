import type { AudioEntry } from '../types'
import { parseSrt, fmtTime, type SrtCue } from './srt'
import { diffWords, renderSpansHtml } from './diff'
import * as pdfjsLib from 'pdfjs-dist'
import pdfjsWorker from 'pdfjs-dist/build/pdf.worker.min.mjs?url'
pdfjsLib.GlobalWorkerOptions.workerSrc = pdfjsWorker

const esc = (s: string) =>
  s.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;')
const escAttr = (s: string) => esc(s).replace(/"/g, '&quot;')

function alignSim(finText: string, gtText: string): number {
  if (!finText || !gtText) return 0
  const shortFin = finText.slice(0, gtText.length + 10)
  return longestCommonSubstringLen(shortFin, gtText)
}

function longestCommonSubstringLen(a: string, b: string): number {
  const m = a.length, n = b.length
  if (m === 0 || n === 0) return 0
  if (m > 500 || n > 500) return 0 
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

  const pdfTabsHtml = entry.pdfs
    .map((p, i) => `<button class="pdf-tab${i === 0 ? ' active' : ''}" data-raw-url="${escAttr(p.url)}">${esc(p.label)}</button>`)
    .join('')

  const controlsHtml = entry.audioUrl
    ? `<div class="audio-controls">
        ${hasPdfs ? `<button class="pdf-show-btn" id="pdf-show-btn" style="display:none" title="顯示簡報"><svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/></svg>簡報</button>` : ''}
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
        ${hasPdfs ? `<button class="pdf-show-btn" id="pdf-show-btn" style="display:none" title="顯示簡報"><svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/></svg>簡報</button>` : ''}
        （無音訊檔）
      </div>`

  container.innerHTML = `
    <div class="player-page">
      <header class="player-header">
        <button class="back-btn" title="返回列表">
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><path d="m15 18-6-6 6-6"/></svg>
          返回
        </button>
        <div class="player-meta">
          <div class="player-title">${esc(titleParts.join('  ·  '))}</div>
          ${entry.businessDesc ? `<div class="player-desc">${esc(entry.businessDesc)}</div>` : ''}
          <div class="player-actions">
            ${hasBothSrts
              ? `<div class="mode-selector">
                   <input type="radio" name="play-mode" id="mode-gt" value="GT">
                   <label for="mode-gt"><span class="mode-dot mode-dot-gt"></span>GT</label>
                   <input type="radio" name="play-mode" id="mode-fin" value="FIN">
                   <label for="mode-fin"><span class="mode-dot mode-dot-fin"></span>FIN</label>
                   <input type="radio" name="play-mode" id="mode-diff" value="DIFF" checked>
                   <label for="mode-diff"><span class="mode-dot mode-dot-diff"></span>Diff</label>
                   <div class="mode-glider"></div>
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
        ${hasPdfs
          ? `<div class="pdf-panel" id="pdf-panel">
              <div class="pdf-panel-header">
                <div class="pdf-tabs">${pdfTabsHtml}</div>
                <div class="pdf-util-btns">
                  <a class="pdf-util-btn pdf-open-link" href="${escAttr(primaryPdf.url)}" target="_blank" rel="noopener" title="在新分頁開啟">
                    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M18 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h6"/><polyline points="15 3 21 3 21 9"/><line x1="10" y1="14" x2="21" y2="3"/></svg>
                  </a>
                  <button class="pdf-util-btn pdf-toggle-btn" title="隱藏簡報">
                    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M18 6 6 18"/><path d="m6 6 12 12"/></svg>
                  </button>
                </div>
              </div>
              <div class="pdf-canvas-wrap" id="pdf-canvas-wrap">
                <canvas id="pdf-canvas"></canvas>
              </div>
              <div class="pdf-panel-footer">
                <button class="pdf-nav-btn" id="pdf-prev" title="上一頁">
                  <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><path d="m15 18-6-6 6-6"/></svg>
                </button>
                <div class="pdf-page-indicator">
                  <select id="pdf-page-select" class="pdf-page-select"></select>
                  <span class="pdf-page-total">/ <span id="pdf-page-total">?</span></span>
                </div>
                <button class="pdf-nav-btn" id="pdf-next" title="下一頁">
                  <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><path d="m9 18 6-6-6-6"/></svg>
                </button>
              </div>
            </div>`
          : ''}
      </div>
    </div>
  `

  container.querySelector('.back-btn')!.addEventListener('click', onBack)

  if (hasPdfs) {
    const pdfPanel    = container.querySelector<HTMLElement>('#pdf-panel')!
    const canvasEl    = container.querySelector<HTMLCanvasElement>('#pdf-canvas')!
    const canvasWrap  = container.querySelector<HTMLElement>('#pdf-canvas-wrap')!
    const toggleBtn   = container.querySelector<HTMLButtonElement>('.pdf-toggle-btn')!
    const showBtn     = container.querySelector<HTMLButtonElement>('#pdf-show-btn')
    const prevBtn      = container.querySelector<HTMLButtonElement>('#pdf-prev')!
    const nextBtn      = container.querySelector<HTMLButtonElement>('#pdf-next')!
    const pageSelectEl = container.querySelector<HTMLSelectElement>('#pdf-page-select')!
    const pageTotalEl  = container.querySelector<HTMLElement>('#pdf-page-total')!

    let pdfDoc: any = null
    let currentPage = 1
    let totalPages = 0
    let renderTask: any = null

    async function renderPage(pageNum: number) {
      if (!pdfDoc) return
      if (renderTask) { renderTask.cancel(); renderTask = null }
      const page = await pdfDoc.getPage(pageNum)
      const dpr = window.devicePixelRatio || 1
      const wrapWidth = canvasWrap.clientWidth - 16
      const baseVP = page.getViewport({ scale: 1 })
      const cssScale = Math.max(0.5, Math.min(wrapWidth / baseVP.width, 2.5))
      const vp = page.getViewport({ scale: cssScale * dpr })
      canvasEl.width = vp.width; canvasEl.height = vp.height
      canvasEl.style.width = `${Math.round(vp.width / dpr)}px`; canvasEl.style.height = `${Math.round(vp.height / dpr)}px`
      const ctx = canvasEl.getContext('2d')!
      renderTask = page.render({ canvasContext: ctx, viewport: vp })
      try { await renderTask.promise } catch { }
      currentPage = pageNum; pageSelectEl.value = String(pageNum)
      prevBtn.disabled = pageNum <= 1; nextBtn.disabled = pageNum >= totalPages
    }

    async function loadPdf(url: string) {
      try {
        pdfDoc = await pdfjsLib.getDocument({ url, withCredentials: false }).promise
        totalPages = pdfDoc.numPages; pageTotalEl.textContent = String(totalPages)
        pageSelectEl.innerHTML = Array.from({ length: totalPages }, (_, i) => `<option value="${i+1}">${i+1}</option>`).join('')
        await renderPage(1)
      } catch (e) { console.error('PDF load error:', e) }
    }
    prevBtn.addEventListener('click', () => { if (currentPage > 1) renderPage(currentPage - 1) })
    nextBtn.addEventListener('click', () => { if (currentPage < totalPages) renderPage(currentPage + 1) })
    pageSelectEl.addEventListener('change', () => { const n = parseInt(pageSelectEl.value, 10); if (!isNaN(n)) renderPage(n) })
    toggleBtn.addEventListener('click', () => { pdfPanel.classList.add('hidden'); if (showBtn) showBtn.style.display = '' })
    showBtn?.addEventListener('click', () => { pdfPanel.classList.remove('hidden'); showBtn.style.display = 'none' })
    container.querySelectorAll<HTMLButtonElement>('.pdf-tab').forEach(tab => {
      tab.addEventListener('click', () => {
        container.querySelectorAll('.pdf-tab').forEach(t => t.classList.remove('active'))
        tab.classList.add('active'); loadPdf(tab.dataset['rawUrl'] ?? '')
      })
    })
    loadPdf(primaryPdf.url)
  }

  const PLAY_ICON = `<svg class="ctrl-icon" viewBox="0 0 24 24"><path d="M5 3l14 9-14 9V3z"/></svg>`
  const PAUSE_ICON = `<svg class="ctrl-icon" viewBox="0 0 24 24"><rect x="6" y="4" width="4" height="16"/><rect x="14" y="4" width="4" height="16"/></svg>`

  let audio: HTMLAudioElement | null = null
  if (entry.audioUrl) {
    audio = new Audio(); audio.preload = 'metadata'
    const src = document.createElement('source'); src.src = entry.audioUrl
    audio.appendChild(src); audio.load()
    const playPauseBtn  = container.querySelector<HTMLButtonElement>('.play-pause-btn')!
    const muteBtn       = container.querySelector<HTMLButtonElement>('.mute-btn')!
    const volumeSlider  = container.querySelector<HTMLInputElement>('.volume-slider')!
    const progressBar   = container.querySelector<HTMLInputElement>('.progress-bar')!
    const speedSelect   = container.querySelector<HTMLSelectElement>('.speed-select')!
    const currentTimeEl = container.querySelector<HTMLElement>('.current-time')!
    const totalTimeEl   = container.querySelector<HTMLElement>('.total-time')!
    if (entry.durationSec) totalTimeEl.textContent = fmtTime(entry.durationSec, false)
    playPauseBtn.addEventListener('click', () => audio!.paused ? audio!.play() : audio!.pause())
    muteBtn.addEventListener('click', () => { audio!.muted = !audio!.muted; muteBtn.classList.toggle('muted', audio!.muted) })
    volumeSlider.addEventListener('input', () => { audio!.volume = parseFloat(volumeSlider.value); audio!.muted = false })
    progressBar.addEventListener('input', () => { if (audio!.duration) audio!.currentTime = (parseFloat(progressBar.value) / 100) * audio!.duration })
    speedSelect.addEventListener('change', () => audio!.playbackRate = parseFloat(speedSelect.value))
    audio.addEventListener('play',  () => playPauseBtn.innerHTML = PAUSE_ICON)
    audio.addEventListener('pause', () => playPauseBtn.innerHTML = PLAY_ICON)
    audio.addEventListener('timeupdate', () => {
      currentTimeEl.textContent = fmtTime(audio!.currentTime, false)
      progressBar.value = String((audio!.currentTime / (audio!.duration || 1)) * 100)
    })
  }

  const gtSrt  = entry.srts.find(s => s.badge === 'GT')
  const finSrt = entry.srts.find(s => s.badge === 'FIN')
  let gtCues: SrtCue[] = [], finCues: SrtCue[] = []
  const [gtRes, finRes] = await Promise.allSettled([
    gtSrt ? fetch(gtSrt.url).then(r => r.text()) : Promise.resolve(''),
    finSrt ? fetch(finSrt.url).then(r => r.text()) : Promise.resolve('')
  ])
  if (gtRes.status === 'fulfilled' && gtRes.value) gtCues = parseSrt(gtRes.value)
  if (finRes.status === 'fulfilled' && finRes.value) finCues = parseSrt(finRes.value)

  const subtitleWindow = container.querySelector<HTMLElement>('.subtitle-window')!
  let playerMode: 'GT' | 'FIN' | 'DIFF' = hasBothSrts ? 'DIFF' : (gtCues.length > 0 ? 'GT' : 'FIN')

  function renderSubtitles() {
    if (playerMode === 'GT') {
      subtitleWindow.innerHTML = gtCues.map(c => `<div class="cue" id="cue-${c.index}" data-start="${c.startSec}">[${fmtTime(c.startSec, true)}] <span class="badge badge-gt">GT</span> ${esc(c.text)}</div>`).join('')
    } else if (playerMode === 'FIN') {
      subtitleWindow.innerHTML = finCues.map(c => `<div class="cue" id="cue-${c.index}" data-start="${c.startSec}">[${fmtTime(c.startSec, true)}] <span class="badge badge-fin">FIN</span> ${esc(c.text)}</div>`).join('')
    } else if (playerMode === 'DIFF' && gtCues.length && finCues.length) {
      const parent = new Array(gtCues.length).fill(0).map((_, i) => i)
      const find = (i: number): number => { while (parent[i] !== i) { parent[i] = parent[parent[i]]; i = parent[i] } return i }
      const union = (i: number, j: number) => { const rootI = find(i), rootJ = find(j); if (rootI !== rootJ) parent[rootI] = rootJ }
      const norm = (s: string) => s.replace(/\s+/g, '').replace(/[，,、。.!！?？；;：:""''「」（）()【】\[\]—–\-…·～~]/g, '')
      const giToFis = new Map<number, Set<number>>()
      for (let gi = 0; gi < gtCues.length; gi++) giToFis.set(gi, new Set())

      for (let fi = 0; fi < finCues.length; fi++) {
        const finCue = finCues[fi], finNorm = norm(finCue.text)
        if (!finNorm) continue
        const WINDOW = 30
        const candidates = gtCues.map((gt, gi) => ({ gt, gi, dist: Math.abs(gt.startSec - finCue.startSec) })).filter(e => e.dist <= WINDOW)
        if (!candidates.length) continue
        let best = candidates[0], bestSim = alignSim(finNorm, norm(best.gt.text))
        for (const cand of candidates.slice(1)) {
          const sim = alignSim(finNorm, norm(cand.gt.text))
          if (sim > bestSim) { bestSim = sim; best = cand }
        }
        giToFis.get(best.gi)!.add(fi); union(best.gi, best.gi)
      }

      const giToGroupId = new Map<number, number>(), groupHtml: string[] = [], processedGis = new Set<number>()
      for (let i = 0; i < gtCues.length; i++) {
        if (processedGis.has(i)) continue
        const startI = i, root = find(i)
        while (i + 1 < gtCues.length && find(i + 1) === root) i++
        const endI = i, groupGtText = gtCues.slice(startI, endI + 1).map(c => c.text).join('')
        const finIdSet = new Set<number>()
        for (let k = startI; k <= endI; k++) { giToGroupId.set(k, startI); processedGis.add(k); for (const fi of giToFis.get(k)!) finIdSet.add(fi) }
        const groupFinText = Array.from(finIdSet).sort((a, b) => finCues[a].startSec - finCues[b].startSec).map(fid => finCues[fid].text).join(' ')
        groupHtml.push(`<div class="cue" id="cue-d-${startI}" data-start="${gtCues[startI].startSec}">[${fmtTime(gtCues[startI].startSec, true)}] ${renderSpansHtml(diffWords(groupGtText, groupFinText))}</div>`)
      }
      subtitleWindow.innerHTML = groupHtml.join('')
      ;(subtitleWindow as any)._giToGroupId = giToGroupId
    }
  }

  container.querySelectorAll<HTMLInputElement>('input[name="play-mode"]').forEach(i => i.addEventListener('change', e => { playerMode = (e.target as any).value; renderSubtitles() }))
  renderSubtitles()

  subtitleWindow.addEventListener('click', e => {
    const cue = (e.target as HTMLElement).closest<HTMLElement>('.cue')
    if (cue && audio) { audio.currentTime = parseFloat(cue.dataset['start'] || '0'); audio.play() }
  })

  let activeCueEl: HTMLElement | null = null
  audio?.addEventListener('timeupdate', () => {
    const t = audio!.currentTime
    let activeId = ''
    if (playerMode === 'DIFF' && gtCues.length && finCues.length) {
      let idx = -1; for (let i = 0; i < gtCues.length; i++) { if (t >= gtCues[i].startSec) idx = i; else break }
      if (idx !== -1) { const gid = ((subtitleWindow as any)._giToGroupId as Map<number, number>)?.get(idx); activeId = `cue-d-${gid ?? idx}` }
    } else {
      const cues = (playerMode === 'GT' ? gtCues : finCues); const active = cues.find(c => t >= c.startSec && t <= c.endSec)
      if (active) activeId = `cue-${active.index}`
    }
    const newEl = activeId ? document.getElementById(activeId) : null
    if (newEl && newEl !== activeCueEl) {
      activeCueEl?.classList.remove('cue-active'); activeCueEl = newEl
      newEl.classList.add('cue-active'); newEl.scrollIntoView({ behavior: 'smooth', block: 'nearest' })
    }
  })

  return () => { audio?.pause() }
}
