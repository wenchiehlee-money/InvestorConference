import { rawUrl, mediaUrl } from './github'
import type { LoadedData } from './loader'
import type {
  AudioEntry,
  CompanyInfoRow,
  ConceptStockRow,
  ContentType,
  EarningsRow,
  PdfFile,
  SrtFile,
} from '../types'

// ── file-path patterns ────────────────────────────────────────────────────────

/** 法說會: numeric top-level folder, e.g. 2382/2382_2025_q3.mp3 */
const IR_AUDIO_RE = /^(\d+)\/(\d+)_(\d{4})_q(\d)\.(?:mp3|m4a|wav)$/i
const IR_PDF_RE   = /^(\d+)\/(\d+)_(\d{4})_q(\d)_([^/]+)\.pdf$/i
/** GT SRT: {stem}_GT.srt  |  FIN SRT: {stem}.srt or {stem}_FIN.srt */
const IR_SRT_RE   = /^(\d+)\/(\d+)_(\d{4})_q(\d)(?:_GT|_FIN)?\.srt$/i

/** GTC: top-level GTC/ folder */
const GTC_AUDIO_RE = /^GTC\/(.+)\.(?:mp3|m4a|wav)$/i
const GTC_PDF_RE   = /^GTC\/(.+?)_([^/]+)\.pdf$/i
const GTC_SRT_RE   = /^GTC\/(.+?)(?:_GT|_FIN)?\.srt$/i

/** Podcast: top-level Podcast/ folder */
const POD_AUDIO_RE = /^Podcast\/(.+)\.(?:mp3|m4a|wav)$/i
const POD_PDF_RE   = /^Podcast\/(.+?)_([^/]+)\.pdf$/i
const POD_SRT_RE   = /^Podcast\/(.+?)(?:_GT|_FIN)?\.srt$/i

// ── lookup helpers ────────────────────────────────────────────────────────────

function buildCompanyMap(
  companyInfo: CompanyInfoRow[],
  conceptStock: ConceptStockRow[],
): Map<string, { name: string; desc: string }> {
  const map = new Map<string, { name: string; desc: string }>()
  for (const row of companyInfo) {
    const code = (row['代號'] ?? '').trim()
    if (code) map.set(code, { name: row['名稱'] ?? code, desc: row['主要業務'] ?? '' })
  }
  for (const row of conceptStock) {
    const ticker = (row['Ticker'] ?? '').trim().toUpperCase()
    if (ticker) map.set(ticker, { name: row['公司名稱'] ?? ticker, desc: row['產品區段'] ?? '' })
  }
  return map
}

/**
 * Extract IR date from raw_event_upcoming_earnings.csv.
 * 事件名稱 contains the stock code somewhere, e.g. "2382 廣達 2025 Q3 法說會".
 */
function buildEarningsMap(earnings: EarningsRow[]): Map<string, string> {
  // key: `${stockId}_${year}_q${quarter}` → YYYY-MM-DD
  const map = new Map<string, string>()
  for (const row of earnings) {
    const name  = row['事件名稱'] ?? ''
    const date  = (row['開始日期'] ?? '').trim()
    if (!date) continue

    // Try to match patterns like "2382 廣達 2025 Q3" or "NVDA 2025 Q4"
    const m = name.match(/(\d{4}|[A-Z]{1,5})\D+(\d{4})\s+[Qq](\d)/)
    if (m) {
      const key = `${m[1]}_${m[2]}_q${m[3]}`
      map.set(key, date)
    }
  }
  return map
}

function quarterLabel(year: string, quarter: string): string {
  return `${year} Q${quarter}`
}

// ── entry builder ─────────────────────────────────────────────────────────────

function getAudioUrl(path: string, stem: string, data: LoadedData): string {
  if (data.manifest[stem]) {
    // Direct Google Drive link for public (anyone with link) files
    return `https://docs.google.com/uc?export=open&id=${data.manifest[stem]}`
  }
  return mediaUrl(path)
}

/**
 * Build a stable entry key used to group files belonging to the same session.
 * For IR: `{stockId}_{year}_q{quarter}`
 * For GTC / Podcast: stem of the audio/SRT filename
 */
type EntryKey = string

interface MutableEntry {
  id: string
  contentType: ContentType
  quarterLabel: string
  irDate: string
  audioUrl?: string
  durationSec?: number
  srts: SrtFile[]
  pdfs: PdfFile[]
}

// ── main export ───────────────────────────────────────────────────────────────

