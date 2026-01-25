"""
Gemini 图片生成模块
使用 Gemini 3 Pro Image (Nano Banana Pro) 生成穿搭图片
"""
import os
import requests
import base64
from pathlib import Path

# ========== 配置区域 ==========
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "AIzaSyCRX1RgNF3ZcXyEg_xS3IlewDE0kHAYFQA")
GEMINI_MODEL = "gemini-3-pro-image-preview"  # Nano Banana Pro
# ==============================

def load_base_image():
    """加载基础人物图片"""
    script_dir = Path(__file__).parent
    base_image_path = script_dir.parent / "assets" / "base_character.png"
    
    with open(base_image_path, 'rb') as f:
        image_data = f.read()
    
    # 转换为 base64
    return base64.b64encode(image_data).decode('utf-8')

def generate_outfit_image(prompt, output_path=None):
    """
    使用 Gemini 3 Pro Image (Nano Banana Pro) 生成穿搭图片
    
    Args:
        prompt: 生成提示词
        output_path: 输出图片路径（可选）
    
    Returns:
        str: 生成的图片路径，失败返回 None
    """
    # 使用 Gemini 3 Pro Image 模型 (Nano Banana Pro)
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{GEMINI_MODEL}:generateContent?key={GEMINI_API_KEY}"
    
    # 加载基础图片
    base_image_b64 = load_base_image()
    
    # 构建请求 - 图片编辑模式
    payload = {
        "contents": [{
            "parts": [
                {
                    "inlineData": {
                        "mimeType": "image/png",
                        "data": base_image_b64
                    }
                },
                {
                    "text": prompt
                }
            ]
        }],
        "generationConfig": {
            "responseModalities": ["image", "text"],
            "temperature": 0.8,
        }
    }
    
    try:
        print(f"正在调用 {GEMINI_MODEL} 生成图片...")
        response = requests.post(url, json=payload, timeout=120)
        result = response.json()
        
        if response.status_code != 200:
            print(f"API 错误: {result}")
            return None
        
        # 提取生成的图片数据
        candidates = result.get("candidates", [])
        if not candidates:
            print("未生成任何结果")
            print(f"完整响应: {result}")
            return None
        
        content = candidates[0].get("content", {})
        parts = content.get("parts", [])
        
        # 检查是否有图片数据
        for part in parts:
            if "inlineData" in part:
                image_data = base64.b64decode(part["inlineData"]["data"])
                
                # 确定输出路径
                if output_path is None:
                    script_dir = Path(__file__).parent
                    output_path = script_dir.parent / "assets" / "generated_outfit.png"
                
                with open(output_path, 'wb') as f:
                    f.write(image_data)
                print(f"图片已保存到: {output_path}")
                return str(output_path)
        
        # 如果没有图片，输出文本响应
        for part in parts:
            if "text" in part:
                print(f"Gemini 返回文本: {part['text']}")
        
        return None
        
    except Exception as e:
        print(f"生成图片失败: {e}")
        return None

def test_gemini_api():
    """测试 Gemini 3 Pro Image API 连接"""
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{GEMINI_MODEL}:generateContent?key={GEMINI_API_KEY}"
    
    payload = {
        "contents": [{
            "parts": [{"text": "Generate a simple red circle on white background"}]
        }],
        "generationConfig": {
            "responseModalities": ["image", "text"],
        }
    }
    
    try:
        print(f"测试 {GEMINI_MODEL} (Nano Banana Pro) API...")
        response = requests.post(url, json=payload, timeout=60)
        result = response.json()
        
        if response.status_code == 200:
            print("Gemini API 连接成功!")
            candidates = result.get("candidates", [])
            if candidates:
                parts = candidates[0].get("content", {}).get("parts", [])
                for part in parts:
                    if "inlineData" in part:
                        print("图片生成功能正常!")
                        return True
                    if "text" in part:
                        print(f"响应: {part['text'][:100]}...")
            return True
        else:
            print(f"API 错误: {result}")
            return False
    except Exception as e:
        print(f"连接失败: {e}")
        return False

if __name__ == "__main__":
    test_gemini_api()
