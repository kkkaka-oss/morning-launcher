"""
飞书 Webhook 服务
接收飞书消息事件，支持交互式穿搭推荐
部署到 Railway
"""
import os
import json
import hashlib
import threading
from flask import Flask, request, jsonify
from feishu_bot import send_text_message
from daily_outfit import generate_outfit_recommendation, send_outfit_to_feishu
from weather import get_weather, get_mock_weather

app = Flask(__name__)

# 用于去重的消息ID缓存
processed_messages = set()

def process_message_async(message_content, chat_id, message_id):
    """异步处理消息"""
    try:
        print(f"处理消息: {message_content}")
        
        # 解析用户请求
        style_request = message_content
        
        # 获取天气
        weather = get_weather()
        if not weather:
            weather = get_mock_weather(temp=15, text="晴")
        
        # 检查是否有特殊天气请求
        if "雨" in message_content:
            weather["text"] = "中雨"
        elif "雪" in message_content:
            weather["text"] = "小雪"
        elif "冷" in message_content or "降温" in message_content:
            weather["temp"] = max(weather["temp"] - 10, -5)
        
        # 生成推荐
        recommendation = generate_outfit_recommendation(weather, style_request)
        
        # 发送到飞书
        send_outfit_to_feishu(recommendation)
        
        print(f"穿搭推荐已发送")
        
    except Exception as e:
        print(f"处理消息失败: {e}")
        import traceback
        traceback.print_exc()
        send_text_message(f"抱歉，生成穿搭时出错了：{str(e)}")

@app.route('/webhook', methods=['POST'])
def webhook():
    """飞书事件回调"""
    data = request.json
    print(f"收到请求: {json.dumps(data, ensure_ascii=False)[:500]}")
    
    # 处理 URL 验证请求
    if data.get("type") == "url_verification":
        challenge = data.get("challenge", "")
        return jsonify({"challenge": challenge})
    
    # 处理事件回调
    header = data.get("header", {})
    event = data.get("event", {})
    
    # 获取事件类型
    event_type = header.get("event_type", "")
    
    # 处理消息事件
    if event_type == "im.message.receive_v1":
        message = event.get("message", {})
        message_id = message.get("message_id", "")
        
        # 去重
        if message_id in processed_messages:
            return jsonify({"code": 0})
        processed_messages.add(message_id)
        
        # 限制缓存大小
        if len(processed_messages) > 1000:
            processed_messages.clear()
        
        # 获取消息内容
        msg_type = message.get("message_type", "")
        chat_id = message.get("chat_id", "")
        
        if msg_type == "text":
            content = json.loads(message.get("content", "{}"))
            text = content.get("text", "").strip()
            
            # 移除 @机器人 的部分
            if "@" in text:
                text = text.split("@")[0].strip() or text.split("@")[-1].strip()
            
            print(f"收到消息: {text}")
            
            # 判断是否是穿搭请求
            trigger_keywords = ["穿搭", "穿什么", "搭配", "今天穿", "推荐", "可爱", "优雅", "帅气", "温柔", "休闲", "生成"]
            
            if any(kw in text for kw in trigger_keywords) or text:
                # 先回复确认消息
                send_text_message("💕 收到啦！正在挑选今日穿搭，等我一下哒...")
                
                # 异步处理穿搭生成
                thread = threading.Thread(
                    target=process_message_async,
                    args=(text, chat_id, message_id)
                )
                thread.start()
    
    return jsonify({"code": 0})

@app.route('/health', methods=['GET'])
def health():
    """健康检查"""
    return jsonify({"status": "ok", "service": "outfit-assistant"})

@app.route('/', methods=['GET'])
def index():
    """首页"""
    return """
    <html>
    <head><meta charset="utf-8"><title>穿搭小助手</title></head>
    <body style="font-family: sans-serif; padding: 40px; text-align: center;">
        <h1>🎀 穿搭小助手</h1>
        <p>飞书机器人 Webhook 服务运行中...</p>
        <p>请在飞书中给机器人发消息来获取穿搭推荐</p>
    </body>
    </html>
    """

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    print(f"服务启动在端口 {port}")
    app.run(host='0.0.0.0', port=port, debug=False)
