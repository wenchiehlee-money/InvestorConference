export interface DiffSpan {
  text: string
  type: 'same' | 'gt' | 'fin'
}

/** Word-level LCS diff. Returns spans describing how gt and fin differ. */
export function diffWords(gt: string, fin: string): DiffSpan[] {
  if (!gt && !fin) return []
  if (!fin) return [{ text: gt, type: 'gt' }]
  if (!gt) return [{ text: fin, type: 'fin' }]

  const a = tokenize(gt)
  const b = tokenize(fin)

  const dp = buildLCS(a, b)
  const tokens = backtrack(dp, a, b)
  return suppressPunctuationDiffs(mergeSpans(tokens))
}

function tokenize(text: string): string[] {
  // For Chinese/CJK text there are no spaces, so whitespace-splitting produces
  // one giant token per sentence — any single-char difference marks the whole
  // sentence orange.  Instead we split character-by-character, but keep
  // alphanumeric runs (e.g. "2025", "4.9%", "Q&A") as single tokens.
  const tokens: string[] = []
  let buf = ''
  for (const ch of text.trim()) {
    if (/[a-zA-Z0-9]/.test(ch)) {
      buf += ch
    } else {
      if (buf) { tokens.push(buf); buf = '' }
      if (!/\s/.test(ch)) tokens.push(ch)
    }
  }
  if (buf) tokens.push(buf)
  return tokens.filter(Boolean)
}

function buildLCS(a: string[], b: string[]): number[][] {
  const m = a.length
  const n = b.length
  const dp = Array.from({ length: m + 1 }, () => new Array<number>(n + 1).fill(0))
  for (let i = 1; i <= m; i++) {
    for (let j = 1; j <= n; j++) {
      dp[i][j] = a[i - 1] === b[j - 1]
        ? dp[i - 1][j - 1] + 1
        : Math.max(dp[i - 1][j], dp[i][j - 1])
    }
  }
  return dp
}

function backtrack(
  dp: number[][],
  a: string[],
  b: string[],
): Array<{ token: string; type: 'same' | 'gt' | 'fin' }> {
  const result: Array<{ token: string; type: 'same' | 'gt' | 'fin' }> = []
  let i = a.length
  let j = b.length

  while (i > 0 || j > 0) {
    if (i > 0 && j > 0 && a[i - 1] === b[j - 1]) {
      result.push({ token: a[i - 1], type: 'same' })
      i--; j--
    } else if (j > 0 && (i === 0 || dp[i][j - 1] >= dp[i - 1][j])) {
      result.push({ token: b[j - 1], type: 'fin' })
      j--
    } else {
      result.push({ token: a[i - 1], type: 'gt' })
      i--
    }
  }

  return result.reverse()
}

function mergeSpans(
  tokens: Array<{ token: string; type: 'same' | 'gt' | 'fin' }>,
): DiffSpan[] {
  if (tokens.length === 0) return []
  const spans: DiffSpan[] = [{ text: tokens[0].token, type: tokens[0].type }]
  for (let i = 1; i < tokens.length; i++) {
    const last = spans[spans.length - 1]
    if (last.type === tokens[i].type) {
      // Only insert a space between alphanumeric tokens (English words, numbers).
      // CJK characters are concatenated directly — no spaces between them.
      const needsSpace =
        /[a-zA-Z0-9]$/.test(last.text) || /^[a-zA-Z0-9]/.test(tokens[i].token)
      last.text += needsSpace ? ' ' + tokens[i].token : tokens[i].token
    } else {
      spans.push({ text: tokens[i].token, type: tokens[i].type })
    }
  }
  return spans
}

// Punctuation characters (CJK fullwidth and ASCII) whose differences are
// considered non-key and should be suppressed in the diff display.
const PUNCT_RE = /^[，,、。.!！?？；;：:""''「」（）()【】\[\]—–\-…·～~]+$/

/**
 * Convert punctuation-only diff spans to 'same' so that minor punctuation
 * differences (e.g. fullwidth ，vs halfwidth ,) are not highlighted.
 * Only substantive character differences (key CER) remain marked.
 */
function suppressPunctuationDiffs(spans: DiffSpan[]): DiffSpan[] {
  const result: DiffSpan[] = []
  for (let i = 0; i < spans.length; i++) {
    const s = spans[i]
    if (s.type === 'gt' && PUNCT_RE.test(s.text)) {
      // GT punctuation: absorb the paired FIN punctuation (if any) and show as same
      if (i + 1 < spans.length && spans[i + 1].type === 'fin' && PUNCT_RE.test(spans[i + 1].text)) {
        i++ // skip the FIN punctuation span
      }
      result.push({ text: s.text, type: 'same' })
    } else if (s.type === 'fin' && PUNCT_RE.test(s.text)) {
      // FIN-only punctuation insertion — silently drop it
    } else {
      result.push(s)
    }
  }
  return result
}

const esc = (s: string) =>
  s.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;')
const escAttr = (s: string) => esc(s).replace(/"/g, '&quot;')

/**
 * Convert DiffSpan[] to HTML.
 * - same  → plain text
 * - gt    → orange-underlined; if followed by fin → tooltip "FIN: {alt}"
 * - fin   → insertion shown as [text] in brackets
 */
export function renderSpansHtml(spans: DiffSpan[]): string {
  let html = ''
  for (let i = 0; i < spans.length; i++) {
    const s = spans[i]
    if (s.type === 'same') {
      html += esc(s.text)
    } else if (s.type === 'gt') {
      let finAlt = ''
      if (i + 1 < spans.length && spans[i + 1].type === 'fin') {
        finAlt = spans[i + 1].text
        i++
      }
      const tooltip = finAlt
        ? `FIN: ${finAlt.trim()}`
        : 'FIN: (已刪除)'
      html += ` <span class="diff-gt" title="${escAttr(tooltip)}">${esc(s.text)}</span>`
    } else {
      // pure fin insertion
      html += ` <span class="diff-fin" title="FIN 新增">[${esc(s.text.trim())}]</span>`
    }
  }
  return html.trim()
}
