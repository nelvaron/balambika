#!/usr/bin/env python3
"""Shape the conjuncts shown on the site with HarfBuzz and record glyph counts.

Writes src/data/conjuncts.json. Re-run after the font changes:

    pip install uharfbuzz
    python3 site/scripts/shape-data.py

Each conjunct is shaped four times, adding OpenType features stage by stage,
exactly as the "Shaping, step by step" control on the home page does with
font-feature-settings in the browser.
"""
import json
from pathlib import Path

import uharfbuzz as hb

ROOT = Path(__file__).resolve().parents[2]
FONT = ROOT / "fonts/ttf/Balambika-Regular.ttf"
OUT = ROOT / "site/src/data/conjuncts.json"

# Feature values per stage; must match STAGES in src/data/shaping.ts.
LIGATURES = ["akhn", "pres", "cjct", "abvs", "blws", "psts"]
FORMS = ["half", "haln", "rphf", "rkrf", "pref", "blwf", "vatu", "pstf", "cfar"]
STAGES = [
    {f: False for f in LIGATURES + FORMS},          # code points
    {f: False for f in LIGATURES},                  # half and below-base forms
    {f: False for f in LIGATURES if f != "akhn"},   # akhand ligatures
    {},                                             # full shaping
]

# (conjunct, IAST, example word, IAST of word, gloss en, gloss bg)
CONJUNCTS = [
    ("क्ष", "kṣa", "क्षेत्र", "kṣetra", "field", "поле"),
    ("ज्ञ", "jña", "ज्ञान", "jñāna", "knowledge", "знание"),
    ("त्र", "tra", "मन्त्र", "mantra", "sacred formula", "свещена формула"),
    ("श्र", "śra", "श्री", "śrī", "radiance", "сияние"),
    ("द्ध", "ddha", "बुद्धि", "buddhi", "intellect", "разум"),
    ("द्य", "dya", "विद्या", "vidyā", "lore", "знание, учение"),
    ("द्व", "dva", "द्वार", "dvāra", "door", "врата"),
    ("ह्म", "hma", "ब्रह्मन्", "brahman", "the absolute", "абсолютът"),
    ("ह्य", "hya", "गुह्य", "guhya", "secret", "тайно"),
    ("ङ्ग", "ṅga", "गङ्गा", "gaṅgā", "the Ganges", "Ганг"),
    ("ञ्च", "ñca", "पञ्च", "pañca", "five", "пет"),
    ("ण्ड", "ṇḍa", "कुण्ड", "kuṇḍa", "fire pit", "огнище"),
    ("न्द्र", "ndra", "इन्द्र", "indra", "Indra", "Индра"),
    ("स्त्र", "stra", "शास्त्र", "śāstra", "treatise", "трактат"),
    ("ष्ट्र", "ṣṭra", "राष्ट्र", "rāṣṭra", "realm", "държава"),
    ("त्त्व", "ttva", "तत्त्व", "tattva", "principle", "принцип"),
    ("श्च", "śca", "पश्चिम", "paścima", "west", "запад"),
    ("त्स्य", "tsya", "मत्स्य", "matsya", "fish", "риба"),
    ("श्व", "śva", "ईश्वर", "īśvara", "lord", "господар"),
    ("ङ्ख्य", "ṅkhya", "साङ्ख्य", "sāṅkhya", "Sāṅkhya", "санкхя"),
    ("ह्ण", "hṇa", "अपराह्ण", "aparāhṇa", "afternoon", "следобед"),
    ("र्ध्व", "rdhva", "ऊर्ध्व", "ūrdhva", "upward", "нагоре"),
    ("क्ष्म्य", "kṣmya", "लक्ष्म्या", "lakṣmyā", "by Lakṣmī", "чрез Лакшми"),
    ("र्त्स्न्य", "rtsnya", "कार्त्स्न्य", "kārtsnya", "entirety", "цялост"),
]

STRESS = ["द्ध्र्य", "ङ्क्ष्व", "ष्ट्र्य", "न्त्र्य", "स्फ्र", "ग्ध्र", "क्त्र्य", "ड्ढ"]

blob = hb.Blob.from_file_path(str(FONT))
face = hb.Face(blob)
font = hb.Font(face)


def shape(text, features):
    buf = hb.Buffer()
    buf.add_str(text)
    buf.guess_segment_properties()
    hb.shape(font, buf, features)
    return [font.glyph_to_string(i.codepoint) for i in buf.glyph_infos]


def entry(text):
    return {
        "cps": [f"U+{ord(c):04X}" for c in text],
        "names": [__import__("unicodedata").name(c, "?").title() for c in text],
        "stages": [len(shape(text, s)) for s in STAGES],
        "glyphs": shape(text, {}),
    }


data = {
    "conjuncts": [
        {"c": c, "iast": iast, "word": w, "wordIast": wi, "gloss": {"en": en, "bg": bg}, **entry(c)}
        for c, iast, w, wi, en, bg in CONJUNCTS
    ],
    "stress": [{"c": c, **entry(c)} for c in STRESS],
}
OUT.write_text(json.dumps(data, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
print(f"wrote {OUT.relative_to(ROOT)}")
for item in data["conjuncts"] + data["stress"]:
    print(item["c"], item["stages"], item["glyphs"])
