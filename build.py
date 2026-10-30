#!/usr/bin/env python3
"""Build the Balambika and Balambika Sans font families.

Each family merges two SIL OFL 1.1 typefaces into one font per style:

Balambika (serif)
  * Latin, IAST and Cyrillic from Common Serif, scaled to 108 % so that its
    cap height matches the Shobhika headline (shirorekha);
  * Devanagari, Vedic Extensions and Devanagari Extended from Shobhika.

Balambika Sans
  * Latin, IAST and Cyrillic from Source Sans 3, scaled to 109 % so that its
    cap height matches Noto Sans, the design partner of Noto Sans Devanagari;
  * Devanagari, Vedic Extensions and Devanagari Extended from Noto Sans
    Devanagari, instanced at weights whose stems balance the Latin weight.

In both, the Bulgarian Cyrillic forms are promoted to the default glyphs and
the Devanagari part keeps its complete deva/dev2 shaping tables.

Usage:
    python3 build.py                     # build all families and styles
    python3 build.py --family sans       # one family (serif or sans)
    python3 build.py --style Regular     # one style name, in every family
    python3 build.py --no-autohint       # skip ttfautohint
"""

from __future__ import annotations

import argparse
import io
import logging
import sys
import tempfile
from dataclasses import dataclass, field
from pathlib import Path

from fontTools import subset
from fontTools.merge import Merger, Options as MergeOptions
from fontTools.pens.boundsPen import BoundsPen
from fontTools.pens.cu2quPen import Cu2QuPen
from fontTools.pens.ttGlyphPen import TTGlyphPen
from fontTools.ttLib import TTFont, newTable
from fontTools.ttLib.scaleUpem import scale_upem
from fontTools.varLib import instancer

log = logging.getLogger("balambika")

ROOT = Path(__file__).resolve().parent

# --------------------------------------------------------------------------
# Configuration
# --------------------------------------------------------------------------

VERSION = "1.000"
VENDOR_ID = "NELV"          # Microsoft font vendor ID, registered to Nelvaron
COMPILER = "Nelvaron (https://github.com/nelvaron)"
RESERVED_FONT_NAME = "Balambika"

# Vertical metrics (units per em = 1000), shared by both families.
# typo/hhea give a uniform default line height of 1.4 em; win covers the
# full glyph bounding box so that nothing is clipped on Windows.
TYPO_ASCENDER = 1000
TYPO_DESCENDER = -400
TYPO_LINE_GAP = 0

# Word space between two Devanagari words. None keeps the Devanagari source's
# own space width; the Latin space is used everywhere else, including around
# a Devanagari word inside Latin or Cyrillic text.
DEVA_SPACE_WIDTH: int | None = None

# Code points taken from the Devanagari source. Everything else comes from
# the Latin source. Ranges a source does not cover are simply skipped.
DEVA_RANGES = [
    (0x0900, 0x097F),  # Devanagari
    (0x1CD0, 0x1CFF),  # Vedic Extensions
    (0xA8E0, 0xA8FF),  # Devanagari Extended
    (0x0FD5, 0x0FD8),  # Swastika signs
    (0xE000, 0xF8FF),  # Private Use Area (Shobhika Vedic alternates)
]
DEVA_SINGLES = [
    0x200C,  # ZERO WIDTH NON-JOINER - referenced by Devanagari shaping
    0x200D,  # ZERO WIDTH JOINER
    0x25CC,  # DOTTED CIRCLE - inserted by shapers for broken clusters
]

LICENSE = (
    "This Font Software is licensed under the SIL Open Font License, "
    "Version 1.1. This license is available with a FAQ at: "
    "https://openfontlicense.org"
)
LICENSE_URL = "https://openfontlicense.org"


@dataclass(frozen=True)
class Source:
    """A source font file (relative to sources/) and, for a variable font,
    the axis location of the instance to use."""
    path: str
    location: dict = field(default_factory=dict)


@dataclass(frozen=True)
class Style:
    file_suffix: str        # <ps_family>-<suffix>.ttf
    latin: Source
    deva: Source
    weight: int             # usWeightClass
    italic: bool
    ribbi_family: str       # name ID 1
    ribbi_style: str        # name ID 2
    typo_style: str         # name ID 17


