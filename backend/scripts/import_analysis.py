"""Parse a.txt and import sentence analysis data into MySQL."""
import re
import json
import asyncio
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from db import get_db, release_db


def parse_analysis_file(filepath: str) -> list[dict]:
    """Parse the a.txt file and return a list of sentence analysis dicts."""
    with open(filepath, "r", encoding="utf-8") as f:
        text = f.read()

    # Split by sentence markers
    sentence_blocks = re.split(r"\n#### 句子\d+\n", text)
    # First block is header, skip it
    sentence_blocks = sentence_blocks[1:]

    results = []
    for block in sentence_blocks:
        entry: dict = {
            "sentence_text": "",
            "connected_speech": [],
            "sense_groups_segmented": "",
            "sense_groups_explanation": "",
        }

        # Extract 原句
        m = re.search(r"\*\*原句\*\*[：:]\s*(.+?)(?:\n|$)", block)
        if m:
            entry["sentence_text"] = m.group(1).strip()

        # Split block into sections: before 连读, 连读 section, 意群 section
        # Find 连读现象分析 section
        cs_match = re.search(r"\*\*连读现象分析\*\*\s*\n(.*?)(?=\n\*\*意群切分|\Z)", block, re.DOTALL)
        if cs_match:
            cs_text = cs_match.group(1)
            # Parse each numbered item
            items = re.findall(
                r"(\d+)\.\s+\*\*(.+?)\*\*\s*(/.+?/)\s*\n\s*-\s*(.+?)(?=\n\d+\.\s+\*\*|\n\*\*意群|\Z)",
                cs_text,
                re.DOTALL,
            )
            for num, words, phonetic, desc in items:
                desc_clean = " ".join(desc.split())
                entry["connected_speech"].append({
                    "words": words.strip(),
                    "phonetic": phonetic.strip(),
                    "description": desc_clean,
                })

        # Extract 意群切分
        m = re.search(r"\*\*意群切分\*\*[：:]\s*(.+?)(?:\n|$)", block)
        if m:
            entry["sense_groups_segmented"] = m.group(1).strip()

        # Extract 划分依据
        m = re.search(r"\*\*划分依据\*\*[：:]\s*(.+?)(?:\n\s*\n|\n---|\Z)", block, re.DOTALL)
        if m:
            entry["sense_groups_explanation"] = m.group(1).strip()

        results.append(entry)

    return results


async def import_to_db(entries: list[dict]):
    """Insert parsed entries into listening_sentence_analysis table."""
    db = await get_db()
    try:
        async with db.cursor() as cur:
            # Ensure table exists
            await cur.execute("""
                CREATE TABLE IF NOT EXISTS listening_sentence_analysis (
                    sentence_text TEXT NOT NULL,
                    connected_speech JSON NOT NULL,
                    sense_groups_segmented TEXT NOT NULL,
                    sense_groups_explanation TEXT NOT NULL,
                    PRIMARY KEY (sentence_text(255))
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
            """)

            # Clear existing data
            await cur.execute("DELETE FROM listening_sentence_analysis")

            inserted = 0
            for entry in entries:
                if not entry["sentence_text"]:
                    print(f"  SKIP (no text): {entry}")
                    continue
                try:
                    await cur.execute(
                        "INSERT INTO listening_sentence_analysis (sentence_text, connected_speech, sense_groups_segmented, sense_groups_explanation) VALUES (%s, %s, %s, %s)",
                        (
                            entry["sentence_text"],
                            json.dumps(entry["connected_speech"], ensure_ascii=False),
                            entry["sense_groups_segmented"],
                            entry["sense_groups_explanation"],
                        ),
                    )
                    inserted += 1
                except Exception as e:
                    print(f"  ERROR inserting: {entry['sentence_text'][:50]}... -> {e}")

            await db.commit()
            print(f"Inserted {inserted} records.")
    finally:
        await release_db(db)


async def main():
    filepath = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "a.txt")
    print(f"Parsing: {filepath}")
    entries = parse_analysis_file(filepath)
    print(f"Parsed {len(entries)} sentence analysis entries.")
    await import_to_db(entries)
    print("Done.")


if __name__ == "__main__":
    asyncio.run(main())