export function parseEntries(data: LoadedData): AudioEntry[] {
  const companyMap = buildCompanyMap(data.companyInfo, data.conceptStock)
  const earningsMap = buildEarningsMap(data.earnings)

  const entries = new Map<EntryKey, MutableEntry>()

  function getOrCreate(key: EntryKey, defaults: () => MutableEntry): MutableEntry {
    if (!entries.has(key)) entries.set(key, defaults())
    return entries.get(key)!
  }

  for (const item of data.tree) {
    const path = item.path

    // ── 法說會 ──────────────────────────────────────────────────────────────
    let m: RegExpMatchArray | null

    if ((m = path.match(IR_AUDIO_RE))) {
      const [, stockId, , year, quarter] = m
      const key = `${stockId}_${year}_q${quarter}`
      const entry = getOrCreate(key, () => ({
        id: stockId,
        contentType: '法說會',
        quarterLabel: quarterLabel(year, quarter),
        irDate: earningsMap.get(key) ?? '',
        srts: [],
        pdfs: [],
      }))
      entry.audioUrl = getAudioUrl(path, key, data)
      entry.durationSec = data.durations[path]

    } else if ((m = path.match(IR_SRT_RE))) {
      const [, stockId, , year, quarter] = m
      const key = `${stockId}_${year}_q${quarter}`
      const entry = getOrCreate(key, () => ({
        id: stockId,
        contentType: '法說會',
        quarterLabel: quarterLabel(year, quarter),
        irDate: earningsMap.get(key) ?? '',
        srts: [],
        pdfs: [],
      }))
      const badge: SrtFile['badge'] = path.includes('_GT.') ? 'GT' : 'FIN'
      entry.srts.push({ url: rawUrl(path), badge })

    } else if ((m = path.match(IR_PDF_RE))) {
      const [, stockId, , year, quarter, label] = m
      const key = `${stockId}_${year}_q${quarter}`
      const entry = getOrCreate(key, () => ({
        id: stockId,
        contentType: '法說會',
        quarterLabel: quarterLabel(year, quarter),
        irDate: earningsMap.get(key) ?? '',
        srts: [],
        pdfs: [],
      }))
      entry.pdfs.push({ url: rawUrl(path), label })

    // ── GTC 大會 ─────────────────────────────────────────────────────────────
    } else if ((m = path.match(GTC_AUDIO_RE))) {
      const stem = m[1]
      const entry = getOrCreate(stem, () => ({
        id: stem,
        contentType: 'GTC大會',
        quarterLabel: '',
        irDate: '',
        srts: [],
        pdfs: [],
      }))
      entry.audioUrl = getAudioUrl(path, stem, data)
      entry.durationSec = data.durations[path]

    } else if ((m = path.match(GTC_SRT_RE))) {
      const stem = m[1]
      const entry = getOrCreate(stem, () => ({
        id: stem,
        contentType: 'GTC大會',
        quarterLabel: '',
        irDate: '',
        srts: [],
        pdfs: [],
      }))
      const badge: SrtFile['badge'] = path.includes('_GT.') ? 'GT' : 'FIN'
      entry.srts.push({ url: rawUrl(path), badge })

    } else if ((m = path.match(GTC_PDF_RE))) {
      const [, stem, label] = m
      const entry = getOrCreate(stem, () => ({
        id: stem,
        contentType: 'GTC大會',
        quarterLabel: '',
        irDate: '',
        srts: [],
        pdfs: [],
      }))
      entry.pdfs.push({ url: rawUrl(path), label })

    // ── Podcast ───────────────────────────────────────────────────────────────
    } else if ((m = path.match(POD_AUDIO_RE))) {
      const stem = m[1]
      const entry = getOrCreate(stem, () => ({
        id: stem,
        contentType: 'Podcast',
        quarterLabel: '',
        irDate: '',
        srts: [],
        pdfs: [],
      }))
      entry.audioUrl = getAudioUrl(path, stem, data)
      entry.durationSec = data.durations[path]

    } else if ((m = path.match(POD_SRT_RE))) {
      const stem = m[1]
      const entry = getOrCreate(stem, () => ({
        id: stem,
        contentType: 'Podcast',
        quarterLabel: '',
        irDate: '',
        srts: [],
        pdfs: [],
      }))
      const badge: SrtFile['badge'] = path.includes('_GT.') ? 'GT' : 'FIN'
      entry.srts.push({ url: rawUrl(path), badge })

    } else if ((m = path.match(POD_PDF_RE))) {
      const [, stem, label] = m
      const entry = getOrCreate(stem, () => ({
        id: stem,
        contentType: 'Podcast',
        quarterLabel: '',
        irDate: '',
        srts: [],
        pdfs: [],
      }))
      entry.pdfs.push({ url: rawUrl(path), label })
    }
  }

  // ── assemble final AudioEntry[] ───────────────────────────────────────────
  const result: AudioEntry[] = []
  for (const [, e] of entries) {
    const info = companyMap.get(e.id.toUpperCase()) ?? companyMap.get(e.id)
    result.push({
      id: e.id,
      contentType: e.contentType,
      companyName: info?.name ?? e.id,
      businessDesc: info?.desc ?? '',
      quarterLabel: e.quarterLabel,
      irDate: e.irDate,
      audioUrl: e.audioUrl,
      durationSec: e.durationSec,
      srts: e.srts,
      pdfs: e.pdfs,
    })
  }

  // Sort: by irDate desc (blank dates last), then by id
  result.sort((a, b) => {
    if (a.irDate && b.irDate) return b.irDate.localeCompare(a.irDate)
    if (a.irDate) return -1
    if (b.irDate) return 1
    return a.id.localeCompare(b.id)
  })

  return result
}
