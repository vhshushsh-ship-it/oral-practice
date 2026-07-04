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


# ═══════════════════════════════════════════════════════════════
# 美式口语风格规则（注入所有场景对话）
# ═══════════════════════════════════════════════════════════════
_AMERICAN_SPOKEN_STYLE = """
=== AMERICAN CASUAL SPOKEN ENGLISH RULES (MUST FOLLOW) ===
1. LENGTH: 2-3 short sentences max. Each sentence ≤15 words. No long paragraphs, no complex clauses.
2. CONTRACTIONS: Use gonna, wanna, kinda, sorta, y'all, dunno, gotta, lemme, gimme, outta, ain't.
3. INTERJECTIONS: Use haha, wow, huh, right, cool, nah, sure, oh, yep, nope, uh-huh, hey naturally.
4. VOCABULARY: Everyday spoken words only. Replace formal/written words with casual equivalents. No academic or literary language.
5. TOPIC: ONE lightweight topic at a time. Don't pile on multiple questions.
6. ENDING: End with a short open-ended question to invite the user to continue. No long monologues.
7. TONE: Relaxed, casual, friendly — like texting or chatting with a close friend your age. Not a teacher or a textbook.
"""


def _build_chat_prompt(user_text: str, scene: str, conversation_history: list = None, memory_context: list[str] = None) -> str:
    """构建对话 prompt（供 streaming 和非 streaming 共用）"""
    if conversation_history is None:
        conversation_history = []

    prompt = SCENE_ROLES.get(scene, SCENE_ROLES["restaurant"]) + "\n"
    prompt += _AMERICAN_SPOKEN_STYLE + "\n"

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


def _build_analysis_prompt(text: str) -> str:
    """构建句子分析 prompt（供 analyze_sentence 和 analyze_sentence_deepseek 共用）"""
    return f"""Analyze this English sentence for connected speech and sense groups. Return ONLY valid JSON:

{{
  "connected_speech": [
    {{ "words": "...", "phonetic": "...", "description": "中文解释" }}
  ],
  "sense_groups": {{ "segmented": "... / ...", "explanation": "中文划分依据" }}
}}

Rules:
- GA American IPA, rhotic, flapped /t,d/→[ɾ], use /oʊ ɑ ɜr/ not /əʊ ɒ ɜː/
- Connected speech types: C+V linking, C+C blending, flapping, reduction (gonna/wanna), elision, intrusive R, palatalization (did you→dɪdʒə), unreleased stops
- Each item: name the rule, explain articulatory mechanism in Chinese, give connected IPA not citation form
- Sense groups: split at clause boundaries, punctuation, long subjects; keep determiner+noun, aux+verb, prep+object together; 3-8 words each
- Reduced forms: "to"→/tə/, "and"→/ən/, "of"→/əv/
- description field: Chinese, specific (e.g. "舌尖从上齿龈滑向硬腭"), no vague phrases

Sentence: "{text}" """


def _extract_json_from_response(raw: str) -> dict:
    """从 LLM 原始响应中提取并解析 JSON，支持多种容错策略"""
    if not raw or not raw.strip():
        raise ValueError("模型返回了空响应（content 为 None 或空字符串）")

    raw = raw.strip()

    # 1) 去掉 markdown 代码围栏 ```json ... ```
    raw = re.sub(r'^```(?:json)?\s*\n?', '', raw)
    raw = re.sub(r'\n?```\s*$', '', raw)

    # 2) 尝试直接解析
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        pass

    # 3) 尝试在响应中查找 JSON 对象
    m = re.search(r'\{[\s\S]*\}', raw)
    if not m:
        raise ValueError(f"响应中未找到 JSON 对象，原始内容前 300 字符: {raw[:300]}")

    candidate = m.group(0)
    # 去掉尾部多余逗号（如 "key": "value",}）
    candidate = re.sub(r',\s*([}\]])', r'\1', candidate)

    try:
        return json.loads(candidate)
    except json.JSONDecodeError:
        pass

    # 4) 尝试将 Python 风格的单引号键值转为双引号（仅替换 JSON 结构引号，保护文本内撇号）
    # 策略：用 json5 式启发法 —— 只替换跟在 {[,: 空格之后的开引号，和出现在 :, 空格之前的闭引号
    # 更稳健的做法：逐字符状态机。此处用两次保守替换：先处理键名的单引号，再处理字符串值
    try:
        # 尝试用 demjson3 或简单策略：连续两个单引号替换为空
        fixed = re.sub(r"(?<!\w)'([^']*?)'(?=\s*:)", r'"\1"', candidate)  # key: 'key' -> "key"
        fixed = re.sub(r":\s*'([^']*?)'", r': "\1"', fixed)  # value: 'val' -> "val"
        fixed = re.sub(r",\s*'([^']*?)'", r', "\1"', fixed)  # array: 'item' -> "item"
        fixed = re.sub(r"\[\s*'([^']*?)'", r'["\1"', fixed)  # first item ['item' -> ["item"
        if fixed != candidate:
            return json.loads(fixed)
    except (json.JSONDecodeError, ValueError):
        pass

    raise ValueError(f"无法解析 JSON，候选内容前 300 字符: {candidate[:300]}")


def _validate_analysis_result(result: dict) -> dict:
    """校验分析结果必填字段"""
    for k in ("connected_speech", "sense_groups"):
        if k not in result:
            raise ValueError(f"JSON 缺少必填字段: {k}")
    sg = result["sense_groups"]
    if not isinstance(sg, dict) or "segmented" not in sg or "explanation" not in sg:
        raise ValueError("sense_groups 缺少 segmented/explanation 字段")
    if not isinstance(result["connected_speech"], list):
        raise ValueError("connected_speech 必须是数组")
    return result