@dataclass(frozen=True)
class Family:
    key: str                # command-line key: serif, sans
    name: str               # typographic family name (name ID 16 / 1)
    ps_name: str            # PostScript and file name prefix
    latin_scale: float
    copyright: str
    description: str
    version_note: str       # appended to name ID 5
    styles: list


def _style(fam: str, suffix: str, latin: Source, deva: Source, weight: int,
           italic: bool, typo_style: str) -> Style:
    """Derive RIBBI naming: Regular/Italic/Bold/Bold Italic stay in the main
    family; every other weight gets its own legacy family name."""
    weight_name = typo_style.replace(" Italic", "").replace("Italic", "")
    if weight_name in ("Regular", "", "Bold"):
        ribbi_family = fam
        ribbi_style = typo_style
    else:
        ribbi_family = f"{fam} {weight_name}"
        ribbi_style = "Italic" if italic else "Regular"
    return Style(suffix, latin, deva, weight, italic, ribbi_family,
                 ribbi_style, typo_style)


# --- Balambika (serif) ------------------------------------------------------

_SERIF = "Balambika"
_CS = "common-serif/commonserif-{}.otf"
_SH = "shobhika/Shobhika-{}.otf"
SERIF = Family(
    key="serif",
    name=_SERIF,
    ps_name="Balambika",
    # Common Serif cap height 645 -> ~697 = Shobhika headline top (700).
    latin_scale=1.08,
    # Copyright chain of the glyphs actually used (see sources/*/OFL.txt and
    # sources/shobhika/Copyright.txt). Shobhika's Latin and Cyrillic, which
    # are based on PT Serif (ParaType), are not included.
    copyright=(
        "Copyright 2022-2024 The Common Serif Project Authors. "
        "Copyright 2012-2021 The Libertinus Project Authors. "
        "Copyright (c) 2016 IIT Bombay. "
        "Copyright (c) 2015 Rajya Marathi Vikas Samstha. "
        f"Copyright 2026 {COMPILER}, "
        f'with Reserved Font Name "{RESERVED_FONT_NAME}".'
    ),
    description=(
        "Balambika is a Sanskrit-oriented compilation of two OFL typefaces: "
        "Devanagari, Vedic and Devanagari Extended from Shobhika "
        "(IIT Bombay), and Latin, IAST transliteration and Bulgarian Cyrillic "
        "from Common Serif (Stefan Peev and contributors), scaled to 108%."
    ),
    version_note="Common Serif 1.048 + Shobhika 1.05",
    styles=[
        _style(_SERIF, "Regular", Source(_CS.format("regular")),
               Source(_SH.format("Regular")), 400, False, "Regular"),
        _style(_SERIF, "Italic", Source(_CS.format("italic")),
               Source(_SH.format("Regular")), 400, True, "Italic"),
        _style(_SERIF, "Medium", Source(_CS.format("medium")),
               Source(_SH.format("Bold")), 500, False, "Medium"),
        _style(_SERIF, "MediumItalic", Source(_CS.format("mediumitalic")),
               Source(_SH.format("Bold")), 500, True, "Medium Italic"),
        # The family Bold uses Common Serif SemiBold: its stems balance
        # better with Shobhika Bold than Common Serif Bold does.
        _style(_SERIF, "Bold", Source(_CS.format("semibold")),
               Source(_SH.format("Bold")), 700, False, "Bold"),
        _style(_SERIF, "BoldItalic", Source(_CS.format("semibolditalic")),
               Source(_SH.format("Bold")), 700, True, "Bold Italic"),
    ],
)

# --- Balambika Sans ------------------------------------------------------------

_SANS = "Balambika Sans"
_SS = "source-sans-3/SourceSans3[wght].ttf"
_SSI = "source-sans-3/SourceSans3-Italic[wght].ttf"
_NSD = "noto-sans-devanagari/NotoSansDevanagari[wdth,wght].ttf"

# Latin weight -> Noto Sans Devanagari weight. Chosen so that the Devanagari
# vertical stem is about 92 % of the scaled Source Sans stem, the same
# balance as in the serif family (the headline makes Devanagari look darker).
# Measured stems at 1000 px: Source Sans x1.09 l = 48/89/108/125/160/187 for
# 300/400/500/600/700/900; Noto Sans Devanagari danda grows from 54 (300)
# to 177 (900).
SANS_DEVA_WEIGHT = {300: 245, 400: 405, 500: 505, 600: 590, 700: 745, 900: 875}
SANS_WEIGHTS = [
    (300, "Light"), (400, "Regular"), (500, "Medium"),
    (600, "SemiBold"), (700, "Bold"), (900, "Black"),
]


