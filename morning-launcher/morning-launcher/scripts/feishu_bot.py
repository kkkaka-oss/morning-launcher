"""
飞书机器人消息发送模块
"""
import os
import json
import requests
from dotenv import load_dotenv

load_dotenv()

APP_ID = os.getenv("FEISHU_APP_ID")
APP_SECRET = os.getenv("FEISHU_APP_SECRET")
OPEN_ID = os.getenv("FEISHU_OPEN_ID")

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
    """发送图片消息"""
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

