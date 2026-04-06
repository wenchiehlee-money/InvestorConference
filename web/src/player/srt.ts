export interface SrtCue {
  index: number
  startSec: number
  endSec: number
  text: string
}

/**
 * Auto-detect format and parse.
 * Supports:
 *   - Turboscribe custom: `(MM:SS) text` per line  (MM can exceed 59)
 *   - Standard SRT: numbered blocks with `HH:MM:SS,mmm --> HH:MM:SS,mmm`
 */
export function parseSrt(raw: string): SrtCue[] {
  const normalized = raw.replace(/\r\n/g, '\n').replace(/^\uFEFF/, '').trim()
  const lines = normalized.split('\n')
  const turboscribeStart = lines.findIndex(line => /^\(\d+:\d+\)/.test(line.trim()))
  if (turboscribeStart !== -1) {
    return parseTurboscribe(lines.slice(turboscribeStart).join('\n'))
  }
  return parseStandardSrt(normalized)
}

// ── Turboscribe format ────────────────────────────────────────────────────────
// Each line: (MM:SS) text   where MM is total minutes (may exceed 59)

function parseTurboscribe(text: string): SrtCue[] {
  const cues: SrtCue[] = []

  for (const line of text.split('\n')) {
    const m = line.match(/^\((\d+):(\d+)\)\s*(.+)$/)
    if (!m) continue
    const startSec = parseInt(m[1], 10) * 60 + parseInt(m[2], 10)
    const lineText = m[3].trim()
    if (!lineText) continue
    cues.push({ index: cues.length + 1, startSec, endSec: 0, text: lineText })
  }

  // Derive endSec from next cue's startSec; last cue gets +5s
  for (let i = 0; i < cues.length - 1; i++) {
    cues[i].endSec = cues[i + 1].startSec
  }
  if (cues.length > 0) {
    const last = cues[cues.length - 1]
    last.endSec = last.startSec + 5
  }

  return cues
}

// ── Standard SRT format ───────────────────────────────────────────────────────

function parseStandardSrt(text: string): SrtCue[] {
  const blocks = text.split(/\n{2,}/)
  const cues: SrtCue[] = []

  for (const block of blocks) {
    const lines = block.trim().split('\n')
    if (lines.length < 3) continue

    const index = parseInt(lines[0], 10)
    if (isNaN(index)) continue

    const m = lines[1].match(
      /(\d+):(\d+):(\d+)[,.](\d+)\s*-->\s*(\d+):(\d+):(\d+)[,.](\d+)/
    )
    if (!m) continue

    const startSec = +m[1] * 3600 + +m[2] * 60 + +m[3] + +m[4] / 1000
    const endSec   = +m[5] * 3600 + +m[6] * 60 + +m[7] + +m[8] / 1000
    const lineText = lines.slice(2).join(' ').replace(/<[^>]+>/g, '')

    cues.push({ index, startSec, endSec, text: lineText })
  }

  return cues
}

export function fmtTime(sec: number): string {
  const h = Math.floor(sec / 3600)
  const m = Math.floor((sec % 3600) / 60)
  const s = Math.floor(sec % 60)
  if (h > 0) return `${h}:${String(m).padStart(2, '0')}:${String(s).padStart(2, '0')}`
  return `${m}:${String(s).padStart(2, '0')}`
}
