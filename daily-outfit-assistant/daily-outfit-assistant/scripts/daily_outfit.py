"""
每日穿搭推送主脚本
整合天气、衣橱、搭配逻辑、Gemini生图、飞书推送
支持天气适配背景
"""
import sys
import io
import json
import random
from pathlib import Path
from weather import get_weather, get_mock_weather, get_weather_suggestion
from feishu_bot import send_text_message, send_outfit_card, upload_image, send_image_message
from gemini_image import generate_outfit_image

# 设置输出编码为 UTF-8
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# 获取脚本所在目录
SCRIPT_DIR = Path(__file__).parent
ASSETS_DIR = SCRIPT_DIR.parent / "assets"
WARDROBE_PATH = ASSETS_DIR / "wardrobe.json"

def load_wardrobe():
    """加载衣橱数据"""
    with open(WARDROBE_PATH, 'r', encoding='utf-8') as f:
        return json.load(f)

def filter_by_warmth(items, target_warmth):
    """根据保暖度筛选衣服"""
    # 允许 ±1 的容差
    filtered = [item for item in items if abs(item.get("warmth", 3) - target_warmth) <= 1]
    # 如果筛选后为空，返回原列表
    return filtered if filtered else items

def filter_by_style(items, style_keywords):
    """根据风格关键词筛选"""
    if not style_keywords:
        return items
    filtered = [item for item in items if any(s in item.get("style", []) for s in style_keywords)]
    return filtered if filtered else items

def pick_outfit(wardrobe, warmth_level, style_keywords=None):
    """选择搭配方案 - 确保完整（上装+下装+鞋履 或 连衣裙+鞋履）"""
    outfit = {}
    
    # 筛选适合温度的衣服
    tops = filter_by_warmth(wardrobe.get("tops", []), warmth_level)
    bottoms = filter_by_warmth(wardrobe.get("bottoms", []), warmth_level)
    outerwear = filter_by_warmth(wardrobe.get("outerwear", []), warmth_level)
    dresses = filter_by_warmth(wardrobe.get("dresses", []), warmth_level)
    shoes = filter_by_warmth(wardrobe.get("shoes", []), warmth_level)
    
    # 根据风格筛选
    if style_keywords:
        tops = filter_by_style(tops, style_keywords)
        bottoms = filter_by_style(bottoms, style_keywords)
        outerwear = filter_by_style(outerwear, style_keywords)
        dresses = filter_by_style(dresses, style_keywords)
        shoes = filter_by_style(shoes, style_keywords)
    
    # 随机决定穿连衣裙还是上下装分开
    if dresses and random.random() < 0.25:
        outfit["dress"] = random.choice(dresses)
    else:
        # 必须有上装和下装
        if tops:
            outfit["top"] = random.choice(tops)
        if bottoms:
            outfit["bottom"] = random.choice(bottoms)
    
    # 冷天加外套 (warmth >= 3)
    if warmth_level >= 3 and outerwear:
        outfit["outerwear"] = random.choice(outerwear)
    
    # 必须有鞋履
    if shoes:
        outfit["shoes"] = random.choice(shoes)
    
    return outfit

def get_weather_background(weather_text, temp):
    """根据天气返回背景描述"""
    if "雨" in weather_text:
        return "rainy city street with wet pavement and soft rain drops, cozy atmosphere, umbrellas in background"
    elif "雪" in weather_text:
        return "snowy winter scene with gentle snowflakes falling, white snow covered ground, magical winter atmosphere"
    elif "阴" in weather_text or "多云" in weather_text:
        return "overcast day with soft diffused light, cozy urban street scene"
    elif temp >= 25:
        return "bright sunny summer day, warm golden sunlight, cheerful outdoor scene"
    elif temp <= 5:
        return "cold winter day with crisp air, soft winter light, cozy atmosphere"
    else:
        return "pleasant day with soft natural lighting, gentle breeze, comfortable outdoor scene"

def generate_outfit_prompt(outfit, weather):
    """生成 Gemini 图片 prompt - 包含天气适配背景"""
    parts = []
    
    # 外套
    if "outerwear" in outfit:
        parts.append(outfit["outerwear"]["prompt"])
    
    # 上装或连衣裙
    if "dress" in outfit:
        parts.append(outfit["dress"]["prompt"])
    else:
        if "top" in outfit:
            parts.append(outfit["top"]["prompt"])
        if "bottom" in outfit:
            parts.append(outfit["bottom"]["prompt"])
    
    # 鞋履
    if "shoes" in outfit:
        parts.append(outfit["shoes"]["prompt"])
    
    outfit_desc = ", ".join(parts)
    
    # 获取天气适配背景
    background = get_weather_background(weather["text"], weather["temp"])
    
    # 随机选择一个姿势
    poses = [
        "one hand slightly touching hair, gentle head tilt",
        "hands naturally at sides, soft smile",
        "one hand on hip, confident pose",
        "holding a small bag, walking pose",
        "arms crossed casually, relaxed stance"
    ]
    pose = random.choice(poses)
    
    prompt = f"""Keep this character's face, hair, facial expression, and body proportions exactly the same. 
Change her outfit to: {outfit_desc}. 
Natural relaxed pose, {pose}. 
Background: {background}.
Keep the same 3D doll aesthetic, full body shot showing the complete outfit including shoes, aspect ratio 3:4"""
    
    return prompt

