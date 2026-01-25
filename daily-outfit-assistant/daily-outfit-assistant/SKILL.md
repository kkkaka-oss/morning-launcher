---
name: daily-outfit-assistant
description: 每日智能穿搭助手。根据天气和衣橱数据生成个性化穿搭建议，输出卡通风格穿搭图片和情绪文案，推送到飞书。触发场景：(1) 用户请求今日穿搭建议 (2) 用户想添加新衣服到衣橱 (3) 用户想生成穿搭卡片 (4) 用户想设置每日推送
---

# 每日穿搭助手 Daily Outfit Assistant

根据天气和用户衣橱，智能生成穿搭建议和卡通风格穿搭卡片。

## 核心功能

1. **衣橱管理** - 分析衣服图片，提取标签存入 wardrobe.json
2. **智能搭配** - 根据天气温度、场合选择合适的搭配组合
3. **卡片生成** - 输出 Gemini 图片生成 prompt + 情绪文案
4. **飞书推送** - 将卡片推送到用户飞书

## 工作流程

### 1. 添加衣服到衣橱

用户上传衣服图片时，分析并提取：
- 类别：tops / outerwear / dresses / bottoms
- 颜色（中英文）
- 风格标签
- 适合季节
- 保暖度（1-5）
- 图片生成 prompt（英文）

将结果追加到 `assets/wardrobe.json`。

### 2. 生成今日穿搭

输入：当日天气（温度、天气状况）

流程：
1. 根据温度筛选适合的衣服（参考 warmth 值）
2. 选择风格协调的上下装组合
3. 天冷时加外套
4. 生成搭配说明

输出：
- 搭配方案（具体单品）
- Gemini 图片生成 prompt
- 情绪文案

### 3. Gemini 图片生成 Prompt 模板

```
Keep this character's face, hair, facial expression, and body proportions exactly the same. 
Change her outfit to: [具体服装描述]. 
Natural relaxed pose, [姿势描述]. 
Keep the same 3D doll aesthetic, same soft pastel background, full body, aspect ratio 3:4
```

需要用户提供基础角色形象图作为参考。

### 4. 情绪文案风格

温暖治愈系，例如：
- "今天也要元气满满地出门呀 ☀️"
- "降温了，记得把自己裹暖和一点 🧣"
- "穿上喜欢的衣服，好心情自然来 💕"

## 天气-穿搭对应规则

| 温度范围 | 建议穿搭 | warmth 参考 |
|----------|----------|-------------|
| ≥28°C | 轻薄单品、连衣裙 | 1 |
| 20-27°C | 薄外套/开衫 + 裙装 | 2 |
| 12-19°C | 毛衣 + 裙装/裤装 | 3 |
| 5-11°C | 厚毛衣 + 外套 | 4 |
| <5°C | 羽绒服 + 保暖内搭 | 5 |

## 飞书推送

使用 `scripts/feishu_bot.py` 发送消息。

需要配置：
- APP_ID
- APP_SECRET  
- OPEN_ID（用户标识）

支持发送：
- 文本消息
- 图片消息（需先上传图片获取 image_key）
- 富文本卡片

## 文件说明

- `assets/wardrobe.json` - 衣橱数据
- `assets/base_character.png` - 用户基础角色形象图
- `scripts/feishu_bot.py` - 飞书消息发送
- `scripts/weather.py` - 天气获取
- `scripts/daily_outfit.py` - 每日推送主脚本
- `references/outfit_rules.md` - 搭配规则详细说明
