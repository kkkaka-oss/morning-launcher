"""
晨间启动器配置
从环境变量读取，支持 .env 文件
"""
import os
from dotenv import load_dotenv

load_dotenv()

# ========== 飞书应用配置 ==========
APP_ID = os.getenv("FEISHU_APP_ID", "cli_a9d8fc40b7e35cc9")
APP_SECRET = os.getenv("FEISHU_APP_SECRET", "aPCyuJima8IXL3qOMSksedGSqRQhatCy")
OPEN_ID = os.getenv("FEISHU_OPEN_ID", "ou_be34cea2e0cbe2474cb2b6a15000b857")

# ========== 城市配置 ==========
CITY = os.getenv("CITY", "北京")
CITY_ID = os.getenv("CITY_ID", "101010100")  # 和风天气城市代码

# ========== 天气API ==========
QWEATHER_API_KEY = os.getenv("QWEATHER_API_KEY", "eaa005014e9a4523a9b1f0d90e645033")

# ========== 推送配置 ==========
PUSH_TIME = os.getenv("PUSH_TIME", "08:00")  # 每日推送时间
TIMEZONE = os.getenv("TIMEZONE", "Asia/Shanghai")
