"""
天气获取模块
使用和风天气 API（免费版）
"""
import os
import requests
from dotenv import load_dotenv

load_dotenv()

QWEATHER_API_KEY = os.getenv("QWEATHER_API_KEY")
CITY_ID = os.getenv("CITY_ID", "101010100")  # 默认北京

def get_weather():
    """获取当日天气"""
    url = f"https://devapi.qweather.com/v7/weather/now"
    params = {
        "location": CITY_ID,
        "key": QWEATHER_API_KEY
    }
    
    try:
        response = requests.get(url, params=params)
        data = response.json()
        
        if data.get("code") == "200":
            now = data["now"]
            return {
                "temp": int(now["temp"]),
                "feels_like": int(now["feelsLike"]),
                "text": now["text"],
                "humidity": int(now["humidity"]),
                "wind": now["windDir"]
            }
        else:
            print(f"天气API错误: {data.get('code')}")
            return None
    except Exception as e:
        print(f"获取天气失败: {e}")
        return None

def get_weather_suggestion(temp):
    """根据温度返回穿搭建议"""
    if temp >= 28:
        return {"warmth": 1, "suggestion": "今天很热，穿轻薄透气的衣服"}
    elif temp >= 20:
        return {"warmth": 2, "suggestion": "温度适宜，可以穿薄外套或开衫"}
    elif temp >= 12:
        return {"warmth": 3, "suggestion": "有点凉，建议穿毛衣"}
    elif temp >= 5:
        return {"warmth": 4, "suggestion": "天气冷了，需要厚毛衣加外套"}
    else:
        return {"warmth": 5, "suggestion": "很冷！记得穿羽绒服"}

def get_mock_weather(temp=15, text="多云"):
    """模拟天气数据，用于测试"""
    return {
        "temp": temp,
        "feels_like": temp - 2,
        "text": text,
        "humidity": 60,
        "wind": "北风"
    }

