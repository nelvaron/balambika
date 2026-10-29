# Balambika

![Balambika: Devanagari, IAST and Cyrillic in one font — Ṛgveda 1.1.1](images/readme-header.png)

Balambika (*Bālāmbikā*) is a font family for Sanskrit publishing — Vedic and
Purāṇic texts set in Devanagari, with IAST transliteration and Bulgarian or
English translation, in one font that works the same in Pages, Word and
XeLaTeX.

Specimens, a conjunct explorer and a type tester are on the website:
<https://nelvaron.github.io/balambika/>.

It is a compilation of two typefaces released under the SIL Open Font License:

| Component | Source | Scripts |
|---|---|---|
| Devanagari | [Shobhika](https://github.com/Sandhi-IITBombay/Shobhika) 1.05, IIT Bombay (Devanagari based on Yashomudra) | Devanagari, Vedic Extensions, Devanagari Extended, PUA alternates |
| Latin, IAST, Cyrillic | [Common Serif](https://github.com/StefanPeev/Common-Serif) 1.048, The Common Serif Project Authors (derived from Libertinus Serif) | Latin incl. full IAST, Bulgarian Cyrillic, Greek |

## Styles

| File | Style | Latin / Cyrillic from | Devanagari from | Weight |
|---|---|---|---|---|
| `Balambika-Regular.ttf` | Regular | Common Serif Regular | Shobhika Regular | 400 |
| `Balambika-Italic.ttf` | Italic | Common Serif Italic | Shobhika Regular (upright) | 400 |
| `Balambika-Medium.ttf` | Medium | Common Serif Medium | Shobhika Bold | 500 |
| `Balambika-MediumItalic.ttf` | Medium Italic | Common Serif Medium Italic | Shobhika Bold (upright) | 500 |
| `Balambika-Bold.ttf` | Bold | Common Serif **SemiBold** | Shobhika Bold | 700 |
| `Balambika-BoldItalic.ttf` | Bold Italic | Common Serif **SemiBold** Italic | Shobhika Bold (upright) | 700 |

Regular, Italic, Bold and Bold Italic form the style-linked (RIBBI) family
*Balambika*, so the B and I buttons in Word and Pages work as expected.
Medium appears as *Balambika Medium* in applications that do not read
typographic family names.

## Design decisions

- **Latin scaled to 108 %.** Common Serif's cap height (645) becomes 697,
  matching Shobhika's headline (700). x-height becomes 463.
- **Bold uses Common Serif SemiBold.** Measured stem widths (after scaling):
  Common Serif Regular 86, Medium 105, SemiBold 122, Bold 140; Shobhika
  Regular 80, Bold 108. Shobhika has only two weights and its masters are not
  interpolation-compatible, so Medium and Bold share Shobhika Bold, and
  SemiBold is the closest Latin partner for a balanced bold.
- **Upright Devanagari in italic styles.** Devanagari has no italic tradition;
  the italic files contain the same upright Devanagari, so applications never
  synthesise a slanted one.
- **Bulgarian Cyrillic is the default.** The Bulgarian forms (`locl` BGR) are
  mapped directly in `cmap`, so they appear without language tagging, which
  Word and Pages do not apply reliably. The Russian, Serbian and Macedonian
  alternates are removed.
- **Devanagari word spacing.** Latin and Cyrillic use Common Serif's space
  (259 units). Between two Devanagari words a contextual `calt` lookup
  (deva/dev2 only) substitutes `space.deva`, which keeps Shobhika's own width
  (450 Regular, 500 Medium/Bold). A space next to Latin or Cyrillic keeps the
  narrow width, so a Devanagari word inside English or Bulgarian text is
  spaced evenly on both sides. (`calt` rather than `locl`: shapers apply
  `locl` to Indic text per syllable, so its context cannot see neighbouring
  words.)
- **Vertical metrics.** `hhea` = `typo` = 1000 / −400 / 0 (default line height
  1.4 em) with `USE_TYPO_METRICS` set. `usWinAscent/Descent` cover the full
  bounding box (1121 / 1015) so stacked Vedic marks are never clipped.
- **TrueType outlines, autohinted.** Both sources are CFF; they are converted
  to TrueType so the two scripts share one hinting model (ttfautohint, Latin
  default with Devanagari detected automatically).

## Building

Requirements: Python 3.10+, and

```sh
pip install fonttools ttfautohint-py uharfbuzz
```

Source fonts are in `sources/`. Then:

```sh
python3 build.py                 # all styles -> fonts/ttf/
python3 build.py --style Regular # one style
python3 build.py --no-autohint   # unhinted
python3 tools/verify.py          # compare shaping with the source fonts
```

Configuration (family name, scale factor, vertical metrics, Devanagari space,
code-point split) is at the top of `build.py`. When a source font is updated,
replace the file in `sources/` and rebuild.

`tools/verify.py` shapes test strings with HarfBuzz and checks that Devanagari
and Vedic text produce exactly the same glyphs and positions as Shobhika, and
Latin/IAST/Cyrillic the same as Common Serif with Bulgarian localisation
(positions × 1.08). It also checks IAST and Bulgarian coverage and the style
naming.

## Using the fonts

### Pages (macOS)

- Use *Spacing › Exactly* for even line spacing in mixed-script text.
- Hyphenation follows the document language; switch it off per paragraph
  (*Format › Text › More*) for IAST-heavy passages, or protect terms with
  non-breaking spaces.

### Word

- Set Balambika as both the Latin and the *Complex scripts* font in every
  style, with the same size and bold settings, otherwise Devanagari words
  inside Latin text may come out in a different size or weight.
- Word for Windows uses `usWin` metrics for line height, so the default
  spacing is loose; use *Line spacing › Exactly*.
- Mark IAST as *Do not check spelling or grammar* (or as Sanskrit).

### XeLaTeX

XeTeX shapes each font instance with a single OpenType script. Devanagari
must therefore be set with a `Script=Devanagari` instance, even though
everything is in one file. See `examples/xelatex-specimen.tex` for a complete
polyglossia setup:

```latex
\usepackage{fontspec}
\usepackage{polyglossia}
\setdefaultlanguage{bulgarian}
\setotherlanguages{english, sanskrit}

\setmainfont{Balambika}[
  UprightFont = *-Regular, ItalicFont = *-Italic,
  BoldFont = *-Bold, BoldItalicFont = *-BoldItalic,
  FontFace = {mb}{n}{*-Medium}, FontFace = {mb}{it}{*-MediumItalic}]
\newfontfamily\devanagarifont{Balambika}[Script = Devanagari,
  WordSpace = 1.737, BoldFeatures = {WordSpace = 1.931},
  UprightFont = *-Regular, BoldFont = *-Bold, ...]
\newfontfamily\iastfont{Balambika}[UprightFont = *-Regular, ...]

\newcommand\dev[1]{\textsanskrit{#1}}
\newcommand\iast[1]{\textlang{sa-Latn}{\iastfont\itshape #1}}
```

Notes:

- Define `\devanagarifont`, not `\sanskritfont`: polyglossia applies
  `\sanskritfont` even to `sa-Latn`, which would shape IAST with Devanagari
  features.
- XeTeX measures the word space from a lone U+0020, so the font's contextual
  Devanagari space never applies; `WordSpace` restores Shobhika's spacing
  (450/259 = 1.737 for Regular, 500/259 = 1.931 for Medium and Bold).
- `\textsanskrit[script=latin]{…}` inserts spurious space in current
  polyglossia; use `\textlang{sa-Latn}{…}` instead.

## Known limitations

See also [ACCESSIBILITY.md](ACCESSIBILITY.md).

- **Devanagari Extended** (U+A8E0–U+A8FF): Shobhika covers only 6 of 32
  characters. Missing: the Sāmaveda combining digits and letters
  U+A8E0–U+A8F1, U+A8F2 (spacing candrabindu), U+A8F8–U+A8FA,
  U+A8FC–U+A8FF.
- **Vedic Extensions**: U+1CF7 and U+1CFA are missing.
- Common Serif has no `mkmk` feature. Precomposed IAST letters with an added
  accent (e.g. *ā́*) position correctly; long stacks of combining marks on one
  base letter may not.
- Hinting is automatic; at small screen sizes on Windows some Devanagari
  details may be less crisp than in the original CFF hinting.

## License

SIL Open Font License 1.1 — see `OFL.txt`.

**Balambika** is a Reserved Font Name. Modified versions made by anyone other
than the copyright holder must be distributed under a different name; this
includes rebuilds, subsets and format conversions (e.g. WOFF2) that are
redistributed. No Reserved Font Name of the source fonts ("Common Serif",
"Linux Libertine", "Biolinum", "STIX Fonts") is used as the font name.
The original license and copyright files of both sources are in `sources/`
(see `sources/README.md`).

The OS/2 vendor ID is `NELV`, registered to Nelvaron in the
[Microsoft Typography vendor registry](https://learn.microsoft.com/en-us/typography/vendors/). The fonts may be used, embedded and redistributed freely, including in
commercial books, but may not be sold on their own.
