import re
import json
from dashscope import Generation
from config import SCENE_ROLES


def clean_ai_reply(text: str) -> str:
    """清理 AI 回复中的角色标识前缀"""
    if not text:
        return text
    role_pattern = r'(?:\*+|#)?\s*(?:Waiter|服务员|Interviewer|面试官|Receptionist|前台|AI|Assistant|assistant)\s*[:：]\s*'
    cleaned = re.sub(rf'^{role_pattern}', '', text, flags=re.IGNORECASE)
    cleaned = re.sub(rf'\n\s*{role_pattern}', '\n', cleaned, flags=re.IGNORECASE)
    return cleaned.strip()


def agent_reply(user_text: str, scene: str, conversation_history: list = None, memory_context: list[str] = None, max_tokens: int = 200) -> str:
    """调用 LLM 生成场景对话回复"""
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

    try:
        response = Generation.call(
            model="qwen-turbo",
            messages=[{"role": "user", "content": prompt}],
            result_format="message",
            max_tokens=max_tokens,
            temperature=0.7,
        )
        raw_reply = response.output.choices[0].message["content"].strip()
        return clean_ai_reply(raw_reply)
    except Exception as e:
        print("[LLM ERROR]", e)
        return "Sorry, I didn't catch that. Could you repeat?"


def translate_text(text: str) -> str:
    """英文→中文翻译"""
    if not text.strip():
        return ""

    prompt = f"翻译英文为自然中文，仅输出结果：{text}"
    try:
        response = Generation.call(
            model="qwen-turbo",
            messages=[{"role": "user", "content": prompt}],
            result_format="message",
            temperature=0.1,
        )
        return response.output.choices[0].message["content"].strip()
    except Exception as e:
        print(f"[TRANSLATE ERROR] {e}")
        return "翻译出错"


def translate_to_english(text: str) -> str:
    """中文→英文翻译"""
    if not text.strip():
        return ""

    prompt = f"翻译中文为自然、地道的英文，仅输出翻译结果，不要添加其他内容：{text}"
    try:
        response = Generation.call(
            model="qwen-turbo",
            messages=[{"role": "user", "content": prompt}],
            result_format="message",
            temperature=0.1,
        )
        return response.output.choices[0].message["content"].strip()
    except Exception as e:
        print(f"[TRANSLATE ERROR] {e}")
        return "翻译出错"


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
