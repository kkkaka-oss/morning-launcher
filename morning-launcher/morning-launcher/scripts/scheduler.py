"""
定时任务调度器
每天 8:00 触发晨间推送

使用方式：
1. 直接运行此脚本保持后台运行
2. 或配置 cron/systemd 定时执行 morning_push.py
"""
import schedule
import time
from datetime import datetime
from morning_push import send_morning_push
from config import PUSH_TIME, TIMEZONE

def job():
    """定时任务"""
    print(f"\n{'='*50}")
    print(f"定时任务触发: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'='*50}\n")
    
    # 发送晨间推送
    # 注意：如果要包含穿搭图片，需要先调用穿搭skill生成图片
    send_morning_push(use_mock=False)

def run_scheduler():
    """启动调度器"""
    print(f"晨间启动器调度器已启动")
    print(f"推送时间: 每天 {PUSH_TIME}")
    print(f"时区: {TIMEZONE}")
    print("-" * 30)
    
    # 设置每天定时任务
    schedule.every().day.at(PUSH_TIME).do(job)
    
    print("等待下一次推送...")
    
    while True:
        schedule.run_pending()
        time.sleep(60)  # 每分钟检查一次

if __name__ == "__main__":
    run_scheduler()

# ========== 其他部署方式 ==========

# 方式1: Linux Cron
# 编辑 crontab: crontab -e
# 添加: 0 8 * * * /usr/bin/python3 /path/to/morning_push.py

# 方式2: systemd service
# 创建 /etc/systemd/system/morning-launcher.service
# 然后 systemctl enable morning-launcher

# 方式3: 飞书定时消息
# 在飞书后台配置定时触发 webhook

# 方式4: 云函数
# 使用阿里云/腾讯云函数，配置定时触发器
