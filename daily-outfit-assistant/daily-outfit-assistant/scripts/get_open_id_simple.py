"""
获取飞书用户 Open ID - 多种方式尝试
"""
import requests
import json

APP_ID = "cli_a9e7b6aaf7381bd7"
APP_SECRET = "zq9NLh2vroEGz4DcnLVEqdM3fH60GIeU"

def get_tenant_access_token():
    """获取 tenant_access_token"""
    url = "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal"
    payload = {"app_id": APP_ID, "app_secret": APP_SECRET}
    response = requests.post(url, json=payload)
    result = response.json()
    print(f"Token response: {result}")
    return result.get("tenant_access_token")

def get_bot_info():
    """获取机器人信息"""
    token = get_tenant_access_token()
    url = "https://open.feishu.cn/open-apis/bot/v3/info"
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(url, headers=headers)
    return response.json()

def search_user_by_mobile(mobile):
    """通过手机号搜索用户获取 open_id"""
    token = get_tenant_access_token()
    url = "https://open.feishu.cn/open-apis/contact/v3/users/batch_get_id"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    params = {"user_id_type": "open_id"}
    payload = {"mobiles": [mobile]}
    response = requests.post(url, headers=headers, params=params, json=payload)
    return response.json()

def list_messages():
    """获取机器人收到的消息（需要 webhook）"""
    token = get_tenant_access_token()
    # 这个 API 需要事件订阅
    pass

if __name__ == "__main__":
    print("=" * 60)
    print("Feishu Open ID Tool")
    print("=" * 60)
    
    print("\n[1] Testing token...")
    token = get_tenant_access_token()
    
    print("\n[2] Getting bot info...")
    bot_info = get_bot_info()
    print(json.dumps(bot_info, indent=2, ensure_ascii=False))
    
    print("\n[3] Trying to search by mobile: 19984847751")
    result = search_user_by_mobile("19984847751")
    print(json.dumps(result, indent=2, ensure_ascii=False))
    
    print("\n" + "=" * 60)
    print("INSTRUCTIONS:")
    print("=" * 60)
    print("""
If you see permission errors, please do the following in Feishu Open Platform:

1. Go to: https://open.feishu.cn/app/{app_id}
2. Click "Permissions" (权限管理)
3. Add these permissions:
   - contact:user.id:readonly (获取用户 ID)
   - im:message (发送消息)
   - im:chat (获取群信息)
4. Click "Create Version" (创建版本) and publish
5. Wait for admin approval if needed

Alternative: Get your open_id from Feishu web:
1. Open Feishu web: https://www.feishu.cn/
2. Open browser DevTools (F12) -> Network tab
3. Refresh page, look for any API request
4. Find 'open_id' in the response
""".format(app_id=APP_ID))
