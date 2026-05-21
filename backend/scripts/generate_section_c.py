"""Generate Section C analysis via LLM, append to a.txt, and re-import."""
import re
import json
import asyncio
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from db import get_db, release_db
from services.ai_service import analyze_sentence

A_TXT_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
    "a.txt",
)

SECTION_C_HEADER = """

## Section C: Passages
"""


def format_connected_speech(items: list) -> str:
    lines = ["**连读现象分析**"]
    for i, item in enumerate(items, 1):
        lines.append(
            f"{i}.  **{item['words']}** {item['phonetic']}\n"
            f"    - {item['description']}"
        )
    return "\n".join(lines)


def format_entry(
    item_name: str,
    sentence_num: int,
    en: str,
    zh: str,
    analysis: dict,
) -> str:
    cs = format_connected_speech(analysis["connected_speech"])
    sg = analysis["sense_groups"]
    return f"""### {item_name}
#### 句子{sentence_num}
**原句**：{en}
**翻译**：{zh}

{cs}

**意群切分**：{sg["segmented"]}
**划分依据**：{sg["explanation"]}

---
"""


async def main():
    db = await get_db()
    try:
        async with db.cursor() as cur:
            await cur.execute(
                """
                SELECT ls.id, ls.en, ls.zh, li.name AS item_name,
                       li.id AS item_id, ls.sort_order
                FROM listening_sentence ls
                LEFT JOIN listening_item li ON li.id = ls.item_id
                WHERE ls.set_id = 'cet4-2025-12'
                  AND ls.section_id = 'cet4-2025-12-secC'
                ORDER BY li.sort_order, ls.sort_order
                """
            )
            sentences = list(await cur.fetchall())
    finally:
        await release_db(db)

    # Group by item
    items: dict[str, list[dict]] = {}
    for s in sentences:
        item_name = s[3] or "Passage"
        items.setdefault(item_name, []).append(s)

    print(f"Found {len(sentences)} sentences in {len(items)} items.")

    total = len(sentences)
    done = 0

    with open(A_TXT_PATH, "a", encoding="utf-8") as f:
        f.write(SECTION_C_HEADER)

        for item_name in ["Passage One", "Passage Two", "Passage Three"]:
            if item_name not in items:
                print(f"  SKIP {item_name}: not found")
                continue
            f.write(f"\n### {item_name}\n")
            for idx, s in enumerate(items[item_name], 1):
                s_id, en, zh, _, item_id, sort_order = s
                print(f"  [{done+1}/{total}] Analyzing: {en[:80]}...")
                try:
                    analysis = analyze_sentence(en)
                    if isinstance(analysis, dict) and "connected_speech" in analysis:
                        entry = format_entry(item_name, idx, en, zh, analysis)
                        f.write(entry)
                        done += 1
                        print(f"    OK ({len(analysis['connected_speech'])} cs items)")
                    else:
                        print(f"    FAIL: unexpected response type: {type(analysis)}")
                except Exception as e:
                    print(f"    ERROR: {e}")

    print(f"\nGenerated {done}/{total} entries. Appended to {A_TXT_PATH}")


if __name__ == "__main__":
    asyncio.run(main())
