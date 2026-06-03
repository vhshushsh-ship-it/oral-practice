"""将 chat_records 中的后端格式对话，转为前端 DialogueScene 格式（含中文翻译和 speaker 标签）。"""
import json
import sys
import time
import io
from pathlib import Path

# 解决 Windows 终端 emoji 编码问题
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from openai import OpenAI
from config import DEEPSEEK_API_KEY, DEEPSEEK_BASE_URL, CHAT_DIR

if not DEEPSEEK_API_KEY:
    print("[ERROR] DEEPSEEK_API_KEY not configured")
    sys.exit(1)

client = OpenAI(base_url=DEEPSEEK_BASE_URL, api_key=DEEPSEEK_API_KEY)

# 场景名和角色映射
SCENE_NAMES = {
    "free_talk": "💬 自由话题畅聊",
    "restaurant": "🍽️ 餐厅点餐用餐",
    "interview": "💼 职场英文面试",
    "hotel": "🏨 酒店入住办理",
    "home_life": "🏠 日常居家交流",
    "directions": "🗺️ 出行问路乘车",
    "shopping": "🛍️ 商场购物逛街",
    "medical": "🏥 看病就医问诊",
    "campus": "🎓 校园师生交流",
    "social": "🤝 日常社交寒暄",
    "travel": "🧳 旅游出行观光",
    "workplace": "💻 职场工作沟通",
    "service": "🏦 生活服务办事",
    "phone_chat": "📱 电话微信沟通",
    "hobbies": "🎨 兴趣爱好闲聊",
    "transport": "✈️ 机场高铁出行",
    "housing": "🏠 租房看房沟通",
}

SPEAKER_LABELS = {
    "free_talk": {"assistant": "Friend", "user": "You"},
    "restaurant": {"assistant": "Waiter", "user": "You"},
    "interview": {"assistant": "Interviewer", "user": "You"},
    "hotel": {"assistant": "Receptionist", "user": "You"},
    "home_life": {"assistant": "Friend", "user": "You"},
    "directions": {"assistant": "Local", "user": "You"},
    "shopping": {"assistant": "Salesperson", "user": "You"},
    "medical": {"assistant": "Doctor", "user": "You"},
    "campus": {"assistant": "Teacher", "user": "You"},
    "social": {"assistant": "Friend", "user": "You"},
    "travel": {"assistant": "Guide", "user": "You"},
    "workplace": {"assistant": "Manager", "user": "You"},
    "service": {"assistant": "Staff", "user": "You"},
    "phone_chat": {"assistant": "Friend", "user": "You"},
    "hobbies": {"assistant": "Friend", "user": "You"},
    "transport": {"assistant": "Staff", "user": "You"},
    "housing": {"assistant": "Landlord", "user": "You"},
}


