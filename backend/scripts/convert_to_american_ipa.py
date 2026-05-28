"""Convert British IPA to American IPA in sentence analysis data.

USAGE:
    python scripts/convert_to_american_ipa.py --file a.txt
    python scripts/convert_to_american_ipa.py --file regenerate_all_analysis.py
    python scripts/convert_to_american_ipa.py --file fix_empty_analysis.py
    python scripts/convert_to_american_ipa.py --string "/həʊp/"
    python scripts/convert_to_american_ipa.py --check a.txt   # Dry-run, show changes only
"""

import re
import sys
import os
from pathlib import Path

# Force UTF-8 output on Windows consoles
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")


# ── Core conversion rules (applied in order) ──────────────────────
# Each rule: (pattern_regex, replacement) — operates on content between /slashes/
# Order matters: specific patterns before general ones

RULES = [
    # ── Centering diphthongs → r-colored vowels ──
    # Apply rC+r → rC first to avoid double-r (e.g., /jɪər/ → /jɪr/ not /jɪrr/)
    ("ɪər", "ɪr"),  # NEAR + r: /jɪər/ → /jɪr/
    ("eər", "er"),  # SQUARE + r: /ðeər/ → /ðer/
    ("ʊər", "ʊr"),  # CURE + r: /tʊər/ → /tʊr/
    # Then general cases
    ("ɪə", "ɪr"),   # NEAR: /nɪə/ → /nɪr/
    ("eə", "er"),   # SQUARE: /heə/ → /her/
    ("ʊə", "ʊr"),   # CURE: /tʊə/ → /tʊr/

    # ── GOAT diphthong shift (must be before /ɒ/ → /ɑ/ to avoid confusion) ──
    ("əʊ", "oʊ"),   # GOAT: /ɡəʊ/ → /ɡoʊ/

    # ── /ɒr/ → /ɔr/ (must be before /ɒ/ → /ɑ/) ──
    ("ɒr", "ɔr"),   # "orange" /ˈɒrɪndʒ/ → /ˈɔrɪndʒ/

    # ── /ɒ/ → /ɑ/ (LOT-PALM merger) ──
    ("ɒ", "ɑ"),     # LOT: /nɒt/ → /nɑt/

    # ── NURSE vowel → r-colored ──
    ("ɜː", "ɜr"),   # NURSE: /bɜːd/ → /bɜrd/

    # ── Remove phonemic length marks ──
    ("ɔː", "ɔ"),    # THOUGHT: /θɔːt/ → /θɔt/
    ("ɑː", "ɑ"),    # PALM/START: /kɑː/ → /kɑ/ (BATH fix applied later)
    ("iː", "i"),    # FLEECE: /siː/ → /si/
    ("uː", "u"),    # GOOSE: /tuː/ → /tu/
]

# ── BATH-broadening corrections (applied AFTER main rules) ──────
# In British RP, these words use /ɑː/. In American, they use /æ/.
# After the main rules, /ɑː/ → /ɑ/, so we correct /ɑ/ → /æ/ in these contexts.
BATH_PATTERNS = [
    ("ˈɑft", "ˈæft"),    # after
    ("ɑsk", "æsk"),       # ask, asked, asking
    ("pɑs", "pæs"),       # pass, past, passed, passage
    ("lɑs", "læs"),       # last
    ("dɑns", "dæns"),     # dance
    ("fɑst", "fæst"),     # fast
    ("ɡlɑs", "ɡlæs"),     # glass
    ("klɑs", "klæs"),     # class
    ("pɑθ", "pæθ"),       # path
    ("stɑf", "stæf"),     # staff
    ("tʃɑns", "tʃæns"),   # chance
    ("hɑf", "hæf"),       # half
    ("lɑf", "læf"),       # laugh
    ("rɑð", "ræð"),       # rather
    ("bɑθ", "bæθ"),       # bath
    ("ɡrɑnt", "ɡrænt"),   # grant
    ("plɑnt", "plænt"),   # plant
    ("sɑmp", "sæmp"),     # sample, example
    ("mɑst", "mæst"),     # master
    ("kɑst", "kæst"),     # cast, casting
    ("drɑft", "dræft"),   # draft
    ("kɑnt", "kænt"),     # can't (when pronounced with /ɑː/)
]


