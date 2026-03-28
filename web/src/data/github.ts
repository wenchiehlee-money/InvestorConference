export const REPO_OWNER = 'wenchiehlee-money'
export const REPO_NAME = 'InvestorConference'
export const BRANCH = 'main'

export const RAW_BASE = `https://raw.githubusercontent.com/${REPO_OWNER}/${REPO_NAME}/${BRANCH}`
export const API_BASE = `https://api.github.com/repos/${REPO_OWNER}/${REPO_NAME}`

export function rawUrl(path: string): string {
  const normalized = path.startsWith('/') ? path.slice(1) : path
  return `${RAW_BASE}/${normalized}`
}

export const GIT_TREE_URL = `${API_BASE}/git/trees/${BRANCH}?recursive=1`

export const AUDIO_DURATIONS_URL = rawUrl('audio_durations.json')

/** CSV synced from wenchiehlee-investment/Python-Actions.GoodInfo.CompanyInfo */
export const COMPANY_INFO_CSV_URL = rawUrl('raw_companyinfo.csv')

/** CSV synced from wenchiehlee-investment/ConceptStocks */
export const CONCEPT_STOCK_CSV_URL = rawUrl('raw_conceptstock_company_metadata.csv')

/** CSV synced from wenchiehlee-investment/InvestorEvents */
export const UPCOMING_EARNINGS_CSV_URL = rawUrl('upcoming_earnings.csv')
