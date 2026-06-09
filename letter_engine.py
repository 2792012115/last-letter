"""
AI "最后一封信" 生成引擎
核心逻辑：引导式提问 → 生成告别信 → 关系关键词云
"""

import os
import json
from dataclasses import dataclass, field
from typing import Optional
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

# ============================================================
# 配置（必须通过环境变量设置，无默认值）
# ============================================================
CLIENT = OpenAI(
    api_key=os.environ["OPENAI_API_KEY"],
    base_url=os.environ["OPENAI_BASE_URL"],
)
MODEL = os.environ.get("MODEL_NAME", "deepseek-chat")

# ============================================================
# 关系类型预设
# ============================================================
RELATIONSHIP_PRESETS = {
    "妈妈": {
        "label": "给妈妈",
        "icon": "👩",
        "tone": "温暖感恩，像小时候趴在她膝头说话的语气",
        "questions": [
            "你記憶中，媽媽為你做過最讓你鼻子一酸的小事是什麼？",
            "如果只能讓她記住你的一句話，那會是什麼？",
            "你覺得她這輩子最大的遺憾是什麼——和你有關嗎？",
            "你現在做著什麼事的時候，會突然想起她？",
        ],
    },
    "爸爸": {
        "label": "给爸爸",
        "icon": "👨",
        "tone": "深沉克制但真摯，中國式父子/父女那種不說破的深情",
        "questions": [
            "你有沒有一直想問他、但從來沒敢開口的一件事？",
            "他教會你的最重要的一個道理是什麼？",
            "你覺得他年輕時候的夢想是什麼，實現了嗎？",
            "如果明天不在了，你最想替他做完哪件事？",
        ],
    },
    "前任": {
        "label": "给前任",
        "icon": "💔",
        "tone": "溫柔但清醒，感謝相遇但不糾纏，像一本翻完的小說合上最後一頁",
        "questions": [
            "分開後你才終於明白的一件事是什麼？",
            "你們之間最好的一天，那天發生了什麼？",
            "如果重來一次，你會在什麼時候做出不同的選擇？",
            "你現在還留著TA的什麼東西？為什麼留著？",
        ],
    },
    "最好的朋友": {
        "label": "给最好的朋友",
        "icon": "🤝",
        "tone": "輕鬆真誠，像深夜路邊攤喝了三瓶啤酒之後的語氣",
        "questions": [
            "TA幫你扛過的最大的事是什麼？",
            "你們之間只屬於彼此的那個梗是什麼？",
            "如果 TA 明天不在了，你最遺憾沒一起做的事是什麼？",
            "你想替 TA 對 TA 的另一半/家人說一句什麼？",
        ],
    },
    "18岁的自己": {
        "label": "给 18 岁的自己",
        "icon": "🕰️",
        "tone": "像大哥哥/大姐姐對當年的自己說話，有心疼也有驕傲",
        "questions": [
            "18歲的你最害怕的事情是什麼？現在想告訴TA：別怕。為什麼？",
            "當年你以為天塌下來的那件事，現在還記得嗎？",
            "你最想讓 18 歲的自己提前知道的道理是什麼？",
            "現在的你有沒有活成 18 歲時期待的樣子？",
        ],
    },
    "自定义": {
        "label": "给想说话的人",
        "icon": "✉️",
        "tone": "真誠自然，像寫一封真正會寄出的信",
        "questions": [
            "這個人和你之間最難忘的一個畫面是什麼？",
            "有什麼話你攢了很久但從來沒說出口？",
            "如果這是你們最後一次對話，你最想讓TA明白什麼？",
            "你希望TA讀完這封信之後，第一反應是什麼？",
        ],
    },
}


@dataclass
class LetterSession:
    """一封信的完整会话"""
    relationship: str
    recipient_name: str = ""
    answers: list[str] = field(default_factory=list)
    questions: list[str] = field(default_factory=list)


def get_questions(relationship: str) -> list[str]:
    """根据关系类型返回引导问题"""
    preset = RELATIONSHIP_PRESETS.get(relationship, RELATIONSHIP_PRESETS["自定义"])
    return preset["questions"].copy()


