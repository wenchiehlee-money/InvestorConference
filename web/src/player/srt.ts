export interface SrtCue {
  index: number
  startSec: number
  endSec: number
  text: string
}

export function parseSrt(raw: string): SrtCue[] {
  const blocks = raw.replace(/\r\n/g, '\n').trim().split(/\n{2,}/)
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
    // Strip HTML tags (common in some SRT files)
    const text = lines.slice(2).join(' ').replace(/<[^>]+>/g, '')

    cues.push({ index, startSec, endSec, text })
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