def convert_ipa_phonetic(text):
    """Convert British IPA symbols inside a /phonetic/ string to American IPA.

    Args:
        text: The full /phonetic/ string including slashes, e.g. "/həʊp/"

    Returns:
        Converted string, e.g. "/hoʊp/"
    """
    for pattern, replacement in RULES:
        text = text.replace(pattern, replacement)

    for brit, ame in BATH_PATTERNS:
        text = text.replace(brit, ame)

    return text


def convert_text(text):
    """Find all /.../ phonetic patterns in text and convert each to American IPA.

    Only matches /X/ where X does not start with a space (to avoid matching
    sense-group separators like ' / has survived / ').
    """
    return re.sub(r"/[^\s/][^/]*/", lambda m: convert_ipa_phonetic(m.group()), text)


def convert_python_file(text):
    """Convert IPA inside 'phonetic' field values in Python source files.

    Matches "phonetic": "/.../" specifically to avoid false positives
    on sense_groups.segmented fields which use / as separators.
    """
    def replace_phonetic_field(match):
        prefix = match.group(1)  # "phonetic": "
        phonetic = match.group(2)  # /.../
        converted = convert_ipa_phonetic(phonetic)
        return prefix + converted

    return re.sub(
        r'("phonetic":\s*")(/[^/]+/)"',
        replace_phonetic_field,
        text,
    )


def convert_python_file_apply(text):
    """Same as convert_python_file but handles the closing quote properly."""
    def replace_full(match):
        prefix = match.group(1)  # "phonetic": "
        phonetic = match.group(2)  # /.../
        closing = match.group(3)  # "
        converted = convert_ipa_phonetic(phonetic)
        return prefix + converted + closing

    return re.sub(
        r'("phonetic":\s*")(/[^"]+?)(")',
        replace_full,
        text,
    )


# ── CLI ────────────────────────────────────────────────────────────

def process_file(filepath, dry_run=False):
    """Convert a file in place. Supports .txt, .py, and .json files."""
    path = Path(filepath)
    if not path.exists():
        print(f"ERROR: File not found: {filepath}")
        sys.exit(1)

    original = path.read_text(encoding="utf-8")

    ext = path.suffix.lower()
    if ext == ".py":
        # First convert "phonetic" field values precisely,
        # then convert any remaining /.../ patterns in descriptions
        converted = convert_python_file_apply(original)
        converted = convert_text(converted)
    else:
        converted = convert_text(original)

    # Safety fallback: direct str.replace for core Br→Am patterns
    # Ensures patterns missed by regex (e.g., /ɒ/ in complex contexts) are caught
    FALLBACKS = [
        ("/əʊ/", "/oʊ/"),
        ("/ɒ/", "/ɑ/"),
        ("/ɪə/", "/ɪr/"),
        ("/eə/", "/er/"),
        ("/ʊə/", "/ʊr/"),
        ("/ɜː/", "/ɜr/"),
        ("/ɔː/", "/ɔ/"),
        ("/ɑː/", "/ɑ/"),
        ("/iː/", "/i/"),
        ("/uː/", "/u/"),
    ]
    for brit, ame in FALLBACKS:
        converted = converted.replace(brit, ame)

    if original == converted:
        print(f"No changes needed in: {filepath}")
        return

    # Count changes
    original_ipa = re.findall(r"/[^\s/][^/]*/", original)
    converted_ipa = re.findall(r"/[^\s/][^/]*/", converted)
    changed = sum(1 for o, c in zip(original_ipa, converted_ipa) if o != c)
    print(f"Changes in {filepath}: {changed} phonetics converted")

    if dry_run:
        for o, c in zip(original_ipa, converted_ipa):
            if o != c:
                print(f"  {o}  →  {c}")
        return

    path.write_text(converted, encoding="utf-8")
    print(f"Saved: {filepath}")


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(0)

    dry_run = False
    args = sys.argv[1:]

    if "--check" in args:
        dry_run = True
        args.remove("--check")

    if "--file" in args:
        idx = args.index("--file")
        filepath = args[idx + 1]
        process_file(filepath, dry_run=dry_run)

    elif "--string" in args:
        idx = args.index("--string")
        text = args[idx + 1]
        result = convert_ipa_phonetic(text)
        print(f"Input:  {text}")
        print(f"Output: {result}")

    else:
        print(__doc__)


if __name__ == "__main__":
    main()
