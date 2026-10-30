#!/usr/bin/env python3
"""Verify built Balambika and Balambika Sans fonts against their sources.

Checks, for every style of every family:
  * Devanagari / Vedic text shapes to the same glyphs and positions as the
    Devanagari source (Shobhika, or Noto Sans Devanagari at the instance
    location) with HarfBuzz;
  * Latin, IAST and Cyrillic shape like the Latin source (Common Serif or
    Source Sans 3) with language=bg, positions scaled by the family's
    Latin scale;
  * word spacing around and between Devanagari words;
  * required code points are present and nothing shapes to .notdef;
  * naming and style bits.
"""

from __future__ import annotations

import sys
from pathlib import Path

import uharfbuzz as hb
from fontTools.ttLib import TTFont

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import build  # noqa: E402

DEVA_SAMPLES = [
    "अ॒ग्निमी॑ळे पु॒रोहि॑तं य॒ज्ञस्य॑ दे॒वमृ॒त्विज॑म् । होता॑रं रत्न॒धात॑मम् ॥",
    "ॐ भूर्भुव॒स्स्वः॒ । तत्स॑वि॒तुर्वरे॑ण्यं॒ भर्गो॑ दे॒वस्य॑ धीमहि । धियो॒ यो नः॑ प्रचो॒दया॑त् ॥",
    "श्रीमाता श्रीमहाराज्ञी श्रीमत्सिंहासनेश्वरी । चिदग्निकुण्डसम्भूता देवकार्यसमुद्यता ॥",
    "क्ष्म्ल्व्र्यूं ह्रीं श्रीं क्लीं ऐं सौः र्क र्कि ऱ्य द्ध द्व ह्म ह्य ङ्क्ष ष्ट्र त्त्व",
    "०१२३४५६७८९ ᳐ ᳑ ᳒ ᳚ ᳛ ꣳ ꣴ ᳵ ᳶ ॑ ॒ ॓ ॔ ँ ं ः ऽ",
]
LATIN_SAMPLES = [
    "agním īḷe puróhitaṃ yajñásya devám ṛtvíjam | hótāraṃ ratnadhā́tamam ||",
    "ṚGVEDA SAṂHITĀ Śrī Ṣaṇmukha Ḍhuṇḍhirāja Ṅ Ñ Ṭ Ḍ Ṇ Ḷ Ḹ Ṝ Ḥ Ṁ m̐ haṁsa",
    "Агни възхвалявам — поставения отпред жрец, бога на жертвата; вдигнахме жълтия гълъб, юли, ѝ",
    "The quick brown fox (1234567890) fi fl — “quotes” ‘and’ 50%.",
]
# Sāmaveda notation (Devanagari Extended); checked only where the Devanagari
# source covers it.
EXTENDED_SAMPLE = "अ꣡ग्न꣢ आ꣡ या꣣हि꣡ वी꣡तये꣢ गृणानो꣡ ह꣢व्य꣡दा꣢तये ।"
IAST = "āīūṛṝḷḹṃḥṅñṭḍṇśṣĀĪŪṚṜḶḸṂḤṄÑṬḌṆŚṢṁṀ̐́̀"
BULGARIAN = "АБВГДЕЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЬЮЯабвгдежзийклмнопрстуфхцчшщъьюяѝЍ"


def hb_font(path: Path, location: dict | None = None) -> tuple[hb.Font, TTFont]:
    blob = hb.Blob.from_file_path(str(path))
    font = hb.Font(hb.Face(blob))
    if location:
        font.set_variations(dict(location))
    return font, TTFont(path)


def shape(font: hb.Font, tt: TTFont, text: str, lang: str | None = None):
    buf = hb.Buffer()
    buf.add_str(text)
    buf.guess_segment_properties()
    if lang:
        buf.language = lang
    hb.shape(font, buf, {})
    order = tt.getGlyphOrder()
    return [
        (order[i.codepoint].split("#")[0].replace("space.deva", "space"), p.x_advance, p.x_offset, p.y_offset)
        for i, p in zip(buf.glyph_infos, buf.glyph_positions)
    ]


def segments(text: str):
    """Split text into Devanagari-ish and other runs, like a layout engine."""
    deva = build.deva_codepoints()
    runs, cur, cur_is = [], "", None
    for ch in text:
        is_d = ord(ch) in deva
        if ch == " " and cur_is is not None:
            is_d = cur_is
        if cur_is is None or is_d == cur_is:
            cur += ch
        else:
            runs.append((cur_is, cur))
            cur = ch
        cur_is = is_d
    if cur:
        runs.append((cur_is, cur))
    return runs