def _sans_styles() -> list:
    styles = []
    for weight, wname in SANS_WEIGHTS:
        deva = Source(_NSD, {"wght": SANS_DEVA_WEIGHT[weight], "wdth": 100})
        upright = "Regular" if wname == "Regular" else wname
        italic = "Italic" if wname == "Regular" else f"{wname} Italic"
        styles.append(_style(_SANS, wname, Source(_SS, {"wght": weight}), deva,
                             weight, False, upright))
        styles.append(_style(_SANS, italic.replace(" ", ""),
                             Source(_SSI, {"wght": weight}), deva,
                             weight, True, italic))
    return styles


SANS = Family(
    key="sans",
    name=_SANS,
    ps_name="BalambikaSans",
    # Source Sans 3 cap height 660 -> ~719 = Noto Sans cap height (714),
    # which is how Noto pairs its Latin with Noto Sans Devanagari.
    latin_scale=1.09,
    copyright=(
        "Copyright 2010-2020 Adobe (http://www.adobe.com/), "
        "with Reserved Font Name 'Source'. "
        "Copyright 2022 The Noto Project Authors "
        "(https://github.com/notofonts/devanagari). "
        f"Copyright 2026 {COMPILER}, "
        f'with Reserved Font Name "{RESERVED_FONT_NAME}".'
    ),
    description=(
        "Balambika Sans is a Sanskrit-oriented compilation of two OFL "
        "typefaces: Devanagari, Vedic and Devanagari Extended from Noto Sans "
        "Devanagari, and Latin, IAST transliteration and Cyrillic (Bulgarian "
        "forms by default) from Source Sans 3 by Adobe, scaled to 109%."
    ),
    version_note="Source Sans 3 3.052 + Noto Sans Devanagari 2.007",
    styles=_sans_styles(),
)

FAMILIES = [SERIF, SANS]


# --------------------------------------------------------------------------
# Helpers
# --------------------------------------------------------------------------

def deva_codepoints() -> set[int]:
    cps = set(DEVA_SINGLES)
    for lo, hi in DEVA_RANGES:
        cps.update(range(lo, hi + 1))
    return cps


def load_source(src_dir: Path, source: Source) -> TTFont:
    """Open a source font; instance a variable font at source.location."""
    font = TTFont(src_dir / source.path)
    if "fvar" in font:
        instancer.instantiateVariableFont(
            font, dict(source.location), inplace=True,
            overlap=instancer.OverlapMode.REMOVE)
        for tag in ("STAT", "MVAR", "HVAR", "VVAR", "avar", "cvar"):
            if tag in font:
                del font[tag]
    return font


def otf_to_ttf(font: TTFont, max_err: float = 1.0) -> None:
    """Convert a CFF-flavoured font to TrueType outlines in place."""
    if "glyf" in font:
        return
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


def bulgarian_glyph_map(font: TTFont) -> dict[int, str]:
    """Return {code point: glyph} for Cyrillic letters whose Bulgarian form
    differs from the default form.

    The forms are determined by shaping each letter with HarfBuzz, once with
    language=bg and once without a language, so every 'locl' lookup the font
    applies for Bulgarian is honoured, however it is organised.
    """
    import uharfbuzz as hb

    buf = io.BytesIO()
    font.save(buf)
    hb_font = hb.Font(hb.Face(buf.getvalue()))
    order = font.getGlyphOrder()

    def glyphs(text: str, lang: str | None) -> list[str]:
        b = hb.Buffer()
        b.add_str(text)
        b.direction, b.script = "ltr", "Cyrl"
        if lang:
            b.language = lang
        hb.shape(hb_font, b, {})
        return [order[info.codepoint] for info in b.glyph_infos]

    mapping = {}
    for cp in font.getBestCmap():
        if not 0x0400 <= cp <= 0x052F:
            continue
        bg, default = glyphs(chr(cp), "bg"), glyphs(chr(cp), None)
        if len(bg) == 1 and bg != default:
            mapping[cp] = bg[0]
    return mapping


