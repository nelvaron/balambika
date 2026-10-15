# Accessibility

Balambika is a font, so its accessibility is mostly about whether text set in
it stays readable, searchable and correctly interpreted by assistive
technology. This page describes what the project aims for, what has been
checked, and where the known barriers are.

## Priorities

1. **Correct Unicode text.** Every visible glyph must map back to the correct
   Unicode characters, so that screen readers, search, copy and paste, and
   text-to-speech work on documents set in Balambika. Devanagari conjuncts,
   Vedic accents and IAST letters are produced by OpenType shaping from
   standard Unicode input, never by private-use code points or visual hacks.
2. **Legibility.** Clear forms at text sizes for long Sanskrit and
   transliterated passages: balanced weights between Devanagari and Latin,
   Bulgarian Cyrillic forms by default, and vertical metrics that do not clip
   stacked Vedic marks.
3. **Predictable behaviour across applications**, so that users do not need
   workarounds that break the text layer (for example, faking a conjunct with
   images or overlapping characters).

## Supported environments

| Environment | Status |
|---|---|
| Web browsers (HarfBuzz: Chrome, Edge, Firefox) | Tested; shaping identical to the source fonts |
| Apple Pages / macOS CoreText | Tested via PDF export; text layer carries correct per-cluster `ActualText` |
| XeLaTeX (HarfBuzz) | Tested with the setup in `examples/xelatex-specimen.tex` |
| Microsoft Word | Not tested; see notes in `README.md` |
| Screen readers (VoiceOver, NVDA, JAWS) | Not yet tested |

## Known barriers

- **Private Use Area glyphs.** Shobhika's alternate Vedic glyphs in
  U+F401–U+F6D4 are kept for compatibility, but text that uses them has no
  standard meaning: screen readers, search and other fonts cannot interpret
  it. Prefer standard Unicode characters (Vedic Extensions, Devanagari
  Extended) wherever they exist.
- **Missing characters.** Most of Devanagari Extended (Sāmaveda marks
  U+A8E0–U+A8F2 and others) and U+1CF7, U+1CFA are not covered. Text that
  uses them falls back to another font or shows missing-glyph boxes.
- **PDF text extraction.** In PDFs exported from Pages, Devanagari clusters
  are recoverable only through `ActualText`. Readers that ignore it (for
  example `pdftotext`) lose conjuncts. This is a limitation of the PDF
  producer and the reader, not of the font, but it affects users of such
  documents.
- **IAST avagraha and apostrophes.** Using a straight apostrophe (U+0027) for
  avagraha in transliteration splits words for search and hyphenation. Use
  U+02BC MODIFIER LETTER APOSTROPHE, which the font supports.
- **Line spacing in Word for Windows** follows the large `usWin` metrics and
  may look loose; this affects reading comfort, not correctness.

## Contributor expectations

- Changes to the build must keep `python3 tools/verify.py` passing. It checks
  that Devanagari, IAST and Cyrillic shape exactly like the source fonts.
- Do not map visible glyphs to new Private Use Area code points or to
  incorrect Unicode values.
- Images in the documentation need meaningful alternative text.
- Report any change that affects the text layer, line spacing or legibility
  in the pull request description.

## Reporting accessibility problems

Open an issue at <https://github.com/nelvaron/balambika/issues> and include:

- the application and version, and the assistive technology if any;
- the exact text (as Unicode, not an image) and what you expected;
- a screenshot or PDF if the problem is visual.

## Ownership and maintenance

The project is maintained by Nelvaron (<https://github.com/nelvaron>), who
triages accessibility reports. This page is reviewed with every release and
updated whenever supported environments or known barriers change.
