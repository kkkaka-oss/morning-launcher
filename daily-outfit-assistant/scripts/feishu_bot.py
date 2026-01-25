"""
飞书机器人消息发送模块
"""
import os
import requests
import json

# ========== 配置区域 ==========
APP_ID = os.environ.get("FEISHU_APP_ID", "cli_a9e7b6aaf7381bd7")
APP_SECRET = os.environ.get("FEISHU_APP_SECRET", "zq9NLh2vroEGz4DcnLVEqdM3fH60GIeU")
OPEN_ID = os.environ.get("FEISHU_OPEN_ID", "ou_bf952c0557f9866f8228b6f837aa2329")
# ==============================

def get_access_token():
    """获取 tenant_access_token"""
    url = "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal"
    payload = {"app_id": APP_ID, "app_secret": APP_SECRET}
    response = requests.post(url, json=payload)
    return response.json().get("tenant_access_token")

def send_text_message(text):
    """发送文本消息"""
    token = get_access_token()
    url = "https://open.feishu.cn/open-apis/im/v1/messages"
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    params = {"receive_id_type": "open_id"}
    payload = {
        "receive_id": OPEN_ID,
        "msg_type": "text",
        "content": json.dumps({"text": text})
    }
    response = requests.post(url, headers=headers, params=params, json=payload)
    return response.json()

def send_image_message(image_key):
    """发送图片消息（需要先上传图片获取 image_key）"""
    token = get_access_token()
    url = "https://open.feishu.cn/open-apis/im/v1/messages"
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    params = {"receive_id_type": "open_id"}
    payload = {
        "receive_id": OPEN_ID,
        "msg_type": "image",
        "content": json.dumps({"image_key": image_key})
    }
    response = requests.post(url, headers=headers, params=params, json=payload)
    return response.json()

def upload_image(image_path):
    """上传图片获取 image_key"""
    token = get_access_token()
    url = "https://open.feishu.cn/open-apis/im/v1/images"
    headers = {"Authorization": f"Bearer {token}"}
    with open(image_path, 'rb') as f:
        files = {"image": f}
        data = {"image_type": "message"}
        response = requests.post(url, headers=headers, files=files, data=data)
    return response.json().get("data", {}).get("image_key")

def send_rich_card(title, content, image_key=None):
    """发送富文本卡片消息"""
    token = get_access_token()
    url = "https://open.feishu.cn/open-apis/im/v1/messages"
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    params = {"receive_id_type": "open_id"}
    
    elements = [{"tag": "div", "text": {"tag": "plain_text", "content": content}}]
    if image_key:
        elements.insert(0, {"tag": "img", "img_key": image_key, "alt": {"tag": "plain_text", "content": "穿搭推荐"}})
    
    card = {
        "config": {"wide_screen_mode": True},
        "header": {"title": {"tag": "plain_text", "content": title}, "template": "pink"},
        "elements": elements
    }
    
    payload = {
        "receive_id": OPEN_ID,
        "msg_type": "interactive",
        "content": json.dumps(card)
    }
    response = requests.post(url, headers=headers, params=params, json=payload)
    return response.json()

def send_outfit_card(outfit_text, mood_text, image_path=None):
    """发送穿搭卡片（主要接口）"""
    image_key = None
    if image_path:
        image_key = upload_image(image_path)
    
    title = "✨ 今日穿搭推荐"
    content = f"{outfit_text}\n\n{mood_text}"
    
    return send_rich_card(title, content, image_key)

# 测试
if __name__ == "__main__":
    result = send_text_message("🎉 穿搭小助手准备就绪！")
    print("发送结果:", result.get("code"), result.get("msg"))
