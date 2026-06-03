import re
import json
from openai import OpenAI
from config import SCENE_ROLES, DEEPSEEK_API_KEY, DEEPSEEK_BASE_URL


def _get_deepseek_client() -> OpenAI:
    """Get a DeepSeek OpenAI-compatible client."""
    if not DEEPSEEK_API_KEY:
        raise ValueError("DEEPSEEK_API_KEY not configured")
    return OpenAI(base_url=DEEPSEEK_BASE_URL, api_key=DEEPSEEK_API_KEY)


def clean_ai_reply(text: str) -> str:
    """清理 AI 回复中的角色标识前缀"""
    if not text:
        return text
    role_pattern = r'(?:\*+|#)?\s*(?:Waiter|服务员|Interviewer|面试官|Receptionist|前台|AI|Assistant|assistant)\s*[:：]\s*'
    cleaned = re.sub(rf'^{role_pattern}', '', text, flags=re.IGNORECASE)
    cleaned = re.sub(rf'\n\s*{role_pattern}', '\n', cleaned, flags=re.IGNORECASE)
    return cleaned.strip()


def _build_chat_prompt(user_text: str, scene: str, conversation_history: list = None, memory_context: list[str] = None) -> str:
    """构建对话 prompt（供 streaming 和非 streaming 共用）"""
    if conversation_history is None:
        conversation_history = []

    prompt = SCENE_ROLES.get(scene, SCENE_ROLES["restaurant"]) + "\n"

    if memory_context:
        prompt += "\nHere are relevant past conversations in this scene for context:\n"
        for mem in memory_context:
            prompt += f"- {mem}\n"
        prompt += "\n---\n\n"

    for msg in conversation_history:
        if msg["role"] == "user":
            prompt += f"User: {msg['content']}\n"
        elif msg["role"] == "assistant":
            prompt += f"You: {msg['content']}\n"
    prompt += f"User: {user_text}\nYou: "

    return prompt


def agent_reply(user_text: str, scene: str, conversation_history: list = None, memory_context: list[str] = None, max_tokens: int = 200) -> str:
    """调用 DeepSeek V4 Flash 生成场景对话回复"""
    prompt = _build_chat_prompt(user_text, scene, conversation_history, memory_context)

    try:
        client = _get_deepseek_client()
        response = client.chat.completions.create(
            model="deepseek-v4-flash",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=max_tokens,
            temperature=0.7,
        )
        raw_reply = response.choices[0].message.content.strip()
        return clean_ai_reply(raw_reply)
    except Exception as e:
        print("[LLM ERROR]", e)
        return "Sorry, I didn't catch that. Could you repeat?"


def agent_reply_stream(user_text: str, scene: str, conversation_history: list = None, memory_context: list[str] = None, max_tokens: int = 200):
    """流式调用 DeepSeek V4 Flash 生成场景对话回复，逐 token yield"""
    prompt = _build_chat_prompt(user_text, scene, conversation_history, memory_context)

    client = _get_deepseek_client()
    response = client.chat.completions.create(
        model="deepseek-v4-flash",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=max_tokens,
        temperature=0.7,
        stream=True,
    )

    for chunk in response:
        if chunk.choices and chunk.choices[0].delta.content:
            token = chunk.choices[0].delta.content
            yield token