def _call_deepseek_for_analysis(text: str) -> dict:
    """调用 DeepSeek V4 Flash 生成句子分析（带重试）"""
    client = _get_deepseek_client()
    prompt = _build_analysis_prompt(text)

    last_exc = None
    for attempt in range(2):
        try:
            response = client.chat.completions.create(
                model="deepseek-v4-flash",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.1,
                max_tokens=4096,
                timeout=60,
            )
            raw = response.choices[0].message.content
            if not raw:
                print(f"[DEEPSEEK ANALYZE] 空 content: finish_reason={response.choices[0].finish_reason}, "
                      f"usage={response.usage}, model={response.model}")
                raise ValueError(f"DeepSeek 返回空 content: finish_reason={response.choices[0].finish_reason}")
            result = _extract_json_from_response(raw)
            return _validate_analysis_result(result)
        except Exception as e:
            last_exc = e
            if attempt < 1:  # only retry once more (2 total attempts: 0 → retry, 1 → fail)
                wait = 2 ** attempt  # 1s
                print(f"[DEEPSEEK ANALYZE] 第 {attempt + 1} 次尝试失败 ({type(e).__name__}: {e})，{wait}s 后重试...")
                import time as _time
                _time.sleep(wait)
            else:
                import traceback
                print(f"[DEEPSEEK ANALYZE ERROR] 2 次尝试全部失败。最后错误: {type(e).__name__}: {e}")
                traceback.print_exc()
    raise last_exc


def analyze_sentence_deepseek(text: str) -> dict:
    """使用 DeepSeek V4 Flash 实时分析句子连读和意群切分（失败时抛异常，由调用方处理）"""
    return _call_deepseek_for_analysis(text)


def analyze_sentence(text: str) -> dict:
    """使用 DeepSeek V4 Flash 分析句子连读现象和意群切分，返回结构化数据。
    与 analyze_sentence_deepseek 共享同一实现；失败时返回 fallback 而非抛异常。"""
    try:
        return _call_deepseek_for_analysis(text)
    except Exception as e:
        print(f"[ANALYZE ERROR] {e}")
        return {
            "connected_speech": [],
            "sense_groups": {
                "segmented": text,
                "explanation": "分析失败，请稍后重试",
            },
        }


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


def generate_sentence_hints(scene: str, scene_choice: str, messages: list) -> dict:
    """根据当前对话上下文，调用 DeepSeek V4 Flash 实时生成句型提示和核心词汇。
    返回: {"patterns": [...], "vocabulary": [...]}
    """
    # 场景中文标签映射
    scene_labels = {
        "free_talk": "英语自由交流", "restaurant": "餐厅点餐用餐",
        "interview": "职场英文面试", "hotel": "酒店入住办理",
        "home_life": "日常居家交流", "directions": "出行问路乘车",
        "shopping": "商场购物逛街", "medical": "看病就医问诊",
        "campus": "校园师生交流", "social": "日常社交寒暄",
        "travel": "旅游景点沟通", "workplace": "职场工作沟通",
        "service": "生活办事咨询", "phone_chat": "电话微信沟通",
        "hobbies": "兴趣爱好闲聊", "transport": "机场高铁出行",
        "housing": "租房看房沟通",
    }
    scene_label = scene_labels.get(scene, scene)

    # 取最近 20 条消息作为对话上下文
    recent = messages[-20:] if messages else []
    context_lines = []
    for msg in recent:
        role_label = "User" if msg["role"] == "user" else "AI Partner"
        context_lines.append(f"{role_label}: {msg['content']}")
    context_block = "\n".join(context_lines) if context_lines else "(no conversation yet — just a welcome message)"

    prompt = f"""You are an English speaking practice assistant. The user is practicing oral English in the scenario: "{scene_label}".

Below is the most recent conversation between the user and the AI speaking partner:
---
{context_block}
---

Based on the TOPICS and CONTENT of this specific conversation, generate two lists:

1. "patterns": 10-15 useful spoken English sentence patterns/phrases that are directly relevant to what the user is currently talking about. These should be natural, colloquial patterns a learner could use to continue or improve this specific conversation. Focus on the actual topics being discussed, not generic scene phrases.

2. "vocabulary": 15-20 key English vocabulary words or short phrases (1-3 words) that are relevant to the conversation topics. Include a mix of nouns, verbs, adjectives, and expressions the user might need.

Rules:
- Make everything highly contextual to the actual conversation, not generic to the scene
- If there is no conversation yet (just a welcome message), generate hints appropriate to starting a conversation in this scene
- Patterns should be complete, ready-to-use phrases, not templates with blanks
- Vocabulary should be words the user is likely to need when discussing these topics
- Keep all content in English

Return ONLY valid JSON (no markdown, no explanation):
{{"patterns": ["phrase 1", "phrase 2", ...], "vocabulary": ["word1", "word2", ...]}}"""

    try:
        client = _get_deepseek_client()
        response = client.chat.completions.create(
            model="deepseek-v4-flash",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
            max_tokens=1000,
        )
        raw = response.choices[0].message.content
        if not raw:
            raise ValueError("DeepSeek returned empty response for hints generation")
        result = _extract_json_from_response(raw)

        # Validate structure
        if "patterns" not in result or "vocabulary" not in result:
            raise ValueError("Hints response missing 'patterns' or 'vocabulary'")
        if not isinstance(result["patterns"], list) or not isinstance(result["vocabulary"], list):
            raise ValueError("Hints response fields must be arrays")

        return result
    except Exception as e:
        print(f"[HINTS GENERATE ERROR] {e}")
        raise


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