def generate_letter(session: LetterSession) -> tuple[str, list[str]]:
    """
    根据用户的回答生成告别信 + 关键词列表。
    返回: (信的内容, 关键词列表)
    """

    preset = RELATIONSHIP_PRESETS.get(session.relationship, RELATIONSHIP_PRESETS["自定义"])
    tone = preset["tone"]
    icon = preset["icon"]

    # 构建 Q&A 文本
    qa_text = ""
    for q, a in zip(session.questions, session.answers):
        qa_text += f"問：{q}\n答：{a}\n\n"

    system_prompt = f"""你是一位极其擅长写情感信件的 AI 作家。你的风格是：真实、克制、有画面感，绝不煽情。

现在，一个用户正在使用 "如果明天不在了" 应用。用户选择了「{preset['label']}」{icon}。

你需要根据用户对引导问题的回答，生成一封 300-500 字的告别信。

格式要求：
1. 用繁體中文書寫（因為用戶使用繁體中文回答）
2. 不要用 "親愛的xxx" 這種開頭，直接進入畫面感
3. 每一段都以一個具體的畫面或場景開始
4. 語氣：{tone}
5. 結尾不要說教，用一個溫柔的動作或願望收束
6. 信的末尾，另起一行，输出 JSON 格式的关键词数组，格式为：{{"keywords": ["词1", "词2", ...]}}（5-8个词，用于生成词云）

用户回答：
{qa_text}

现在，请写这封信。"""

    response = CLIENT.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": "你是情感信件写作专家。用繁體中文回覆。每次回复必须包含一封信和末尾的 JSON 关键词数组。"},
            {"role": "user", "content": system_prompt},
        ],
        temperature=0.85,
        max_tokens=1500,
    )

    full_text = response.choices[0].message.content.strip()

    # 解析关键词 JSON（在信末尾）
    keywords = []
    letter_body = full_text

    # 尝试提取 JSON
    if "```json" in full_text:
        parts = full_text.split("```json")
        letter_body = parts[0].strip()
        json_part = parts[1].split("```")[0].strip()
    elif "```" in full_text:
        parts = full_text.split("```")
        # 找最后一个代码块
        letter_body = full_text[: full_text.rfind("```")].strip()
        json_part = parts[-2].strip() if len(parts) >= 2 else ""
    elif '{"keywords"' in full_text:
        idx = full_text.rfind('{"keywords"')
        letter_body = full_text[:idx].strip()
        json_part = full_text[idx:].strip()
    else:
        json_part = ""

    try:
        data = json.loads(json_part)
        keywords = data.get("keywords", [])
    except (json.JSONDecodeError, ValueError):
        keywords = []

    return letter_body, keywords


def format_letter_for_display(
    letter: str,
    keywords: list[str],
    session: LetterSession,
) -> str:
    """排版生成可截图的文字版"""
    preset = RELATIONSHIP_PRESETS.get(session.relationship, RELATIONSHIP_PRESETS["自定义"])
    icon = preset["icon"]
    label = preset["label"]

    recipient = session.recipient_name or session.relationship

    divider = "─" * 32

    output = f"""
{divider}
    {icon}  {label}
{divider}

{letter}

{divider}
"""

    if keywords:
        kw_line = " · ".join(keywords)
        output += f"\n  🏷️  {kw_line}\n"
        output += f"{divider}\n"

    output += f"""
  「如果明天不在了」
  这封信写给：{recipient}

  分享你的信 → 让更多人被温柔以待
{divider}
"""
    return output


if __name__ == "__main__":
    # 快速测试
    session = LetterSession(
        relationship="妈妈",
        recipient_name="妈妈",
        answers=[
            "小时候发烧，她背着我走了四十分钟夜路去医院，路上一直在唱歌哄我。",
            "妈，你辛苦了。",
            "她觉得没让我读更好的学校，但其实我已经很满足了。",
            "做饭的时候，总是想起她教我切菜的下午。",
        ],
    )
    session.questions = get_questions("妈妈")

    print("生成中...")
    letter, keywords = generate_letter(session)
    formatted = format_letter_for_display(letter, keywords, session)
    print(formatted)
