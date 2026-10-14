#!/usr/bin/env python3
"""Build the Balambika font family.

Balambika combines:
  * Latin, IAST and Cyrillic from Common Serif (SIL OFL 1.1), scaled to 108 %
    so that its cap height matches the Shobhika headline (shirorekha),
    with the Bulgarian Cyrillic forms promoted to the default glyphs;
  * Devanagari, Vedic Extensions and Devanagari Extended from Shobhika
    (SIL OFL 1.1), with its complete deva/dev2 shaping tables.

Usage:
    python3 build.py                 # build all styles into ./fonts/ttf
    python3 build.py --no-autohint   # skip ttfautohint
"""

from __future__ import annotations

import argparse
import datetime as dt
import io
import logging
import sys
import tempfile
from dataclasses import dataclass
from pathlib import Path

from fontTools import subset
from fontTools.merge import Merger, Options as MergeOptions
from fontTools.pens.boundsPen import BoundsPen
from fontTools.pens.cu2quPen import Cu2QuPen
from fontTools.pens.ttGlyphPen import TTGlyphPen
from fontTools.ttLib import TTFont, newTable
from fontTools.ttLib.scaleUpem import scale_upem

log = logging.getLogger("balambika")

ROOT = Path(__file__).resolve().parent

# --------------------------------------------------------------------------
# Configuration
# --------------------------------------------------------------------------

FAMILY = "Balambika"
VERSION = "1.000"
VENDOR_ID = "NELV"          # Microsoft font vendor ID (registration requested)
COMPILER = "Nelvaron (https://github.com/nelvaron)"
RESERVED_FONT_NAME = FAMILY

# Latin/Cyrillic scale factor relative to Shobhika (cap height 645 -> ~697,
# Shobhika headline top = 700).
LATIN_SCALE = 1.08

# Vertical metrics (units per em = 1000).
# typo/hhea give a uniform default line height of 1.4 em; win covers the
# full glyph bounding box so that nothing is clipped on Windows.
TYPO_ASCENDER = 1000
TYPO_DESCENDER = -400
TYPO_LINE_GAP = 0

# Word space between two Devanagari words. None keeps Shobhika's own space
# width (450 in Regular, 500 in Bold); Common Serif's space (259 after
# scaling) is used everywhere else, including around a Devanagari word
# inside Latin or Cyrillic text.
DEVA_SPACE_WIDTH: int | None = None

# Code points taken from Shobhika. Everything else comes from Common Serif.
SHOBHIKA_RANGES = [
    (0x0900, 0x097F),  # Devanagari
    (0x1CD0, 0x1CFF),  # Vedic Extensions
    (0xA8E0, 0xA8FF),  # Devanagari Extended
    (0x0FD5, 0x0FD8),  # Swastika signs
    (0xE000, 0xF8FF),  # Private Use Area (Shobhika Vedic alternates)
]
SHOBHIKA_SINGLES = [
    0x200C,  # ZERO WIDTH NON-JOINER - referenced by Devanagari shaping
    0x200D,  # ZERO WIDTH JOINER
    0x25CC,  # DOTTED CIRCLE - inserted by shapers for broken clusters
]


@dataclass(frozen=True)
class Style:
    file_suffix: str        # Balambika-<suffix>.ttf
    latin_source: str       # Common Serif file name
    deva_source: str        # Shobhika file name
    weight: int             # usWeightClass
    italic: bool
    ribbi_family: str       # name ID 1
    ribbi_style: str        # name ID 2
    typo_style: str         # name ID 17


STYLES = [
    Style("Regular", "commonserif-regular.otf", "Shobhika-Regular.otf",
          400, False, FAMILY, "Regular", "Regular"),
    Style("Italic", "commonserif-italic.otf", "Shobhika-Regular.otf",
          400, True, FAMILY, "Italic", "Italic"),
    Style("Medium", "commonserif-medium.otf", "Shobhika-Bold.otf",
          500, False, f"{FAMILY} Medium", "Regular", "Medium"),
    Style("MediumItalic", "commonserif-mediumitalic.otf", "Shobhika-Bold.otf",
          500, True, f"{FAMILY} Medium", "Italic", "Medium Italic"),
    # The family Bold uses Common Serif SemiBold: its stems balance better
    # with Shobhika Bold than Common Serif Bold does.
    Style("Bold", "commonserif-semibold.otf", "Shobhika-Bold.otf",
          700, False, FAMILY, "Bold", "Bold"),
    Style("BoldItalic", "commonserif-semibolditalic.otf", "Shobhika-Bold.otf",
          700, True, FAMILY, "Bold Italic", "Bold Italic"),
]