def translate_text(text: str) -> str:
    """英文→中文翻译"""
    if not text.strip():
        return ""

    prompt = f"翻译英文为自然中文，仅输出结果：{text}"
    try:
        client = _get_deepseek_client()
        response = client.chat.completions.create(
            model="deepseek-v4-flash",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.1,
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        print(f"[TRANSLATE ERROR] {e}")
        return "翻译出错"


def translate_to_english(text: str) -> str:
    """中文→英文翻译"""
    if not text.strip():
        return ""

    prompt = f"翻译中文为自然、地道的英文，仅输出翻译结果，不要添加其他内容：{text}"
    try:
        client = _get_deepseek_client()
        response = client.chat.completions.create(
            model="deepseek-v4-flash",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.1,
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        print(f"[TRANSLATE ERROR] {e}")
        return "翻译出错"


def analyze_sentence(text: str) -> dict:
    """使用 DeepSeek V4 Flash 分析句子连读现象和意群切分，返回结构化数据"""
    client = _get_deepseek_client()

    prompt = f"""你是英语发音专家。请分析以下英文句子的连读现象和意群切分，严格返回纯JSON格式，不要加任何多余的文字、注释、markdown：

{{
  "connected_speech": [
    {{
      "words": "原文词组，如 has survived",
      "phonetic": "美式音标（American IPA），如 /həz sərˈvaɪvd/（注意：请使用美式音标体系，不要使用英式音标符号如 /ɒ/ /əʊ/ /ɪə/ /eə/ /ʊə/ /ɜː/ /ɔː/ /ɑː/ /iː/ /uː/，应使用对应的美式 /ɑ/ /oʊ/ /ɪr/ /er/ /ʊr/ /ɜr/ /ɔ/ /ɑ/ /i/ /u/）",
      "description": "连读/弱读/不完全爆破现象的中文解释，说明具体发生了什么音变，如：/z/ 与 /s/ 相邻，可连成轻微延长或短暂停顿（避免吞音）"
    }}
  ],
  "sense_groups": {{
    "segmented": "用 / 分隔意群的完整句子",
    "explanation": "意群切分依据的中文解释，说明为什么这样划分，以及英语母语者朗读时的停顿规律"
  }}
}}

规则：
- connected_speech 列出句子中所有连读、弱读、不完全爆破、辅元连读等现象，每条包含原词组、音标、现象解释
- sense_groups.segmented 按意群用 " / " 切分整个句子
- sense_groups.explanation 解释划分原则
- 所有解释使用中文

句子：{text}"""
    try:
        response = client.chat.completions.create(
            model="deepseek-v4-flash",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.1,
            max_tokens=800,
        )
        raw = response.choices[0].message.content.strip()

        json_match = re.search(r"\{[\s\S]*\}", raw)
        if not json_match:
            raise ValueError("AI未返回JSON格式")

        clean_json = json_match.group(0)
        clean_json = re.sub(r",\s*([}\]])", r"\1", clean_json)

        try:
            result = json.loads(clean_json)
        except json.JSONDecodeError:
            clean_json = clean_json.replace("'", '"')
            result = json.loads(clean_json)

        if "connected_speech" not in result or "sense_groups" not in result:
            raise ValueError("JSON缺少必填字段")

        return result
    except Exception as e:
        print(f"[ANALYZE ERROR] {e}")
        return {
            "connected_speech": [],
            "sense_groups": {
                "segmented": text,
                "explanation": "分析失败，请稍后重试",
            },
        }


def analyze_sentence_deepseek(text: str) -> dict:
    """使用 DeepSeek V4 Flash 实时分析句子连读和意群切分"""
    client = _get_deepseek_client()

    prompt = f"""你是英语发音专家。请分析以下英文句子的连读现象和意群切分，严格返回纯JSON格式，不要加任何多余的文字、注释、markdown：

{{
  "connected_speech": [
    {{
      "words": "原文词组，如 has survived",
      "phonetic": "美式音标（American IPA），如 /həz sərˈvaɪvd/（注意：请使用美式音标体系，不要使用英式音标符号如 /ɒ/ /əʊ/ /ɪə/ /eə/ /ʊə/ /ɜː/ /ɔː/ /ɑː/ /iː/ /uː/，应使用对应的美式 /ɑ/ /oʊ/ /ɪr/ /er/ /ʊr/ /ɜr/ /ɔ/ /ɑ/ /i/ /u/）",
      "description": "连读/弱读/不完全爆破现象的中文解释，说明具体发生了什么音变，如：/z/ 与 /s/ 相邻，可连成轻微延长或短暂停顿（避免吞音）"
    }}
  ],
  "sense_groups": {{
    "segmented": "用 / 分隔意群的完整句子",
    "explanation": "意群切分依据的中文解释，说明为什么这样划分，以及英语母语者朗读时的停顿规律"
  }}
}}

规则：
- connected_speech 列出句子中所有连读、弱读、不完全爆破、辅元连读等现象，每条包含原词组、音标、现象解释
- sense_groups.segmented 按意群用 " / " 切分整个句子
- sense_groups.explanation 解释划分原则
- 所有解释使用中文

句子：{text}"""

    try:
        response = client.chat.completions.create(
            model="deepseek-v4-flash",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.1,
            max_tokens=800,
        )
        raw = response.choices[0].message.content.strip()

        json_match = re.search(r"\{[\s\S]*\}", raw)
        if not json_match:
            raise ValueError("DeepSeek未返回JSON格式")

        clean_json = json_match.group(0)
        clean_json = re.sub(r",\s*([}\]])", r"\1", clean_json)

        try:
            result = json.loads(clean_json)
        except json.JSONDecodeError:
            clean_json = clean_json.replace("'", '"')
            result = json.loads(clean_json)

        if "connected_speech" not in result or "sense_groups" not in result:
            raise ValueError("JSON缺少必填字段")

        return result
    except Exception as e:
        print(f"[DEEPSEEK ANALYZE ERROR] {e}")
        raise


def check_grammar_deepseek(text: str) -> dict:
    """使用 DeepSeek V4 Flash 进行语法检测和打分（极速轻量模型）"""
    client = _get_deepseek_client()

    # Truncate very long input to avoid overwhelming the model
    MAX_INPUT_CHARS = 500
    if len(text) > MAX_INPUT_CHARS:
        text = text[:MAX_INPUT_CHARS] + "..."

    # Compact prompt — grammar check output is ~200-400 tokens
    prompt = (
        "Check grammar of this English sentence. Return ONLY valid JSON (no markdown):\n"
        '{"score":int(0-100),"source_sent":"<original>","error_index":[[start,end],...],"error_info":[{"error_text":"...","error_type":"tense/SVA/prep/article/word_order/spelling","explain":"Chinese explanation"}],"fixed_sent":"<corrected>"}\n'
        "Rules: casual spoken contractions OK (gonna/wanna). Score: 0 errors=95-100, 1 err=-5~10, 2-3 err=-15~30, 4+ err=-35~60.\n"
        f"Sentence: {text}"
    )

    def _try_parse(raw: str) -> dict:
        """Extract and parse JSON from model response"""
        raw = raw.strip()
        # Remove markdown code fences
        raw = re.sub(r'^```(?:json)?\s*\n?', '', raw)
        raw = re.sub(r'\n?```\s*$', '', raw)
        # Try direct parse first
        try:
            return json.loads(raw)
        except json.JSONDecodeError:
            pass
        # Try to find JSON object in response, fix trailing commas
        m = re.search(r'\{[\s\S]*\}', raw)
        if m:
            candidate = m.group(0)
            candidate = re.sub(r',\s*([}\]])', r'\1', candidate)
            return json.loads(candidate)
        raise ValueError(f"Cannot extract JSON from response: {raw[:200]}")

    def _validate(result: dict) -> dict:
        for k in ("score", "source_sent", "error_index", "error_info", "fixed_sent"):
            if k not in result:
                raise ValueError(f"JSON missing field: {k}")
        return result

    import time as _time
    last_exc = None
    for attempt in range(3):
        try:
            response = client.chat.completions.create(
                model="deepseek-v4-flash",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.1,
                max_tokens=1024,
                timeout=30,
            )
            raw = response.choices[0].message.content
            if not raw:
                raise ValueError(f"DeepSeek empty response: finish_reason={response.choices[0].finish_reason}")
            result = _try_parse(raw)
            return _validate(result)
        except Exception as e:
            last_exc = e
            if attempt < 2:
                wait = 2 ** attempt  # 1s, 2s
                print(f"[GRAMMAR CHECK] Attempt {attempt + 1} failed ({type(e).__name__}: {e}), retrying in {wait}s...")
                _time.sleep(wait)
            else:
                import traceback
                print(f"[GRAMMAR CHECK ERROR] All 3 attempts failed. Last: {type(e).__name__}: {e}")
                traceback.print_exc()
    raise last_exc


def query_word_ai(word: str) -> dict:
    """调用 AI 查询单词释义，返回结构化数据"""
    prompt = f"""
你是专业英语词典，严格只返回纯JSON格式，不要加任何多余的文字、注释、markdown：
{{
  "word": "{word}",
  "phonetic": "美式音标，比如/əˈmeɪkə/",
  "meanings": [
    {{
      "part_of_speech": "词性缩写，比如adj./n./v.",
      "definition": "中文核心释义",
      "example": "英文例句|中文翻译"
    }}
  ]
}}
"""
    raw_result = agent_reply(prompt, "dictionary", [], max_tokens=500)

    json_match = re.search(r"\{[\s\S]*\}", raw_result)
    if not json_match:
        raise ValueError("AI未返回JSON格式")

    clean_json = json_match.group(0)
    clean_json = re.sub(r",\s*([}\]])", r"\1", clean_json)

    try:
        word_data = json.loads(clean_json)
    except json.JSONDecodeError:
        clean_json = clean_json.replace("'", '"')
        word_data = json.loads(clean_json)

    if not all(key in word_data for key in ["word", "phonetic", "meanings"]):
        raise ValueError("JSON缺少必填字段")

    return word_data
