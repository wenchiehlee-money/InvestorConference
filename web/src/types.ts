export type ContentType = '法說會' | 'GTC大會' | 'Podcast'

export interface SrtFile {
  /** raw URL to the .srt file */
  url: string
  /** 'GT' = turboscribe, 'Gen' = generated */
  badge: 'GT' | 'Gen'
}

export interface PdfFile {
  /** raw URL to the .pdf file */
  url: string
  /** suffix part: 'ir', 'ir_en', 'qa', etc. */
  label: string
}

export interface AudioEntry {
  /** e.g. '2382', 'NVDA', 'Podcast' */
  id: string
  contentType: ContentType
  /** TW: from raw_companyinfo.csv 名稱; US: from raw_conceptstock_company_metadata.csv 公司名稱 */
  companyName: string
  /** e.g. '主要業務' for TW, '產品區段' for US */
  businessDesc: string
  /** e.g. '2025 Q3' */
  quarterLabel: string
  /** YYYY-MM-DD from raw_event_upcoming_earnings.csv 開始日期 */
  irDate: string
  /** raw URL to audio file (may be undefined if audio not committed) */
  audioUrl?: string
  /** duration in seconds from audio_durations.json */
  durationSec?: number
  srts: SrtFile[]
  pdfs: PdfFile[]
}

export interface CompanyInfoRow {
  代號: string
  名稱: string
  主要業務: string
  [key: string]: string
}

export interface ConceptStockRow {
  Ticker: string
  公司名稱: string
  產品區段: string
  [key: string]: string
}

export interface EarningsRow {
  事件名稱: string
  開始日期: string
  [key: string]: string
}