# Full copyright chain of both sources (see sources/*/OFL.txt and
# sources/shobhika/Copyright.txt).
COPYRIGHT = (
    "Copyright 2022-2024 The Common Serif Project Authors. "
    "Copyright 2012-2021 The Libertinus Project Authors. "
    "Copyright (c) 2016 IIT Bombay. "
    "Copyright (c) 2015 Rajya Marathi Vikas Samstha. "
    "Copyright (c) 2010 ParaType Ltd. "
    f"Copyright 2026 {COMPILER}, "
    f'with Reserved Font Name "{RESERVED_FONT_NAME}".'
)
DESCRIPTION = (
    "Balambika is a Sanskrit-oriented compilation of two OFL typefaces: "
    "Devanagari, Vedic and Devanagari Extended from Shobhika "
    "(IIT Bombay), and Latin, IAST transliteration and Bulgarian Cyrillic "
    "from Common Serif (Stefan Peev and contributors), scaled to 108%."
)
LICENSE = (
    "This Font Software is licensed under the SIL Open Font License, "
    "Version 1.1. This license is available with a FAQ at: "
    "https://openfontlicense.org"
)
LICENSE_URL = "https://openfontlicense.org"


# --------------------------------------------------------------------------
# Helpers
# --------------------------------------------------------------------------

def shobhika_codepoints() -> set[int]:
    cps = set(SHOBHIKA_SINGLES)
    for lo, hi in SHOBHIKA_RANGES:
        cps.update(range(lo, hi + 1))
    return cps


def otf_to_ttf(font: TTFont, max_err: float = 1.0) -> None:
    """Convert a CFF-flavoured font to TrueType outlines in place."""
    glyph_order = font.getGlyphOrder()
    glyph_set = font.getGlyphSet()
    glyf = newTable("glyf")
    glyf.glyphOrder = glyph_order
    glyf.glyphs = {}
    for name in glyph_order:
        tt_pen = TTGlyphPen(glyph_set)
        glyph_set[name].draw(Cu2QuPen(tt_pen, max_err, reverse_direction=True))
        glyf[name] = tt_pen.glyph()
    font["glyf"] = glyf
    font["loca"] = newTable("loca")
    font["maxp"].tableVersion = 0x00010000
    for attr in ("maxZones", "maxTwilightPoints", "maxStorage",
                 "maxFunctionDefs", "maxInstructionDefs", "maxStackElements",
                 "maxSizeOfInstructions", "maxComponentElements"):
        setattr(font["maxp"], attr, 0)
    font["maxp"].maxZones = 1
    font["head"].glyphDataFormat = 0
    post = font["post"]
    post.formatType = 2.0
    post.extraNames = []
    post.mapping = {}
    post.glyphOrder = glyph_order
    for tag in ("CFF ", "VORG", "DSIG"):
        if tag in font:
            del font[tag]
    font.sfntVersion = "\x00\x01\x00\x00"
    font["glyf"].compile(font)  # recompute bounding boxes early


def bulgarian_lookup_mapping(font: TTFont) -> dict[str, str]:
    """Return the single-substitution mapping of the cyrl/BGR 'locl' feature."""
    gsub = font["GSUB"].table
    mapping: dict[str, str] = {}
    for script in gsub.ScriptList.ScriptRecord:
        if script.ScriptTag != "cyrl":
            continue
        for lang in script.Script.LangSysRecord:
            if lang.LangSysTag != "BGR ":
                continue
            for fi in lang.LangSys.FeatureIndex:
                rec = gsub.FeatureList.FeatureRecord[fi]
                if rec.FeatureTag != "locl":
                    continue
                for li in rec.Feature.LookupListIndex:
                    lookup = gsub.LookupList.Lookup[li]
                    for st in lookup.SubTable:
                        sub = st.ExtSubTable if lookup.LookupType == 7 else st
                        if hasattr(sub, "mapping"):
                            mapping.update(sub.mapping)
    return mapping


