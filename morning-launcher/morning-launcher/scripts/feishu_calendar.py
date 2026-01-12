"""
飞书日历 API 封装
获取用户今日和明日的日程事件
"""
import requests
from datetime import datetime, timedelta
from config import APP_ID, APP_SECRET, OPEN_ID

def get_access_token():
    """获取 tenant_access_token"""
    url = "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal"
    payload = {"app_id": APP_ID, "app_secret": APP_SECRET}
    response = requests.post(url, json=payload)
    return response.json().get("tenant_access_token")

def get_primary_calendar_id(token):
    """获取用户主日历ID"""
    url = "https://open.feishu.cn/open-apis/calendar/v4/calendars/primary"
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(url, headers=headers)
    data = response.json()
    if data.get("code") == 0:
        return data.get("data", {}).get("calendars", [{}])[0].get("calendar", {}).get("calendar_id")
    return None

def get_calendar_events(date_str=None, days=1):
    """
    获取指定日期的日程事件
    
    Args:
        date_str: 日期字符串，格式 "2025-01-06"，默认今天
        days: 获取几天的事件，默认1天
    
    Returns:
        list: 事件列表，每个事件包含 title, start_time, end_time, is_all_day
    """
    token = get_access_token()
    
    # 计算时间范围
    if date_str:
        start_date = datetime.strptime(date_str, "%Y-%m-%d")
    else:
        start_date = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    
    end_date = start_date + timedelta(days=days)
    
    # 转换为时间戳（秒）
    start_ts = int(start_date.timestamp())
    end_ts = int(end_date.timestamp())
    
    # 获取用户日历列表
    url = "https://open.feishu.cn/open-apis/calendar/v4/calendars"
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(url, headers=headers)
    calendars_data = response.json()
    
    all_events = []
    
    if calendars_data.get("code") == 0:
        calendars = calendars_data.get("data", {}).get("calendar_list", [])
        
        for cal in calendars:
            calendar_id = cal.get("calendar_id")
            if not calendar_id:
                continue
            
            # 获取该日历的事件
            events_url = f"https://open.feishu.cn/open-apis/calendar/v4/calendars/{calendar_id}/events"
            params = {
                "start_time": str(start_ts),
                "end_time": str(end_ts),
            }
            
            events_response = requests.get(events_url, headers=headers, params=params)
            events_data = events_response.json()
            
            if events_data.get("code") == 0:
                items = events_data.get("data", {}).get("items", [])
                for item in items:
                    event = parse_event(item)
                    if event:
                        all_events.append(event)
    
    # 按开始时间排序
    all_events.sort(key=lambda x: x.get("start_time", ""))
    
    return all_events

def parse_event(item):
    """解析单个日程事件"""
    try:
        summary = item.get("summary", "无标题")
        
        start_time = item.get("start_time", {})
        end_time = item.get("end_time", {})
        
        # 判断是否全天事件
        is_all_day = "date" in start_time
        
        if is_all_day:
            start_str = start_time.get("date", "")
            end_str = end_time.get("date", "")
            display_time = "全天"
        else:
            # 时间戳转换为可读格式
            start_ts = int(start_time.get("timestamp", 0))
            end_ts = int(end_time.get("timestamp", 0))
            
            start_dt = datetime.fromtimestamp(start_ts)
            end_dt = datetime.fromtimestamp(end_ts)
            
            start_str = start_dt.strftime("%H:%M")
            end_str = end_dt.strftime("%H:%M")
            display_time = f"{start_str}-{end_str}"
        
        return {
            "title": summary,
            "start_time": start_str,
            "end_time": end_str,
            "display_time": display_time,
            "is_all_day": is_all_day,
        }
    except Exception as e:
        print(f"解析事件失败: {e}")
        return None

def get_today_events():
    """获取今日日程"""
    return get_calendar_events(days=1)

def get_tomorrow_events():
    """获取明日日程"""
    tomorrow = datetime.now() + timedelta(days=1)
    return get_calendar_events(tomorrow.strftime("%Y-%m-%d"), days=1)

def format_events_text(events, max_count=5):
    """
    格式化事件列表为文本
    
    Args:
        events: 事件列表
        max_count: 最多显示几条
    
    Returns:
        str: 格式化的文本
    """
    if not events:
        return "今天没有日程安排，轻松一天 ☕"
    
    lines = []
    for i, event in enumerate(events[:max_count]):
        time_str = event.get("display_time", "")
        title = event.get("title", "无标题")
        lines.append(f"• {time_str} {title}")
    
    if len(events) > max_count:
        lines.append(f"  ...还有 {len(events) - max_count} 件事")
    
    return "\n".join(lines)

# 模拟数据（API未配置时使用）
def get_mock_today_events():
    """模拟今日日程"""
    return [
        {"title": "S9项目周会", "display_time": "09:30-10:30", "is_all_day": False},
        {"title": "产品需求评审", "display_time": "14:00-15:00", "is_all_day": False},
        {"title": "和leader 1:1", "display_time": "16:00-16:30", "is_all_day": False},
    ]

def get_mock_tomorrow_events():
    """模拟明日日程"""
    return [
        {"title": "全员大会", "display_time": "10:00-11:00", "is_all_day": False},
    ]

if __name__ == "__main__":
    # 测试
    print("=== 今日日程 ===")
    events = get_mock_today_events()
    print(format_events_text(events))
    
    print("\n=== 明日预告 ===")
    events = get_mock_tomorrow_events()
    print(format_events_text(events))
