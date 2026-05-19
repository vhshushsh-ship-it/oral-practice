import asyncio
from fastapi import APIRouter, Query
from services.ai_service import query_word_ai
from services.storage_service import load_cache, save_cache

router = APIRouter(tags=["word"])


@router.post("/word/query")
async def query_word(word: str = Query(...)):
    word = word.lower().strip()
    if not word:
        return {"error": "请输入有效单词"}

    cache = load_cache()
    if word in cache:
        print(f"[CACHE HIT] {word}")
        return cache[word]

    print(f"[AI QUERY] {word}")

    max_retries = 2
    for attempt in range(max_retries):
        try:
            word_data = query_word_ai(word)
            save_cache(word, word_data)
            print(f"[CACHED] {word}")
            return word_data
        except Exception as e:
            print(f"AI第{attempt+1}次查询失败：{str(e)}")
            if attempt == max_retries - 1:
                return {"error": "单词查询失败，请重试"}
            await asyncio.sleep(0.3)
