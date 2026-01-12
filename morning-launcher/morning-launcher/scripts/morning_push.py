"""
晨间工作启动器 - 主推送脚本
整合天气、穿搭、日历，生成并推送晨间概览
"""
import os
from datetime import datetime

from config import CITY
from feishu_calendar import (
    get_today_events, get_tomorrow_events,
    get_mock_today_events, get_mock_tomorrow_events,
    format_events_text
)
from weather import get_weather, get_mock_weather, get_weather_suggestion
from feishu_bot import send_rich_card, upload_image, get_access_token

# 星期映射
WEEKDAYS = ["周一", "周二", "周三", "周四", "周五", "周六", "周日"]

def get_greeting():
    """生成问候语"""
    hour = datetime.now().hour
    if hour < 6:
        return "🌙 夜深了"
    elif hour < 9:
        return "☀️ 早安"
    elif hour < 12:
        return "🌤️ 上午好"
    elif hour < 14:
        return "🍱 午安"
    elif hour < 18:
        return "☕ 下午好"
    else:
        return "🌆 晚上好"

def get_date_string():
    """获取日期字符串"""
    now = datetime.now()
    weekday = WEEKDAYS[now.weekday()]
    return f"{now.month}月{now.day}日 {weekday}"

def build_morning_message(weather, today_events, tomorrow_events, outfit_text=None):
    """
    构建晨间消息
    
    Args:
        weather: 天气数据 dict
        today_events: 今日事件列表
        tomorrow_events: 明日事件列表
        outfit_text: 穿搭建议文本（可选）
    
    Returns:
        tuple: (标题, 内容文本)
    """
    greeting = get_greeting()
    date_str = get_date_string()
    
    # 标题
    title = f"{greeting}，今天是 {date_str}"
    
    # 内容构建
    sections = []
    
    # 天气
    if weather:
        weather_line = f"🌡️ {CITY} | {weather['text']} {weather['temp']}°C | 体感{weather['feels_like']}°C"
        sections.append(weather_line)
    
    # 穿搭建议
    if outfit_text:
        sections.append(f"\n👔 今日穿搭\n{outfit_text}")
    elif weather:
        suggestion = get_weather_suggestion(weather['temp'])
        sections.append(f"\n👔 {suggestion['suggestion']}")
    
    # 今日日程
    sections.append(f"\n📅 今日日程（{len(today_events)}件）")
    sections.append(format_events_text(today_events))
    
    # 明日预告
    if tomorrow_events:
        sections.append(f"\n👀 明日预告")
        sections.append(format_events_text(tomorrow_events, max_count=3))
    
    # 结尾
    sections.append("\n祝你开工顺利 🚀")
    
    content = "\n".join(sections)
    
    return title, content

def send_morning_push(use_mock=False, outfit_image_path=None, outfit_text=None):
    """
    发送晨间推送
    
    Args:
        use_mock: 是否使用模拟数据
        outfit_image_path: 穿搭图片路径（可选）
        outfit_text: 穿搭建议文本（可选）
    
    Returns:
        dict: 飞书API响应
    """
    print("=== 晨间工作启动器 ===")
    print(f"时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # 获取天气
    if use_mock:
        weather = get_mock_weather(temp=-2, text="晴")
        print(f"[模拟] 天气: {weather['text']} {weather['temp']}°C")
    else:
        weather = get_weather()
        if weather:
            print(f"天气: {weather['text']} {weather['temp']}°C")
        else:
            print("获取天气失败，使用模拟数据")
            weather = get_mock_weather()
    
    # 获取日历
    if use_mock:
        today_events = get_mock_today_events()
        tomorrow_events = get_mock_tomorrow_events()
        print(f"[模拟] 今日日程: {len(today_events)} 件")
    else:
        today_events = get_today_events()
        tomorrow_events = get_tomorrow_events()
        print(f"今日日程: {len(today_events)} 件")
        print(f"明日日程: {len(tomorrow_events)} 件")
    
    # 构建消息
    title, content = build_morning_message(
        weather, today_events, tomorrow_events, outfit_text
    )
    
    print(f"\n--- 消息预览 ---")
    print(f"标题: {title}")
    print(f"内容:\n{content}")
    print("--- 预览结束 ---\n")
    
    # 上传图片（如果有）
    image_key = None
    if outfit_image_path and os.path.exists(outfit_image_path):
        print(f"上传穿搭图片: {outfit_image_path}")
        image_key = upload_image(outfit_image_path)
        if image_key:
            print(f"图片上传成功: {image_key}")
    
    # 发送卡片
    result = send_rich_card(title, content, image_key)
    
    if result.get("code") == 0:
        print("✅ 晨间推送发送成功！")
    else:
        print(f"❌ 发送失败: {result}")
    
    return result

if __name__ == "__main__":
    # 测试：使用模拟数据
    send_morning_push(use_mock=True)
