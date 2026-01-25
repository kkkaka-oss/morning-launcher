"""
天气获取模块
使用和风天气 API（免费版）
"""
import requests

# ========== 配置区域 ==========
QWEATHER_API_KEY = "eaa005014e9a4523a9b1f0d90e645033"
CITY_ID = "101010100"  # 北京
# ==============================

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
                "temp": int(now["temp"]),  # 当前温度
                "feels_like": int(now["feelsLike"]),  # 体感温度
                "text": now["text"],  # 天气状况（晴、多云等）
                "humidity": int(now["humidity"]),  # 湿度
                "wind": now["windDir"]  # 风向
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

# 模拟天气数据（在没有 API Key 时使用）
def get_mock_weather(temp=15, text="多云"):
    """模拟天气数据，用于测试"""
    return {
        "temp": temp,
        "feels_like": temp - 2,
        "text": text,
        "humidity": 60,
        "wind": "北风"
    }

if __name__ == "__main__":
    # 测试
    weather = get_mock_weather(8, "晴")
    print(f"温度: {weather['temp']}°C")
    print(f"天气: {weather['text']}")
    
    suggestion = get_weather_suggestion(weather['temp'])
    print(f"穿搭建议: {suggestion['suggestion']}")
    print(f"保暖度要求: {suggestion['warmth']}")
