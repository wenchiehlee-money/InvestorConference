import {
  AUDIO_DURATIONS_URL,
  COMPANY_INFO_CSV_URL,
  CONCEPT_STOCK_CSV_URL,
  GIT_TREE_URL,
  UPCOMING_EARNINGS_CSV_URL,
} from './github'
import { parseCsv } from './csv'
import type { CompanyInfoRow, ConceptStockRow, EarningsRow } from '../types'

export interface GitTreeItem {
  path: string
  type: 'blob' | 'tree'
  sha: string
  url: string
}

export interface GitTreeResponse {
  tree: GitTreeItem[]
  truncated: boolean
}

export interface LoadedData {
  tree: GitTreeItem[]
  durations: Record<string, number>
  companyInfo: CompanyInfoRow[]
  conceptStock: ConceptStockRow[]
  earnings: EarningsRow[]
}

async function fetchJson<T>(url: string): Promise<T> {
  const res = await fetch(url)
  if (!res.ok) throw new Error(`fetch ${url} → ${res.status}`)
  return res.json() as Promise<T>
}

async function fetchCsv(url: string): Promise<Record<string, string>[]> {
  const res = await fetch(url)
  if (!res.ok) return []          // CSV may not exist yet; return empty
  const text = await res.text()
  return parseCsv(text)
}

export async function loadAll(): Promise<LoadedData> {
  const [treeResp, durations, companyInfo, conceptStock, earnings] = await Promise.all([
    fetchJson<GitTreeResponse>(GIT_TREE_URL),
    fetchJson<Record<string, number>>(AUDIO_DURATIONS_URL).catch(() => ({} as Record<string, number>)),
    fetchCsv(COMPANY_INFO_CSV_URL) as Promise<CompanyInfoRow[]>,
    fetchCsv(CONCEPT_STOCK_CSV_URL) as Promise<ConceptStockRow[]>,
    fetchCsv(UPCOMING_EARNINGS_CSV_URL) as Promise<EarningsRow[]>,
  ])

  return {
    tree: treeResp.tree.filter(item => item.type === 'blob'),
    durations,
    companyInfo,
    conceptStock,
    earnings,
  }
}