def generate_outfit_text(outfit, weather):
    """生成搭配说明文字 - 完整版"""
    items = []
    
    if "outerwear" in outfit:
        items.append(f"外套：{outfit['outerwear']['name']}（{outfit['outerwear']['color']}）")
    if "top" in outfit:
        items.append(f"上装：{outfit['top']['name']}（{outfit['top']['color']}）")
    if "bottom" in outfit:
        items.append(f"下装：{outfit['bottom']['name']}（{outfit['bottom']['color']}）")
    if "dress" in outfit:
        items.append(f"连衣裙：{outfit['dress']['name']}（{outfit['dress']['color']}）")
    if "shoes" in outfit:
        items.append(f"鞋履：{outfit['shoes']['name']}（{outfit['shoes']['color']}）")
    
    weather_info = f"今日天气：{weather['text']} {weather['temp']}°C"
    outfit_info = "\n".join(items)
    
    return f"{weather_info}\n\n📍 今日穿搭：\n{outfit_info}"

def generate_mood_text(weather):
    """生成情绪文案"""
    temp = weather["temp"]
    text = weather["text"]
    
    warm_msgs = [
        "今天也要元气满满地出门呀 ☀️",
        "穿上喜欢的衣服，好心情自然来 💕",
        "新的一天，从精致穿搭开始 ✨",
        "今天的你一定很好看！💫"
    ]
    
    cold_msgs = [
        "降温了，记得把自己裹暖和一点 🧣",
        "天冷也要美美的出门呀 ❄️",
        "保暖第一，时髦第二 🧥",
        "冷冷的天气，暖暖的穿搭 💝"
    ]
    
    rain_msgs = [
        "记得带伞哦 🌂",
        "下雨天也要保持好心情 🌧️",
        "雨天穿搭小技巧：深色更耐脏 💧",
        "去踩踩落雪吧，踏碎烦恼哦 ❄️"
    ]
    
    if "雨" in text:
        return random.choice(rain_msgs)
    elif "雪" in text:
        return random.choice(rain_msgs)
    elif temp < 10:
        return random.choice(cold_msgs)
    else:
        return random.choice(warm_msgs)

def parse_style_request(message):
    """解析用户消息中的风格需求"""
    style_map = {
        "可爱": ["可爱", "甜美"],
        "甜美": ["甜美", "可爱"],
        "优雅": ["优雅", "气质"],
        "气质": ["气质", "优雅"],
        "休闲": ["休闲", "慵懒"],
        "慵懒": ["慵懒", "休闲"],
        "帅气": ["帅气", "甜酷"],
        "酷": ["甜酷", "帅气"],
        "温柔": ["温柔", "优雅"],
        "保暖": ["保暖", "可爱"],
    }
    
    for keyword, styles in style_map.items():
        if keyword in message:
            return styles
    return None

def generate_outfit_recommendation(weather=None, style_request=None):
    """生成穿搭推荐的核心函数"""
    # 1. 获取天气
    if weather is None:
        weather = get_weather()
        if not weather:
            weather = get_mock_weather(temp=15, text="晴")
    
    # 2. 获取穿搭建议
    suggestion = get_weather_suggestion(weather["temp"])
    
    # 3. 解析风格需求
    style_keywords = None
    if style_request:
        style_keywords = parse_style_request(style_request)
    
    # 4. 加载衣橱并选择搭配
    wardrobe = load_wardrobe()
    outfit = pick_outfit(wardrobe, suggestion["warmth"], style_keywords)
    
    # 5. 生成文案
    outfit_text = generate_outfit_text(outfit, weather)
    mood_text = generate_mood_text(weather)
    
    # 6. 生成图片 prompt
    prompt = generate_outfit_prompt(outfit, weather)
    
    return {
        "weather": weather,
        "outfit": outfit,
        "outfit_text": outfit_text,
        "mood_text": mood_text,
        "prompt": prompt
    }

def send_outfit_to_feishu(recommendation, chat_id=None):
    """发送穿搭推荐到飞书"""
    # 生成图片
    output_image_path = ASSETS_DIR / "today_outfit.png"
    image_path = generate_outfit_image(recommendation["prompt"], str(output_image_path))
    
    if image_path:
        # 上传图片并发送
        image_key = upload_image(image_path)
        if image_key:
            send_image_message(image_key)
        # 发送文字说明
        full_text = f"{recommendation['outfit_text']}\n\n{recommendation['mood_text']}"
        send_text_message(full_text)
        return True
    else:
        # 图片生成失败，只发送文字
        full_text = f"{recommendation['outfit_text']}\n\n{recommendation['mood_text']}"
        send_text_message(full_text)
        return False

def main(style_request=None):
    """主函数"""
    print("=" * 50)
    print("🎀 每日穿搭助手启动")
    print("=" * 50)
    
    # 1. 获取天气
    weather = get_weather()
    if not weather:
        print("⚠️ 无法获取天气，使用模拟数据")
        weather = get_mock_weather(temp=8, text="晴")
    print(f"\n📍 天气: {weather['text']} {weather['temp']}°C")
    
    # 2. 生成推荐
    recommendation = generate_outfit_recommendation(weather, style_request)
    print(f"\n{recommendation['outfit_text']}")
    print(f"\n{recommendation['mood_text']}")
    print(f"\n🎨 Gemini Prompt:\n{recommendation['prompt']}")
    
    # 3. 生成图片并发送
    print(f"\n🖼️ 正在生成穿搭图片...")
    success = send_outfit_to_feishu(recommendation)
    
    if success:
        print("✅ 图片发送成功")
    else:
        print("⚠️ 图片生成失败，已发送文字")
    
    print("\n" + "=" * 50)
    print("✨ 完成！")

if __name__ == "__main__":
    import sys
    # 支持命令行传入风格参数
    style = " ".join(sys.argv[1:]) if len(sys.argv) > 1 else None
    main(style)