def promote_bulgarian_forms(font: TTFont) -> int:
    """Point cmap entries for Cyrillic at the Bulgarian (loclBGR) glyphs.

    The Russian default forms then become unreachable and are removed by the
    subsetter, together with the now-redundant locl/ss08 lookups.
    """
    mapping = bulgarian_lookup_mapping(font)
    changed = 0
    for table in font["cmap"].tables:
        if not table.isUnicode():
            continue
        for cp, glyph in list(table.cmap.items()):
            if glyph in mapping and 0x0400 <= cp <= 0x052F:
                table.cmap[cp] = mapping[glyph]
                changed += 1
    return changed


def subset_font(font: TTFont, unicodes: set[int], scripts: list[str] | None) -> None:
    opts = subset.Options()
    opts.layout_features = ["*"]
    opts.layout_scripts = scripts if scripts else ["*"]
    opts.name_IDs = ["*"]
    opts.name_languages = ["*"]
    opts.name_legacy = True
    opts.glyph_names = True
    opts.notdef_outline = True
    opts.notdef_glyph = True
    opts.recommended_glyphs = True
    opts.hinting = False
    opts.legacy_kern = True
    opts.drop_tables += ["DSIG", "VORG", "kern"]
    opts.prune_unicode_ranges = False
    opts.prune_codepage_ranges = False
    sub = subset.Subsetter(opts)
    sub.populate(unicodes=unicodes)
    sub.subset(font)


def prepare_latin(path: Path, exclude: set[int]) -> TTFont:
    font = TTFont(path)
    n = promote_bulgarian_forms(font)
    log.info("  %s: %d Cyrillic code points switched to Bulgarian forms", path.name, n)
    keep = set(font.getBestCmap()) - exclude
    subset_font(font, keep, None)
    otf_to_ttf(font)
    # Scale outlines, metrics and layout values; then restore the 1000 UPM
    # grid so the glyphs come out LATIN_SCALE times larger.
    scale_upem(font, round(1000 * LATIN_SCALE))
    font["head"].unitsPerEm = 1000
    return font


def prepare_devanagari(path: Path, wanted: set[int]) -> TTFont:
    font = TTFont(path)
    keep = set(font.getBestCmap()) & wanted
    subset_font(font, keep, ["deva", "dev2"])
    otf_to_ttf(font)
    return font


def font_bounds(font: TTFont) -> tuple[int, int]:
    glyf = font["glyf"]
    y_min, y_max = 0, 0
    for name in font.getGlyphOrder():
        g = glyf[name]
        if g.numberOfContours == 0:
            continue
        if not hasattr(g, "yMin"):
            g.recalcBounds(glyf)
        y_min = min(y_min, g.yMin)
        y_max = max(y_max, g.yMax)
    return y_min, y_max


def add_devanagari_space(font: TTFont, width: int, deva_glyphs: set[str]) -> None:
    """Add 'space.deva' and use it for space/nbsp between Devanagari words.

    Shapers give a space the script of the preceding text, so a space after
    a Devanagari word in Latin or Cyrillic text is also shaped as Devanagari.
    The substitution is therefore contextual: it applies only when the space
    has a Devanagari glyph on both sides (within the same run). It is
    registered under 'calt' for deva/dev2 only: shapers apply 'locl' to
    Indic text per syllable, so its context could not see the neighbouring
    words, while 'calt' is applied across the whole run.
    """
    from fontTools.pens.ttGlyphPen import TTGlyphPen
    from fontTools.ttLib.tables import otTables as ot

    name = "space.deva"
    order = font.getGlyphOrder()
    if name in order:
        return
    font["glyf"][name] = TTGlyphPen(None).glyph()
    font["hmtx"][name] = (width, 0)
    font.setGlyphOrder(order + [name])
    font["glyf"].glyphOrder = font.getGlyphOrder()
    font["post"].glyphOrder = font.getGlyphOrder()

    cmap = font.getBestCmap()
    spaces = [cmap[cp] for cp in (0x0020, 0x00A0) if cp in cmap]
    context = sorted(deva_glyphs, key=font.getGlyphID)

    def coverage(glyphs):
        cov = ot.Coverage()
        cov.glyphs = list(glyphs)
        return cov

    gsub = font["GSUB"].table
    lookups = gsub.LookupList.Lookup

    # Lookup A: plain single substitution, called from the contextual lookup.
    single = ot.SingleSubst()
    single.mapping = {g: name for g in spaces}
    lk_single = ot.Lookup()
    lk_single.LookupType, lk_single.LookupFlag = 1, 0
    lk_single.SubTable, lk_single.SubTableCount = [single], 1
    lookups.append(lk_single)
    single_index = len(lookups) - 1

    # Lookup B: chaining context, Devanagari | space | Devanagari.
    chain = ot.ChainContextSubst()
    chain.Format = 3
    chain.BacktrackCoverage = [coverage(context)]
    chain.InputCoverage = [coverage(spaces)]
    chain.LookAheadCoverage = [coverage(context)]
    rec = ot.SubstLookupRecord()
    rec.SequenceIndex, rec.LookupListIndex = 0, single_index
    chain.SubstLookupRecord = [rec]
    chain.BacktrackGlyphCount = chain.InputGlyphCount = 1
    chain.LookAheadGlyphCount = chain.SubstCount = 1
    lk_chain = ot.Lookup()
    lk_chain.LookupType, lk_chain.LookupFlag = 6, 0
    lk_chain.SubTable, lk_chain.SubTableCount = [chain], 1
    lookups.append(lk_chain)
    chain_index = len(lookups) - 1
    gsub.LookupList.LookupCount = len(lookups)

    feature = ot.Feature()
    feature.FeatureParams = None
    feature.LookupListIndex = [chain_index]
    feature.LookupCount = 1
    record = ot.FeatureRecord()
    record.FeatureTag = "calt"
    record.Feature = feature
    gsub.FeatureList.FeatureRecord.append(record)
    gsub.FeatureList.FeatureCount = len(gsub.FeatureList.FeatureRecord)
    feature_index = gsub.FeatureList.FeatureCount - 1

    for script in gsub.ScriptList.ScriptRecord:
        if script.ScriptTag not in ("deva", "dev2"):
            continue
        langsys = [script.Script.DefaultLangSys] + [
            r.LangSys for r in script.Script.LangSysRecord]
        for ls in langsys:
            if ls is None:
                continue
            ls.FeatureIndex.append(feature_index)
            ls.FeatureCount = len(ls.FeatureIndex)


