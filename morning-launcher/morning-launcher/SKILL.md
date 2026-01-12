---
name: morning-launcher
description: 晨间工作启动器。每天早上8:00自动推送今日概览到飞书，包括：天气、穿搭建议（调用daily-outfit-assistant）、今日日程、明日重要事项。一条消息看完开工状态。触发场景：(1) 用户请求晨间概览 (2) 用户想手动触发今日汇总 (3) 用户想配置推送时间
---

# 晨间工作启动器 Morning Launcher

每天早上自动推送「开工仪表盘」，一条消息掌握全天状态。

## 核心功能

1. **天气概览** - 当日天气、温度、空气质量
2. **穿搭建议** - 调用 daily-outfit-assistant skill 生成穿搭图片和建议
3. **今日日程** - 从飞书日历拉取今日全部事件
4. **明日预告** - 明天的重要事项提前预警
5. **飞书推送** - 每天 8:00 自动发送到飞书

## 推送消息格式

```
☀️ 早安，今天是 1月6日 周一

🌡️ 北京 | 晴 -3~5°C | 空气良

👔 今日穿搭
[卡通穿搭图片]
羽绒服 + 高领毛衣 + 黑色休闲裤
今天风大，记得裹严实 🧣

📅 今日日程（3件）
• 09:30 S9项目周会
• 14:00 产品需求评审
• 16:00 和leader 1:1

👀 明日预告
• 10:00 全员大会（重要）

祝你开工顺利 🚀
```

## 依赖关系

| 模块 | 来源 | 说明 |
|------|------|------|
| 天气数据 | `daily-outfit-assistant/scripts/weather.py` | 复用现有天气模块 |
| 穿搭生成 | `daily-outfit-assistant` skill | 调用完整穿搭流程 |
| 日历数据 | 飞书日历 API | 需配置应用权限 |
| 消息推送 | `daily-outfit-assistant/scripts/feishu_bot.py` | 复用现有推送模块 |

## 飞书日历权限配置

### 1. 开通日历权限

在飞书开放平台（open.feishu.cn）的应用管理后台：

1. 进入你的应用 → 权限管理
2. 添加以下权限：
   - `calendar:calendar:readonly` - 读取日历列表
   - `calendar:calendar.event:readonly` - 读取日程事件
3. 发布应用版本

### 2. 获取用户授权

需要用户授权应用访问其日历：
- 方式一：让用户在飞书中打开应用授权页面
- 方式二：使用 user_access_token 流程

### 3. 配置项

在 `scripts/config.py` 中配置：
```python
# 飞书应用凭证（复用穿搭助手配置）
APP_ID = "cli_xxxxx"
APP_SECRET = "xxxxx"
OPEN_ID = "ou_xxxxx"

# 城市配置
CITY = "北京"
CITY_ID = "101010100"

# 推送时间
PUSH_TIME = "08:00"
```

## 文件说明

```
morning-launcher/
├── SKILL.md                 # 本文件
├── scripts/
│   ├── config.py           # 配置文件
│   ├── feishu_calendar.py  # 飞书日历API封装
│   ├── morning_push.py     # 主推送脚本
│   └── scheduler.py        # 定时任务调度
```

## 工作流程

```
每天 08:00 定时触发
        ↓
并行获取数据：
  - 天气（weather.py）
  - 今日日历事件
  - 明日日历事件
        ↓
调用穿搭 skill 生成建议和图片
        ↓
组装富文本卡片
        ↓
推送到飞书
```

## 手动触发

用户可以随时请求 Claude 生成晨间概览，触发词：
- "今天有什么安排"
- "早安/晨间概览"  
- "今日汇总"

## 扩展计划（TODO）

- [ ] 未完成任务模块（待确定任务管理工具）
- [ ] 未读重要消息模块（待定义"重要"规则）
- [ ] 周末模式（休闲穿搭 + 无日程时的建议）
