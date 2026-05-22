"""Batch pre-generate sentence analysis (connected speech + sense groups) for ALL scene dialogue sentences.

Processes sentences in batches of 10 per DeepSeek API call, saves to MySQL + JSON backup.
After running, the /api/listening/analyze endpoint returns instant cached results.
"""
import json
import re
import sys
import time
import io
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from openai import OpenAI
from config import DEEPSEEK_API_KEY, DEEPSEEK_BASE_URL

if not DEEPSEEK_API_KEY:
    print("[ERROR] DEEPSEEK_API_KEY not configured")
    sys.exit(1)

client = OpenAI(base_url=DEEPSEEK_BASE_URL, api_key=DEEPSEEK_API_KEY)

BATCH_SIZE = 10

# Paths
SCENE_TS = Path(__file__).resolve().parent.parent.parent / "frontend" / "src" / "data" / "sceneDialogues.ts"
BACKUP_JSON = Path(__file__).resolve().parent.parent / "data" / "scene_analysis_backup.json"

# ── Extract sentences from TS file ──
with open(SCENE_TS, "r", encoding="utf-8") as f:
    ts_content = f.read()

raw_sentences = re.findall(r"en: '(.+?)'", ts_content)
sentences = [s.replace("\\'", "'") for s in raw_sentences]
unique_sentences = sorted(set(sentences))

print(f"Total raw sentences: {len(sentences)}")
print(f"Unique sentences: {len(unique_sentences)}")
print()

# ── Batch analysis prompt ──
BATCH_PROMPT_TEMPLATE = """你是英语发音专家。请分析以下{count}句英文的连读现象和意群切分，严格返回纯JSON格式，不要加任何多余的文字、注释、markdown。

返回格式：
{{
  "results": [
    {{
      "sentence_index": 0,
      "connected_speech": [
        {{
          "words": "原文词组，如 has survived",
          "phonetic": "美式音标（American IPA），如 /həz sərˈvaɪvd/（请使用美式音标体系）",
          "description": "连读/弱读/不完全爆破现象的中文解释"
        }}
      ],
      "sense_groups": {{
        "segmented": "用 / 分隔意群的完整句子",
        "explanation": "意群切分依据的中文解释"
      }}
    }}
  ]
}}

规则：
- connected_speech 列出句子中所有连读、弱读、不完全爆破、辅元连读等现象，每条包含原词组、音标、现象解释
- sense_groups.segmented 按意群用 " / " 切分整个句子
- sense_groups.explanation 解释划分原则
- 所有解释使用中文
- 请使用美式音标体系，不要使用英式音标符号如 /ɒ/ /əʊ/ /ɪə/ /eə/ /ʊə/ /ɜː/ /ɔː/ /ɑː/ /iː/ /uː/，应使用对应的美式 /ɑ/ /oʊ/ /ɪr/ /er/ /ʊr/ /ɜr/ /ɔ/ /ɑ/ /i/ /u/

句子列表：
{sentence_list}"""


def analyze_batch(batch: list[tuple[int, str]]) -> dict[int, dict]:
    """Call DeepSeek to analyze a batch of sentences. Returns dict mapping index->analysis."""
    sentence_lines = "\n".join(f"[{idx}] {text}" for idx, text in batch)
    prompt = BATCH_PROMPT_TEMPLATE.format(count=len(batch), sentence_list=sentence_lines)

    for attempt in range(3):
        try:
            response = client.chat.completions.create(
                model="deepseek-chat",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.1,
                max_tokens=800 * len(batch),
            )
            raw = response.choices[0].message.content.strip()

            json_match = re.search(r"\{[\s\S]*\}", raw)
            if not json_match:
                print(f"  [WARN] No JSON in response (attempt {attempt+1})")
                time.sleep(2)
                continue

            clean_json = json_match.group(0)
            clean_json = re.sub(r",\s*([}\]])", r"\1", clean_json)

            try:
                data = json.loads(clean_json)
            except json.JSONDecodeError:
                clean_json = clean_json.replace("'", '"')
                try:
                    data = json.loads(clean_json)
                except json.JSONDecodeError:
                    print(f"  [WARN] JSON parse error (attempt {attempt+1})")
                    time.sleep(2)
                    continue

            results_list = data.get("results", [])
            if not results_list:
                print(f"  [WARN] Empty results (attempt {attempt+1})")
                time.sleep(2)
                continue

            # Map back to sentence text
            result_map: dict[int, dict] = {}
            for item in results_list:
                idx = item.get("sentence_index", -1)
                if idx >= 0 and "connected_speech" in item and "sense_groups" in item:
                    result_map[idx] = {
                        "connected_speech": item["connected_speech"],
                        "sense_groups": item["sense_groups"],
                    }

            missing = len(batch) - len(result_map)
            if missing > len(batch) // 2:
                print(f"  [WARN] Too many missing ({missing}/{len(batch)}) (attempt {attempt+1})")
                time.sleep(2)
                continue

            if missing > 0:
                print(f"  [WARN] {missing}/{len(batch)} sentences returned no result")

            return result_map

        except Exception as e:
            print(f"  [WARN] API error (attempt {attempt+1}): {e}")
            time.sleep(3)
            continue

    print(f"  [FAIL] Could not analyze batch after 3 attempts")
    return {}


