export interface DiffSpan {
  text: string
  type: 'same' | 'gt' | 'gen'
}

/** Word-level LCS diff. Returns spans describing how gt and gen differ. */
export function diffWords(gt: string, gen: string): DiffSpan[] {
  if (!gt && !gen) return []
  if (!gen) return [{ text: gt, type: 'gt' }]
  if (!gt) return [{ text: gen, type: 'gen' }]

  const a = tokenize(gt)
  const b = tokenize(gen)

  const dp = buildLCS(a, b)
  const tokens = backtrack(dp, a, b)
  return mergeSpans(tokens)
}

function tokenize(text: string): string[] {
  return text.trim().split(/\s+/).filter(Boolean)
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
): Array<{ token: string; type: 'same' | 'gt' | 'gen' }> {
  const result: Array<{ token: string; type: 'same' | 'gt' | 'gen' }> = []
  let i = a.length
  let j = b.length

  while (i > 0 || j > 0) {
    if (i > 0 && j > 0 && a[i - 1] === b[j - 1]) {
      result.push({ token: a[i - 1], type: 'same' })
      i--; j--
    } else if (j > 0 && (i === 0 || dp[i][j - 1] >= dp[i - 1][j])) {
      result.push({ token: b[j - 1], type: 'gen' })
      j--
    } else {
      result.push({ token: a[i - 1], type: 'gt' })
      i--
    }
  }

  return result.reverse()
}

function mergeSpans(
  tokens: Array<{ token: string; type: 'same' | 'gt' | 'gen' }>,
): DiffSpan[] {
  if (tokens.length === 0) return []
  const spans: DiffSpan[] = [{ text: tokens[0].token, type: tokens[0].type }]
  for (let i = 1; i < tokens.length; i++) {
    const last = spans[spans.length - 1]
    if (last.type === tokens[i].type) {
      last.text += ' ' + tokens[i].token
    } else {
      spans.push({ text: tokens[i].token, type: tokens[i].type })
    }
  }
  return spans
}

const esc = (s: string) =>
  s.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;')
const escAttr = (s: string) => esc(s).replace(/"/g, '&quot;')

/**
 * Convert DiffSpan[] to HTML.
 * - same  → plain text
 * - gt    → orange-underlined; if followed by gen → tooltip "Gen: {alt}"
 * - gen   → insertion shown as [text] in brackets
 */
export function renderSpansHtml(spans: DiffSpan[]): string {
  let html = ''
  for (let i = 0; i < spans.length; i++) {
    const s = spans[i]
    if (s.type === 'same') {
      html += esc(s.text)
    } else if (s.type === 'gt') {
      let genAlt = ''
      if (i + 1 < spans.length && spans[i + 1].type === 'gen') {
        genAlt = spans[i + 1].text
        i++
      }
      const tooltip = genAlt
        ? `Gen: ${genAlt.trim()}`
        : 'Gen: (已刪除)'
      html += ` <span class="diff-gt" title="${escAttr(tooltip)}">${esc(s.text)}</span>`
    } else {
      // pure gen insertion
      html += ` <span class="diff-gen" title="Gen 新增">[${esc(s.text.trim())}]</span>`
    }
  }
  return html.trim()
}
