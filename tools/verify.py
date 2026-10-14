#!/usr/bin/env python3
"""Verify built Balambika fonts against their source fonts.

Checks, for every style:
  * Devanagari / Vedic text shapes to the same glyphs and positions as the
    source Shobhika font (HarfBuzz);
  * Latin, IAST and Cyrillic shape like the source Common Serif with
    language=bg, positions scaled by LATIN_SCALE;
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
IAST = "āīūṛṝḷḹṃḥṅñṭḍṇśṣĀĪŪṚṜḶḸṂḤṄÑṬḌṆŚṢṁṀ̐́̀"
BULGARIAN = "АБВГДЕЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЬЮЯабвгдежзийклмнопрстуфхцчшщъьюяѝЍ"


def hb_font(path: Path) -> tuple[hb.Font, TTFont]:
    blob = hb.Blob.from_file_path(str(path))
    return hb.Font(hb.Face(blob)), TTFont(path)


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
    deva = build.shobhika_codepoints()
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


def main() -> int:
    out = ROOT / "fonts" / "ttf"
    failures = 0
    for style in build.STYLES:
        path = out / f"{build.FAMILY}-{style.file_suffix}.ttf"
        if not path.exists():
            print(f"[skip] {path.name} not built")
            continue
        new, new_tt = hb_font(path)
        deva_src, deva_tt = hb_font(ROOT / "sources" / "shobhika" / style.deva_source)
        lat_src, lat_tt = hb_font(ROOT / "sources" / "common-serif" / style.latin_source)
        problems = []

        for text in DEVA_SAMPLES:
            for is_d, run in segments(text):
                if not is_d or not run.strip():
                    continue
                err = compare(shape(deva_src, deva_tt, run), shape(new, new_tt, run))
                if err:
                    problems.append(f"Devanagari '{run[:20]}…': {err}")

        for text in LATIN_SAMPLES:
            lang = "bg" if any("Ѐ" <= c <= "ӿ" for c in text) else None
            err = compare(shape(lat_src, lat_tt, text, lang),
                          shape(new, new_tt, text), scale=build.LATIN_SCALE, tol=1)
            if err:
                problems.append(f"Latin '{text[:20]}…': {err}")

        # Word space after a Devanagari word inside Latin text must keep the
        # Latin width; between two Devanagari words it must be Shobhika's.
        latin_space = round(lat_tt["hmtx"]["space"][0] * build.LATIN_SCALE)
        deva_space = deva_tt["hmtx"]["space"][0]
        run = shape(new, new_tt, "अग्निः (")      # how browsers itemize it
        if run[-2][1] != latin_space:
            problems.append(f"space before Latin: {run[-2][1]} != {latin_space}")
        run = shape(new, new_tt, "अग्निः यज्ञः")
        spaces = [g[1] for g in run if g[0] == "space"]
        if spaces != [deva_space]:
            problems.append(f"space between Devanagari words: {spaces} != [{deva_space}]")

        cmap = new_tt.getBestCmap()
        missing = [c for c in IAST + BULGARIAN if ord(c) not in cmap]
        if missing:
            problems.append(f"missing code points: {''.join(missing)}")
        for text in DEVA_SAMPLES + LATIN_SAMPLES:
            if any(g[0] == ".notdef" for g in shape(new, new_tt, text)):
                problems.append(f".notdef in '{text[:20]}…'")

        os2, name = new_tt["OS/2"], new_tt["name"]
        info = (f"{name.getDebugName(1)} / {name.getDebugName(2)}"
                f" | 16/17: {name.getDebugName(16)} / {name.getDebugName(17)}"
                f" | wght {os2.usWeightClass} fsSel {os2.fsSelection:#06x}"
                f" macStyle {new_tt['head'].macStyle}"
                f" | glyphs {new_tt['maxp'].numGlyphs}"
                f" | hinted {'fpgm' in new_tt}")
        status = "OK " if not problems else "FAIL"
        print(f"[{status}] {path.name}: {info}")
        for p in problems:
            print("       -", p)
        failures += bool(problems)
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
