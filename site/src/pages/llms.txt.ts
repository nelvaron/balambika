import type { APIRoute } from 'astro';
import { localePath, REPO, RAW } from '../i18n/ui';

// llms.txt v2, scoped to this project path and advertised with rel="describedby".
export const GET: APIRoute = ({ site }) => {
  const u = (locale: 'en' | 'bg', page = '') => new URL(localePath(locale, page), site).href;
  const body = `# Balambika

> Balambika is an open-source font project (SIL OFL 1.1) for Sanskrit publishing in two families. Balambika (serif): Devanagari from Shobhika, Latin with full IAST and Bulgarian Cyrillic from Common Serif, in six styles. Balambika Sans: Devanagari from Noto Sans Devanagari (including Sāmaveda notation), Latin with full IAST and Bulgarian Cyrillic from Source Sans 3, in twelve styles. Both work the same in Pages, Word and XeLaTeX.

This site presents the fonts with specimens for each script, a comparison of the two families, a conjunct explorer, Vedic accents and a type tester. A switch in the header shows the whole site in either family; add ?face=sans to any address to open it in Balambika Sans. Pages exist in English and Bulgarian.

## Pages

- [Overview](${u('en')}): What the font is, with examples in Devanagari, IAST, English and Bulgarian.
- [Devanagari specimen](${u('en', 'specimens/devanagari/')}): Character set, conjuncts and Vedic marks.
- [Latin specimen](${u('en', 'specimens/latin/')}): Latin, IAST and the Devanagari–IAST correspondence.
- [Cyrillic specimen](${u('en', 'specimens/cyrillic/')}): Bulgarian Cyrillic with Bulgarian letterforms by default.
- [Usage](${u('en', 'usage/')}): Installing, and setting up Pages, Word, XeLaTeX and the web.
- [Обзор на български](${u('bg')}): The overview in Bulgarian.

## Source

- [Repository](${REPO}): Build scripts, sources and README.
- [Balambika-Regular.ttf](${RAW}/Balambika-Regular.ttf): The regular style of the serif.
- [BalambikaSans-Regular.ttf](${RAW}/BalambikaSans-Regular.ttf): The regular style of the sans.

## Optional

- [Privacy](${u('en', 'privacy/')}): No cookies, no analytics.
`;
  return new Response(body, { headers: { 'Content-Type': 'text/markdown; charset=utf-8' } });
};
