"""
获取飞书用户 Open ID 的脚本
通过 OAuth 授权流程获取当前用户的 open_id
"""
import requests
from flask import Flask, request, redirect
import webbrowser

# 配置
APP_ID = "cli_a9e7b6aaf7381bd7"
APP_SECRET = "zq9NLh2vroEGz4DcnLVEqdM3fH60GIeU"
REDIRECT_URI = "https://feishu.cpolar.top/callback"  # 内网穿透地址

app = Flask(__name__)

@app.route('/')
def index():
    """首页 - 跳转到飞书授权"""
    auth_url = (
        f"https://open.feishu.cn/open-apis/authen/v1/authorize"
        f"?app_id={APP_ID}"
        f"&redirect_uri={REDIRECT_URI}"
        f"&state=random_state"
    )
    return redirect(auth_url)

@app.route('/callback')
def callback():
    """授权回调 - 获取 open_id"""
    code = request.args.get('code')
    if not code:
        return "授权失败：未获取到 code"
    
    # 获取 user_access_token
    token_url = "https://open.feishu.cn/open-apis/authen/v1/oidc/access_token"
    
    # 先获取 app_access_token
    app_token_url = "https://open.feishu.cn/open-apis/auth/v3/app_access_token/internal"
    app_token_resp = requests.post(app_token_url, json={
        "app_id": APP_ID,
        "app_secret": APP_SECRET
    })
    app_access_token = app_token_resp.json().get("app_access_token")
    
    # 用 code 换取 user_access_token
    headers = {
        "Authorization": f"Bearer {app_access_token}",
        "Content-Type": "application/json"
    }
    user_token_resp = requests.post(token_url, headers=headers, json={
        "grant_type": "authorization_code",
        "code": code
    })
    
    result = user_token_resp.json()
    print("\n" + "=" * 50)
    print("完整响应：")
    print(result)
    print("=" * 50)
    
    if result.get("code") == 0:
        data = result.get("data", {})
        open_id = data.get("open_id")
        name = data.get("name", "未知")
        
        print(f"\n🎉 获取成功！")
        print(f"用户名: {name}")
        print(f"Open ID: {open_id}")
        print("\n请将此 Open ID 复制到 feishu_bot.py 中")
        
        return f"""
        <html>
        <head><meta charset="utf-8"><title>获取成功</title></head>
        <body style="font-family: sans-serif; padding: 40px; text-align: center;">
            <h1>🎉 获取成功！</h1>
            <p>用户名: <strong>{name}</strong></p>
            <p>Open ID: <code style="background: #f0f0f0; padding: 8px 16px; font-size: 18px;">{open_id}</code></p>
            <p style="color: #666;">请将此 Open ID 复制到 feishu_bot.py 中的 OPEN_ID 变量</p>
        </body>
        </html>
        """
    else:
        error_msg = result.get("msg", "未知错误")
        return f"获取失败: {error_msg}<br><br>完整响应: {result}"

if __name__ == "__main__":
    print("=" * 50)
    print("飞书 Open ID 获取工具")
    print("=" * 50)
    print(f"\n请确保已配置内网穿透:")
    print(f"  本地端口: 5000")
    print(f"  公网地址: https://feishu.cpolar.top")
    print(f"\n飞书应用后台需要配置:")
    print(f"  重定向 URL: {REDIRECT_URI}")
    print("\n启动服务后，请在浏览器中访问: http://localhost:5000")
    print("=" * 50 + "\n")
    
    # 自动打开浏览器
    webbrowser.open("http://localhost:5000")
    
    app.run(port=5000, debug=False)

