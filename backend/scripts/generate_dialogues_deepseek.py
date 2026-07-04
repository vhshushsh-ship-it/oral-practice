"""使用 DeepSeek 模型为所有场景自动生成 20 条对话，保存到 chat_records 目录。"""
import json
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from openai import OpenAI
from config import (
    DEEPSEEK_API_KEY, DEEPSEEK_BASE_URL,
    SCENE_MAP, SCENE_ROLES, INITIAL_MESSAGES, CHAT_DIR
)

if not DEEPSEEK_API_KEY:
    print("[ERROR] DEEPSEEK_API_KEY not configured in .env file")
    sys.exit(1)

client = OpenAI(base_url=DEEPSEEK_BASE_URL, api_key=DEEPSEEK_API_KEY)

SCENES = list(SCENE_MAP.values())


def generate_scene_dialogue(scene: str) -> list[dict]:
    """调用 DeepSeek 生成一个场景的完整 20 条对话。"""
    initial_msg = INITIAL_MESSAGES.get(scene, "Hello! How can I help you?")
    role_desc = SCENE_ROLES.get(scene, SCENE_ROLES["restaurant"])

    prompt = f"""{role_desc}

请你以 AI 助教和英语学习者的身份，生成一段完整的英语情景对话练习，场景是"{scene}"。

要求：
1. 对话共 20 条消息，严格按照 JSON 数组格式输出，每条消息包含 role 和 content 字段
2. role 只能是 "assistant"（AI助教）或 "user"（英语学习者）
3. 第 1 条必须是 assistant，内容为欢迎语，需要和以下欢迎语一致或意思相近："{initial_msg}"
4. 之后 assistant 和 user 交替对话，即 role 顺序为：assistant, user, assistant, user, ...
5. assistant 的回复要贴合场景角色，短句口语化，每条约 2-4 句，长度适中
6. user 的回复模拟一个中等水平的英语学习者，偶尔用词简单或有小语法瑕疵，但整体可理解，每条约 1-3 句
7. 对话要有自然的起承转合，涵盖该场景的典型会话内容，不要突兀结束
8. 对话中 assistant 绝对禁止在内容里添加任何角色标识前缀（如 Assistant:、Waiter: 等），只输出纯对话内容
9. 输出必须是纯净的 JSON 数组，不要有任何 markdown 标记、注释或额外说明文字

示例格式：
[
  {{"role": "assistant", "content": "欢迎语..."}},
  {{"role": "user", "content": "用户回复..."}},
  {{"role": "assistant", "content": "助理回复..."}},
  ...
  {{"role": "user", "content": "最后一条用户回复..."}}
]

总共 20 条，不多不少。"""

    for attempt in range(3):
        try:
            response = client.chat.completions.create(
                model="deepseek-v4-flash",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.8,
                max_tokens=4000,
            )
            raw = response.choices[0].message.content.strip()

            json_match = None
            import re
            # 尝试匹配 JSON 数组
            arr_match = re.search(r"\[[\s\S]*\]", raw)
            if arr_match:
                json_match = arr_match.group(0)

            if not json_match:
                print(f"  [WARN] No JSON array found in response, retry {attempt+1}")
                continue

            dialogue = json.loads(json_match)

            if not isinstance(dialogue, list):
                print(f"  [WARN] Response is not a list, retry {attempt+1}")
                continue

            valid = []
            for item in dialogue:
                if isinstance(item, dict) and "role" in item and "content" in item:
                    r = item["role"].strip().lower()
                    if r in ("user", "assistant"):
                        valid.append({"role": r, "content": item["content"].strip()})

            if len(valid) < 10:
                print(f"  [WARN] Only {len(valid)} valid messages, retry {attempt+1}")
                continue

            # 确保第一条是 assistant
            if valid and valid[0]["role"] != "assistant":
                valid.insert(0, {"role": "assistant", "content": initial_msg})

            # 截取前 20 条
            valid = valid[:20]
            print(f"  [OK] {len(valid)} messages generated")
            return valid

        except json.JSONDecodeError as e:
            print(f"  [WARN] JSON parse error (attempt {attempt+1}): {e}")
            continue
        except Exception as e:
            print(f"  [WARN] API error (attempt {attempt+1}): {e}")
            time.sleep(2)
            continue

    print(f"  [FAIL] Could not generate dialogue after 3 attempts")
    return []


def main():
    print(f"Generating dialogues for {len(SCENES)} scenes using DeepSeek...\n")

    for i, scene in enumerate(SCENES, 1):
        print(f"[{i}/{len(SCENES)}] {scene} ...")
        dialogue = generate_scene_dialogue(scene)

        if dialogue:
            file_path = CHAT_DIR / f"{scene}.json"
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(dialogue, f, ensure_ascii=False, indent=2)
        else:
            print(f"  [SKIP] No valid dialogue for {scene}")

        # 避免请求太快
        if i < len(SCENES):
            time.sleep(1)

    print(f"\nDone! Files saved to {CHAT_DIR}")


if __name__ == "__main__":
    main()