def main():
    LOG_FILE = Path(__file__).resolve().parent.parent / "data" / "scene_analysis_log.txt"
    PROGRESS_FILE = Path(__file__).resolve().parent.parent / "data" / "scene_analysis_progress.json"

    def log(msg: str):
        print(msg, flush=True)
        with open(LOG_FILE, "a", encoding="utf-8") as lf:
            lf.write(msg + "\n")

    log(f"Starting batch analysis: {len(unique_sentences)} unique sentences, batch size {BATCH_SIZE}")
    log(f"Log file: {LOG_FILE}")

    # Load existing progress if resuming
    results: dict[str, dict] = {}
    if PROGRESS_FILE.exists():
        with open(PROGRESS_FILE, "r", encoding="utf-8") as pf:
            results = json.load(pf)
        log(f"Resuming from progress file: {len(results)} already completed")

    # Build a mapping of index->sentence for batching
    pending = [(i, s) for i, s in enumerate(unique_sentences) if s not in results]
    batches = [pending[i:i+BATCH_SIZE] for i in range(0, len(pending), BATCH_SIZE)]

    log(f"Pending sentences: {len(pending)} in {len(batches)} batches")
    log("=" * 60)

    success = len(results)
    failed: list[str] = []

    for bi, batch in enumerate(batches):
        log(f"\nBatch {bi+1}/{len(batches)} ({len(batch)} sentences):")
        for idx, text in batch:
            short = text[:70] + ("..." if len(text) > 70 else "")
            log(f"  [{idx}] {short}")

        result_map = analyze_batch(batch)
        batch_ok = 0
        for idx, text in batch:
            if idx in result_map:
                results[text] = result_map[idx]
                success += 1
                batch_ok += 1
            else:
                failed.append(text)

        log(f"  -> Got {batch_ok}/{len(batch)} analyses")

        # Save progress after each batch
        with open(PROGRESS_FILE, "w", encoding="utf-8") as pf:
            json.dump(results, pf, ensure_ascii=False)
        log(f"  [PROGRESS SAVED] Total: {success}/{len(unique_sentences)}")

        # Rate limit between batches
        if bi < len(batches) - 1:
            time.sleep(1)

    log(f"\n{'='*60}")
    log(f"Success: {success}/{len(unique_sentences)}")
    log(f"Failed: {len(failed)}")
    if failed:
        log("Failed sentences:")
        for s in failed:
            log(f"  - {s[:80]}")

    # ── Save JSON backup ──
    with open(BACKUP_JSON, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    log(f"\nJSON backup saved to: {BACKUP_JSON}")

    # ── Import to MySQL ──
    log("\nImporting to MySQL...")
    import asyncio

    async def import_to_db():
        from db import get_db, release_db

        db = await get_db()
        try:
            async with db.cursor() as cur:
                inserted = 0
                skipped = 0
                for sentence, analysis in results.items():
                    cs = analysis["connected_speech"]
                    sg = analysis["sense_groups"]
                    try:
                        await cur.execute(
                            "INSERT IGNORE INTO listening_sentence_analysis (sentence_text, connected_speech, sense_groups_segmented, sense_groups_explanation) VALUES (%s, %s, %s, %s)",
                            (
                                sentence,
                                json.dumps(cs, ensure_ascii=False),
                                sg["segmented"],
                                sg["explanation"],
                            ),
                        )
                        if cur.rowcount == 0:
                            skipped += 1
                        else:
                            inserted += 1
                    except Exception as e:
                        log(f"  ERROR inserting: {sentence[:50]}... -> {e}")

                await db.commit()
                log(f"  Inserted: {inserted}, Skipped (duplicates): {skipped}")
        finally:
            await release_db(db)

    asyncio.run(import_to_db())

    log("\nDone!")

    # Clean up progress file on success
    if PROGRESS_FILE.exists() and len(failed) == 0:
        PROGRESS_FILE.unlink()


if __name__ == "__main__":
    main()
