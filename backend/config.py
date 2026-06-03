import os
import json
import secrets
from pathlib import Path
from dotenv import load_dotenv
import chromadb

# ====================== 路径配置 ======================
BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(exist_ok=True)

env_path = BASE_DIR / ".env"
load_dotenv(dotenv_path=env_path)

DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY", "")
DEEPSEEK_BASE_URL = "https://api.deepseek.com"

# ====================== JWT 认证配置 ======================
JWT_SECRET = os.getenv("JWT_SECRET", secrets.token_hex(32))
JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
JWT_EXPIRE_HOURS = int(os.getenv("JWT_EXPIRE_HOURS", "168"))

# ====================== 邮件验证码配置 ======================
SMTP_HOST = os.getenv("SMTP_HOST", "smtp.qq.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", "465"))
SMTP_USER = os.getenv("SMTP_USER", "")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", "")
MAIL_FROM = os.getenv("MAIL_FROM", SMTP_USER)  # 发件人地址，默认同 SMTP_USER
VERIFICATION_CODE_TTL = int(os.getenv("VERIFICATION_CODE_TTL", "300"))  # 验证码有效期，默认5分钟
VERIFICATION_CODE_COOLDOWN = int(os.getenv("VERIFICATION_CODE_COOLDOWN", "60"))  # 发送冷却期，默认60秒

# ====================== ChromaDB 持久化 ======================
chroma_db_path = DATA_DIR / "chroma_db"
chroma_client = chromadb.PersistentClient(path=str(chroma_db_path))
memory_collection = chroma_client.get_or_create_collection(name="scene_talk_memory")

# ====================== 数据文件路径 ======================
CHAT_BASE_DIR = DATA_DIR / "chat_records"
CHAT_BASE_DIR.mkdir(exist_ok=True)

NOTES_BASE_DIR = DATA_DIR / "word_notes"
NOTES_BASE_DIR.mkdir(exist_ok=True)

SENTENCE_BASE_DIR = DATA_DIR / "sentence_collection"
SENTENCE_BASE_DIR.mkdir(exist_ok=True)

GRAMMAR_BASE_DIR = DATA_DIR / "grammar_history"
GRAMMAR_BASE_DIR.mkdir(exist_ok=True)

CACHE_FILE = DATA_DIR / "word_cache.json"
if not CACHE_FILE.exists():
    with open(CACHE_FILE, "w", encoding="utf-8") as f:
        json.dump({}, f, ensure_ascii=False, indent=2)

# 向后兼容旧路径
CHAT_DIR = CHAT_BASE_DIR
NOTES_FILE = DATA_DIR / "word_notes.json"

# ====================== 场景映射 ======================
SCENE_MAP = {
    "0": "free_talk",
    "1": "restaurant",
    "2": "interview",
    "3": "hotel",
    "4": "home_life",
    "5": "directions",
    "6": "shopping",
    "7": "medical",
    "8": "campus",
    "9": "social",
    "10": "travel",
    "11": "workplace",
    "12": "service",
    "13": "phone_chat",
    "14": "hobbies",
    "15": "transport",
    "16": "housing",
}