def set_names(font: TTFont, style: Style) -> None:
    name = font["name"]
    name.names = []
    ps_name = f"{FAMILY}-{style.file_suffix}"
    full_name = f"{FAMILY} {style.typo_style}".replace(" Regular", "") \
        if style.typo_style != "Regular" else f"{FAMILY} Regular"
    records = {
        0: COPYRIGHT,
        1: style.ribbi_family,
        2: style.ribbi_style,
        3: f"{VERSION};{VENDOR_ID};{ps_name}",
        4: full_name,
        5: f"Version {VERSION}; Common Serif 1.048 + Shobhika 1.05",
        6: ps_name,
        10: DESCRIPTION,
        13: LICENSE,
        14: LICENSE_URL,
    }
    if style.ribbi_family != FAMILY:
        records[16] = FAMILY
        records[17] = style.typo_style
    for nid, value in records.items():
        name.setName(value, nid, 3, 1, 0x409)
        if nid in (0, 1, 2, 3, 4, 5, 6):
            name.setName(value, nid, 1, 0, 0)


def set_style_flags(font: TTFont, style: Style) -> None:
    os2 = font["OS/2"]
    head = font["head"]
    bold = style.ribbi_style in ("Bold", "Bold Italic")
    fs = 0
    if style.italic:
        fs |= 1 << 0
    if bold:
        fs |= 1 << 5
    if not style.italic and not bold:
        fs |= 1 << 6          # REGULAR
    fs |= 1 << 7              # USE_TYPO_METRICS
    os2.fsSelection = fs
    os2.usWeightClass = style.weight
    os2.usWidthClass = 5
    os2.fsType = 0
    os2.achVendID = VENDOR_ID
    os2.version = max(os2.version, 4)
    head.macStyle = (1 if bold else 0) | (2 if style.italic else 0)
    if not style.italic:
        font["post"].italicAngle = 0
        font["hhea"].caretSlopeRise = 1
        font["hhea"].caretSlopeRun = 0


def set_vertical_metrics(font: TTFont, latin_metrics: dict) -> None:
    os2 = font["OS/2"]
    hhea = font["hhea"]
    y_min, y_max = font_bounds(font)
    os2.sTypoAscender = TYPO_ASCENDER
    os2.sTypoDescender = TYPO_DESCENDER
    os2.sTypoLineGap = TYPO_LINE_GAP
    hhea.ascent = TYPO_ASCENDER
    hhea.descent = TYPO_DESCENDER
    hhea.lineGap = TYPO_LINE_GAP
    os2.usWinAscent = max(y_max, TYPO_ASCENDER)
    os2.usWinDescent = max(-y_min, -TYPO_DESCENDER)
    # x-height / cap height come from the scaled Latin component.
    os2.sxHeight = latin_metrics["xHeight"]
    os2.sCapHeight = latin_metrics["capHeight"]
    os2.yStrikeoutPosition = latin_metrics["strikeoutPosition"]
    os2.yStrikeoutSize = latin_metrics["strikeoutSize"]