def promote_bulgarian_forms(font: TTFont) -> int:
    """Point cmap entries for Cyrillic at the Bulgarian glyphs.

    The default (Russian) forms then become unreachable and are removed by
    the subsetter, together with the now-redundant Bulgarian lookups.
    """
    mapping = bulgarian_glyph_map(font)
    changed = 0
    for table in font["cmap"].tables:
        if not table.isUnicode():
            continue
        for cp in list(table.cmap):
            if cp in mapping:
                table.cmap[cp] = mapping[cp]
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


def prepare_latin(font: TTFont, exclude: set[int], scale: float) -> TTFont:
    n = promote_bulgarian_forms(font)
    log.info("  Latin: %d Cyrillic code points switched to Bulgarian forms", n)
    keep = set(font.getBestCmap()) - exclude
    subset_font(font, keep, None)
    otf_to_ttf(font)
    # Scale outlines, metrics and layout values; then restore the 1000 UPM
    # grid so the glyphs come out `scale` times larger.
    upem = font["head"].unitsPerEm
    scale_upem(font, round(upem * scale))
    font["head"].unitsPerEm = upem
    if upem != 1000:
        scale_upem(font, 1000)
    return font


def prepare_devanagari(font: TTFont, wanted: set[int]) -> TTFont:
    if font["head"].unitsPerEm != 1000:
        scale_upem(font, 1000)
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


def set_names(font: TTFont, family: Family, style: Style) -> None:
    name = font["name"]
    name.names = []
    ps_name = f"{family.ps_name}-{style.file_suffix}"
    full_name = f"{family.name} {style.typo_style}".replace(" Regular", "") \
        if style.typo_style != "Regular" else f"{family.name} Regular"
    records = {
        0: family.copyright,
        1: style.ribbi_family,
        2: style.ribbi_style,
        3: f"{VERSION};{VENDOR_ID};{ps_name}",
        4: full_name,
        5: f"Version {VERSION}; {family.version_note}",
        6: ps_name,
        10: family.description,
        13: LICENSE,
        14: LICENSE_URL,
    }
    if style.ribbi_family != family.name:
        records[16] = family.name
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


def finalize(font: TTFont, family: Family, style: Style, latin_metrics: dict,
             deva_space: int, deva_glyphs: set[str]) -> None:
    add_devanagari_space(font, deva_space, deva_glyphs)
    set_names(font, family, style)
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


def build_style(family: Family, style: Style, src: Path, out_dir: Path,
                hint: bool) -> Path:
    log.info("Building %s-%s", family.ps_name, style.file_suffix)
    deva_cps = deva_codepoints()
    latin = prepare_latin(load_source(src, style.latin), deva_cps,
                          family.latin_scale)
    deva_font = load_source(src, style.deva)
    deva_upem = deva_font["head"].unitsPerEm
    deva_space = DEVA_SPACE_WIDTH or round(
        deva_font["hmtx"]["space"][0] * 1000 / deva_upem)
    deva = prepare_devanagari(deva_font, deva_cps)

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

    # Glyphs that came only from the Devanagari source (shared names such as
    # .notdef are renamed by the merger and excluded here).
    deva_glyphs = (set(deva.getGlyphOrder()) - set(latin.getGlyphOrder())) \
        & set(merged.getGlyphOrder())
    finalize(merged, family, style, latin_metrics, deva_space, deva_glyphs)

    buf = io.BytesIO()
    merged.save(buf)
    data = buf.getvalue()
    if hint:
        try:
            data = autohint(data)
        except Exception as exc:  # keep an unhinted build rather than failing
            log.warning("  ttfautohint failed (%s); writing unhinted font", exc)

    out = out_dir / f"{family.ps_name}-{style.file_suffix}.ttf"
    out.write_bytes(data)
    log.info("  -> %s", out.relative_to(ROOT) if out.is_relative_to(ROOT) else out)
    return out


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--sources", type=Path, default=ROOT / "sources",
                    help="folder containing the source font folders")
    ap.add_argument("--family", action="append", choices=[f.key for f in FAMILIES],
                    help="build only this family; repeatable")
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
    for family in FAMILIES:
        if args.family and family.key not in args.family:
            continue
        for style in family.styles:
            if args.style and style.file_suffix not in args.style:
                continue
            build_style(family, style, args.sources, args.out,
                        hint=not args.no_autohint)
    return 0


if __name__ == "__main__":
    sys.exit(main())