# ====================== 场景 AI 角色提示词 ======================
SCENE_ROLES = {
    "free_talk": "你是一个友好的英语聊天伙伴，全程用英文和用户交流，话题不限，可以和用户聊任何他感兴趣的内容，保持自然、口语化，像朋友一样对话，不要太正式。",
    "restaurant": "你是餐厅的服务员，全程英文，友好专业，贴合点餐场景，短句口语化。绝对禁止在回答的任何位置添加Waiter:、服务员：等任何角色标识、前缀，只输出纯对话内容，不要任何格式标记。",
    "interview": "你是英语面试官，全程英文，正式礼貌，循序渐进提问。绝对禁止在回答的任何位置添加Interviewer:、面试官：等任何角色标识、前缀，只输出纯对话内容，不要任何格式标记。",
    "hotel": "你是酒店前台，全程英文，专业友好，贴合入住场景。绝对禁止在回答的任何位置添加Receptionist:、前台：等任何角色标识、前缀，只输出纯对话内容，不要任何格式标记。",
    "home_life": "你是用户的居家朋友，全程用英文交流，聊日常居家话题（做饭、打扫、追剧、作息等），保持轻松自然，口语化，像真实朋友对话一样。",
    "directions": "你是热心的路人/工作人员，全程用英文和用户练习问路、乘车、问路线的场景，贴合出行场景，口语化，友好易懂，回答要清晰简单。",
    "shopping": "你是商场的店员/导购，全程用英文和用户交流，贴合购物场景（问商品、砍价、问价格/尺寸、退换货等），友好专业，口语化，不要太生硬。",
    "medical": "你是医生/护士，全程用英文和用户练习看病问诊场景（描述症状、问病情、听医嘱等），专业友好，语气温和，口语化，不要用太复杂的医学术语。",
    "campus": "你是学校的老师/同学，全程用英文和用户交流，贴合校园场景（上课提问、聊作业、校园活动、师生沟通等），语气自然，口语化，符合校园对话的轻松氛围。",
    "social": "你是用户的朋友，全程用英文和用户练习日常社交寒暄（打招呼、聊天气、聊近况、互相问候等），轻松自然，像真实的朋友对话一样，不要太正式。",
    "travel": "你是景点的工作人员/当地向导，全程用英文和用户交流，贴合旅游场景（问路、问景点、买票、聊旅行经历等），友好热情，口语化，回答要实用易懂。",
    "workplace": "你是职场的同事/领导/客户，全程用英文和用户练习职场沟通（开会、汇报工作、和同事对接、和客户沟通等），正式礼貌，专业得体，口语化，符合职场对话的分寸。",
    "service": "你是生活服务场所的工作人员（银行、邮局、营业厅等），全程用英文和用户练习办事咨询（办业务、问流程、咨询问题等），专业友好，口语化，回答要清晰易懂。",
    "phone_chat": "你是用户的朋友/家人/同事，全程用英文和用户练习电话/微信沟通（打电话、语音聊天、约时间、聊日常等），语气自然，像真实的线上聊天一样，不要太生硬。",
    "hobbies": "你是用户的同好伙伴，全程用英文和用户聊兴趣爱好（运动、游戏、音乐、电影、手工等），保持热情，轻松自然，口语化，主动聊相关话题。",
    "transport": "你是机场/高铁站的工作人员/乘务员，全程用英文和用户练习出行沟通（值机、安检、问路、问车次/航班、行李问题等），专业友好，口语化，回答要实用清晰。",
    "housing": "你是房东/中介/室友，全程用英文和用户练习租房看房沟通（问房源、谈价格、聊入住问题、签合同相关等），贴合租房场景，口语化，语气自然。",
    "dictionary": "你是专业英语词典，仅返回纯JSON，无任何多余文字",
}

# ====================== 场景初始欢迎语 ======================
INITIAL_MESSAGES = {
    "free_talk": "Hi there! Feel free to talk about anything you like, I'm here to chat in English!",
    "restaurant": "Hello! Welcome. What would you like to order?",
    "interview": "Hello. Please introduce yourself.",
    "hotel": "Welcome. Do you have a reservation?",
    "home_life": "Hey! What's something you usually do at home? I'd love to chat about daily life!",
    "directions": "Hi there! Need help finding a place or asking for directions?",
    "shopping": "Welcome! Looking for something specific today, or just browsing?",
    "medical": "Hello. I'm here to help you practice talking to a doctor. What's on your mind?",
    "campus": "Hi! Let's chat about school life, classes, or anything related to campus!",
    "social": "Hey! Let's practice casual small talk, like greeting people or chatting about your day!",
    "travel": "Welcome! Planning a trip? Let's practice talking about travel and tourist spots!",
    "workplace": "Hi! Let's practice professional conversations for work, like meetings or emails!",
    "service": "Hello! Need help practicing talking to staff at banks, post offices, or other services?",
    "phone_chat": "Hi! Let's practice phone or WeChat conversations, like making plans or catching up!",
    "hobbies": "Hey! What do you like to do in your free time? Let's chat about hobbies!",
    "transport": "Hi! Let's practice talking about airports, trains, or commuting!",
    "housing": "Hello! Let's practice conversations about renting apartments or talking to landlords!",
}