def finalize(font: TTFont, style: Style, latin_metrics: dict,
             deva_space: int, deva_glyphs: set[str]) -> None:
    add_devanagari_space(font, deva_space, deva_glyphs)
    set_names(font, style)
    set_style_flags(font, style)
    set_vertical_metrics(font, latin_metrics)
    head = font["head"]
    head.fontRevision = float(VERSION)
    head.flags |= 1 << 3      # force ppem to integer values
    os2 = font["OS/2"]
    os2.recalcUnicodeRanges(font)
    os2.recalcCodePageRanges(font)
    gasp = newTable("gasp")
    gasp.version = 1
    gasp.gaspRange = {0xFFFF: 0x000F}
    font["gasp"] = gasp


def autohint(data: bytes) -> bytes:
    import ttfautohint
    return ttfautohint.ttfautohint(
        in_buffer=data,
        default_script="latn",
        fallback_script="none",
        hinting_range_min=8,
        hinting_range_max=50,
        hinting_limit=200,
        increase_x_height=0,
        symbol=False,
        no_info=True,
    )


def build_style(style: Style, src: Path, out_dir: Path, hint: bool) -> Path:
    log.info("Building %s", style.file_suffix)
    deva_cps = shobhika_codepoints()
    latin = prepare_latin(src / "common-serif" / style.latin_source, deva_cps)
    deva_path = src / "shobhika" / style.deva_source
    deva_space = DEVA_SPACE_WIDTH or TTFont(deva_path)["hmtx"]["space"][0]
    deva = prepare_devanagari(deva_path, deva_cps)

    os2 = latin["OS/2"]
    latin_metrics = {
        "xHeight": os2.sxHeight,
        "capHeight": os2.sCapHeight,
        "strikeoutPosition": os2.yStrikeoutPosition,
        "strikeoutSize": os2.yStrikeoutSize,
    }

    with tempfile.TemporaryDirectory() as tmp:
        a, b = Path(tmp, "latin.ttf"), Path(tmp, "deva.ttf")
        latin.save(a)
        deva.save(b)
        merger = Merger(options=MergeOptions(drop_tables=["DSIG", "vhea", "vmtx"]))
        merged = merger.merge([str(a), str(b)])

    # Glyphs that came only from Shobhika (shared names such as .notdef are
    # renamed by the merger and excluded here).
    deva_glyphs = (set(deva.getGlyphOrder()) - set(latin.getGlyphOrder())) \
        & set(merged.getGlyphOrder())
    finalize(merged, style, latin_metrics, deva_space, deva_glyphs)

    buf = io.BytesIO()
    merged.save(buf)
    data = buf.getvalue()
    if hint:
        try:
            data = autohint(data)
        except Exception as exc:  # keep an unhinted build rather than failing
            log.warning("  ttfautohint failed (%s); writing unhinted font", exc)

    out = out_dir / f"{FAMILY}-{style.file_suffix}.ttf"
    out.write_bytes(data)
    log.info("  -> %s", out.relative_to(ROOT) if out.is_relative_to(ROOT) else out)
    return out


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--sources", type=Path, default=ROOT / "sources",
                    help="folder containing common-serif/ and shobhika/")
    ap.add_argument("--out", type=Path, default=ROOT / "fonts" / "ttf")
    ap.add_argument("--no-autohint", action="store_true")
    ap.add_argument("--style", action="append",
                    help="build only this style (e.g. Regular); repeatable")
    ap.add_argument("-v", "--verbose", action="store_true")
    args = ap.parse_args(argv)

    logging.basicConfig(level=logging.DEBUG if args.verbose else logging.INFO,
                        format="%(message)s")
    logging.getLogger("fontTools").setLevel(logging.ERROR)

    args.out.mkdir(parents=True, exist_ok=True)
    styles = [s for s in STYLES if not args.style or s.file_suffix in args.style]
    for style in styles:
        build_style(style, args.sources, args.out, hint=not args.no_autohint)
    return 0


if __name__ == "__main__":
    sys.exit(main())