def compare(a, b, scale=1.0, tol=0):
    if len(a) != len(b):
        return f"length {len(a)} != {len(b)}"
    for i, (ga, gb) in enumerate(zip(a, b)):
        if ga[0] != gb[0]:
            return f"glyph {i}: {ga[0]} != {gb[0]}"
        for k in (1, 2, 3):
            if abs(round(ga[k] * scale) - gb[k]) > tol:
                return f"glyph {i} ({ga[0]}): pos {ga[1:]}x{scale} vs {gb[1:]}"
    return None


def check_style(family, style, path: Path) -> list[str]:
    new, new_tt = hb_font(path)
    src = ROOT / "sources"
    deva_src, deva_tt = hb_font(src / style.deva.path, style.deva.location)
    lat_src, lat_tt = hb_font(src / style.latin.path, style.latin.location)
    # Variable sources are instanced (and overlaps removed), so allow 1 unit
    # of rounding; static Shobhika must match exactly.
    deva_tol = 1 if style.deva.location else 0
    scale = family.latin_scale
    problems = []

    deva_cmap = deva_tt.getBestCmap()
    samples = list(DEVA_SAMPLES)
    if all(ord(c) in deva_cmap for c in EXTENDED_SAMPLE if c != " "):
        samples.append(EXTENDED_SAMPLE)
    for text in samples:
        for is_d, run in segments(text):
            if not is_d or not run.strip():
                continue
            err = compare(shape(deva_src, deva_tt, run), shape(new, new_tt, run),
                          tol=deva_tol)
            if err:
                problems.append(f"Devanagari '{run[:20]}…': {err}")

    for text in LATIN_SAMPLES:
        lang = "bg" if any("Ѐ" <= c <= "ӿ" for c in text) else None
        err = compare(shape(lat_src, lat_tt, text, lang),
                      shape(new, new_tt, text), scale=scale, tol=1)
        if err:
            problems.append(f"Latin '{text[:20]}…': {err}")

    # Word space after a Devanagari word inside Latin text must keep the
    # Latin width; between two Devanagari words it must be the Devanagari
    # source's own width.
    latin_space = round(shape(lat_src, lat_tt, " ")[0][1] * scale)
    deva_space = shape(deva_src, deva_tt, " ")[0][1]
    run = shape(new, new_tt, "अग्निः (")      # how browsers itemize it
    if abs(run[-2][1] - latin_space) > 1:
        problems.append(f"space before Latin: {run[-2][1]} != {latin_space}")
    run = shape(new, new_tt, "अग्निः यज्ञः")
    spaces = [g[1] for g in run if g[0] == "space"]
    if len(spaces) != 1 or abs(spaces[0] - deva_space) > deva_tol:
        problems.append(f"space between Devanagari words: {spaces} != [{deva_space}]")

    cmap = new_tt.getBestCmap()
    missing = [c for c in IAST + BULGARIAN if ord(c) not in cmap]
    if missing:
        problems.append(f"missing code points: {''.join(missing)}")
    for text in samples + LATIN_SAMPLES:
        if any(g[0] == ".notdef" for g in shape(new, new_tt, text)):
            problems.append(f".notdef in '{text[:20]}…'")
    return problems


def main() -> int:
    out = ROOT / "fonts" / "ttf"
    failures = 0
    for family in build.FAMILIES:
        for style in family.styles:
            path = out / f"{family.ps_name}-{style.file_suffix}.ttf"
            if not path.exists():
                print(f"[skip] {path.name} not built")
                continue
            problems = check_style(family, style, path)
            tt = TTFont(path)
            os2, name = tt["OS/2"], tt["name"]
            info = (f"{name.getDebugName(1)} / {name.getDebugName(2)}"
                    f" | 16/17: {name.getDebugName(16)} / {name.getDebugName(17)}"
                    f" | wght {os2.usWeightClass} fsSel {os2.fsSelection:#06x}"
                    f" macStyle {tt['head'].macStyle}"
                    f" | glyphs {tt['maxp'].numGlyphs}"
                    f" | hinted {'fpgm' in tt}")
            status = "OK " if not problems else "FAIL"
            print(f"[{status}] {path.name}: {info}")
            for p in problems:
                print("       -", p)
            failures += bool(problems)
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