def convert_scene(scene_id: str) -> list[dict] | None:
    """调用 DeepSeek 将后端对话转为前端 turns 格式。"""
    file_path = CHAT_DIR / f"{scene_id}.json"
    if not file_path.exists():
        print(f"  [SKIP] No JSON file for {scene_id}")
        return None

    with open(file_path, "r", encoding="utf-8") as f:
        messages = json.load(f)

    speaker_map = SPEAKER_LABELS.get(scene_id, {"assistant": "Assistant", "user": "You"})

    # 构建提示词告诉 DeepSeek 每句话的 role
    msg_list = []
    for m in messages:
        label = "assistant" if m["role"] == "assistant" else "user"
        msg_list.append(f"[{label}] {m['content']}")

    msg_text = "\n".join(msg_list)

    prompt = f"""You are translating an English conversation dialogue to Chinese.

For each line below, output a JSON array of objects. Each object has these fields:
- "speaker": use "{speaker_map['assistant']}" for [assistant] lines, "{speaker_map['user']}" for [user] lines
- "en": the original English text, unchanged
- "zh": natural Chinese translation

Return ONLY a pure JSON array, no markdown, no explanation. Format:
[
  {{"speaker": "...", "en": "...", "zh": "..."}},
  ...
]

Here is the dialogue:

{msg_text}"""

    for attempt in range(3):
        try:
            response = client.chat.completions.create(
                model="deepseek-v4-flash",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3,
                max_tokens=4000,
            )
            raw = response.choices[0].message.content.strip()

            import re
            arr_match = re.search(r"\[[\s\S]*\]", raw)
            if not arr_match:
                print(f"  [WARN] No JSON array (attempt {attempt+1})")
                continue

            turns = json.loads(arr_match.group(0))

            if not isinstance(turns, list) or len(turns) < 10:
                print(f"  [WARN] Only {len(turns) if isinstance(turns, list) else 0} turns (attempt {attempt+1})")
                continue

            # 校验字段
            valid_turns = []
            for t in turns:
                if isinstance(t, dict) and all(k in t for k in ["speaker", "en", "zh"]):
                    valid_turns.append({
                        "speaker": t["speaker"],
                        "en": t["en"],
                        "zh": t["zh"],
                    })
                elif isinstance(t, dict) and "en" in t and "zh" in t:
                    # speaker 缺失时从原始数据推断
                    idx = len(valid_turns)
                    role = messages[idx]["role"] if idx < len(messages) else "user"
                    valid_turns.append({
                        "speaker": speaker_map.get(role, "You"),
                        "en": t["en"],
                        "zh": t["zh"],
                    })

            if len(valid_turns) < len(messages):
                print(f"  [WARN] Only {len(valid_turns)}/{len(messages)} valid turns")
                # 补全缺失的
                for i in range(len(valid_turns), len(messages)):
                    m = messages[i]
                    valid_turns.append({
                        "speaker": speaker_map.get(m["role"], "You"),
                        "en": m["content"],
                        "zh": "(translation missing)",
                    })

            print(f"  [OK] {len(valid_turns)} turns converted")
            return valid_turns

        except json.JSONDecodeError as e:
            print(f"  [WARN] JSON error (attempt {attempt+1}): {e}")
            continue
        except Exception as e:
            print(f"  [WARN] API error (attempt {attempt+1}): {e}")
            time.sleep(2)
            continue

    print(f"  [FAIL] Could not convert after 3 attempts")
    return None


def generate_ts_file(scenes: dict) -> str:
    """生成 TypeScript 代码字符串。"""
    lines = ["import type { DialogueScene } from '../types';\n"]
    lines.append("const defaultDialogues: DialogueScene[] = [")

    for i, (scene_id, scene_data) in enumerate(scenes.items()):
        lines.append(f"  {{")
        lines.append(f"    id: '{scene_id}',")
        lines.append(f"    name: '{scene_data['name']}',")
        lines.append(f"    turns: [")

        for j, turn in enumerate(scene_data["turns"]):
            comma = "," if j < len(scene_data["turns"]) - 1 else ""
            speaker = turn["speaker"].replace("'", "\\'")
            en = turn["en"].replace("'", "\\'")
            zh = turn["zh"].replace("'", "\\'")
            lines.append(f"      {{ speaker: '{speaker}', en: '{en}', zh: '{zh}' }}{comma}")

        lines.append(f"    ],")

        lines.append(f"  }},")

    lines.append("];")
    lines.append("")
    lines.append("export default defaultDialogues;")
    lines.append("")

    return "\n".join(lines)


def main():
    scenes = {}

    for scene_id in sorted(SPEAKER_LABELS.keys()):
        name = SCENE_NAMES.get(scene_id, scene_id)
        print(f"\n[{scene_id}] {name}")
        turns = convert_scene(scene_id)

        if turns:
            scenes[scene_id] = {"name": name, "turns": turns}
        else:
            print(f"  [SKIP] No valid data")

        time.sleep(1)

    if not scenes:
        print("[ERROR] No scenes converted")
        return

    # 生成 TypeScript 文件
    ts_content = generate_ts_file(scenes)

    # 保存为 TS 文件
    output_path = Path(__file__).resolve().parent.parent.parent / "frontend" / "src" / "data" / "sceneDialogues.ts"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(ts_content)

    # 同时保存为 JSON，方便调试
    json_output = Path(__file__).resolve().parent.parent / "data" / "scene_dialogues_frontend.json"
    with open(json_output, "w", encoding="utf-8") as f:
        json.dump(scenes, f, ensure_ascii=False, indent=2)

    print(f"\nDone! {len(scenes)} scenes written to:")
    print(f"  TS: {output_path}")
    print(f"  JSON: {json_output}")


if __name__ == "__main__":
    main()
