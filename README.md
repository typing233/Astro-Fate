# Astro Fate - 命运星图

一款通过捕捉你做选择时的潜意识行为（犹豫、停顿、节奏），利用 AI 实时生成专属隐喻预言与动态命运星图的交互式数字艺术应用。

## 功能特点

- 🎨 **诗意的问题设计** - 5 道极具诗意和抽象感的问题，探索你的内心世界
- 🧠 **潜意识行为捕捉** - 记录用户在每道题上的停留时长和选项切换次数
- 🤖 **AI 命运解读** - 调用大语言模型（DeepSeek）生成带有隐喻色彩的命运判词
- ✨ **动态星图展示** - Canvas 2D 粒子特效，根据行为特征生成专属命运星点
- 🌙 **沉浸式体验** - 现代化的 UI 设计，配合闪烁的星空背景

## 技术栈

### 后端
- **Python 3.8+**
- **FastAPI** - 高性能 Web 框架
- **Uvicorn** - ASGI 服务器
- **Pydantic** - 数据验证
- **Httpx** - 异步 HTTP 客户端
- **Python-dotenv** - 环境变量管理

### 前端
- **原生 HTML5 + CSS3 + JavaScript**
- **Canvas 2D API** - 粒子特效与星图绘制
- **Google Fonts (Noto Sans SC / Noto Serif SC)** - 中文字体支持

## 项目结构

```
Astro-Fate/
├── backend/
│   └── main.py              # FastAPI 主应用文件
├── frontend/
│   └── static/
│       ├── css/
│       │   └── style.css    # 样式文件
│       ├── js/
│       │   └── app.js       # 前端应用逻辑
│       └── index.html       # 主页面
├── tests/
│   └── test_api.py          # API 测试用例
├── .env                      # 环境变量配置（需自行配置）
├── .env.example              # 环境变量示例
├── requirements.txt          # Python 依赖
└── README.md                 # 项目说明
```

## 安装与运行

### 1. 环境准备

确保你已安装 Python 3.8 或更高版本。

### 2. 克隆项目

```bash
cd Astro-Fate
```

### 3. 安装依赖

```bash
pip install -r requirements.txt
```

### 4. 配置环境变量

复制 `.env.example` 文件为 `.env`：

```bash
cp .env.example .env
```

编辑 `.env` 文件，配置你的 DeepSeek API 密钥：

```env
DEEPSEEK_API_KEY=your_deepseek_api_key_here
DEEPSEEK_API_URL=https://api.deepseek.com/v1/chat/completions
DEEPSEEK_MODEL=deepseek-chat
PORT=9354
```

**注意**：如果不配置 `DEEPSEEK_API_KEY`，应用将使用内置的 mock 命运判词，不会调用真实的 AI 接口。

### 5. 启动服务

方式一：直接运行主文件

```bash
cd backend
python main.py
```

方式二：使用 uvicorn 命令

```bash
cd backend
uvicorn main:app --host 0.0.0.0 --port 9354 --reload
```

### 6. 访问应用

打开浏览器，访问：

```
http://localhost:9354
```

## API 接口说明

### GET /api/questions

获取所有问题列表。

**响应示例：**
```json
{
  "questions": [
    {
      "id": 1,
      "text": "你更愿意被哪种风吹散？",
      "options": [
        {"id": "A", "text": "海风，带着咸湿与远方"},
        ...
      ],
      "theme": "探索与归宿"
    },
    ...
  ]
}
```

### POST /api/submit

提交用户答案和行为数据，获取命运判词。

**请求体：**
```json
{
  "behaviors": [
    {
      "question_id": 1,
      "duration_seconds": 5.2,
      "switch_count": 2,
      "final_choice": "A"
    },
    ...
  ],
  "choices": ["A", "B", "C", "D", "A"]
}
```

**响应示例：**
```json
{
  "success": true,
  "fortune": "你是夜空中那颗最亮的星...",
  "star_count": 7,
  "behavior_analysis": {
    "avg_duration": 4.2,
    "total_switches": 6,
    "behavior_traits": "深思熟虑、追求完美",
    "decision_style": "谨慎型决策，倾向于全面考量后再做选择"
  }
}
```

## 行为数据分析

应用会根据用户的行为数据进行以下分析：

### 行为特征判断

| 条件 | 特征标签 |
|------|----------|
| 平均思考时间 > 5秒 | 深思熟虑 |
| 平均思考时间 < 3秒 | 直觉敏锐 |
| 总切换次数 > 5次 | 追求完美 |
| 总切换次数 = 0次 | 坚定果断 |
| 其他情况 | 平衡和谐 |

### 决策风格判断

| 条件 | 决策风格 |
|------|----------|
| 思考时间长 + 切换多 | 谨慎型决策 |
| 思考时间短 + 切换少 | 直觉型决策 |
| 其他情况 | 平衡型决策 |

### 星点数量

根据总切换次数计算：`star_count = min(max(switch_count + 3, 5), 12)`

- 最少 5 颗星
- 最多 12 颗星

## 使用说明

1. **开始探索** - 点击「开始探索」按钮进入答题环节
2. **回答问题** - 依次回答 5 道诗意的问题
   - 你的每一次犹豫、每一次选项切换都会被记录
   - 无需刻意"正确"回答，跟随你的直觉
3. **查看结果** - 完成所有问题后，系统会：
   - 分析你的行为特征
   - 生成专属命运判词
   - 展示动态命运星图
4. **再测一次** - 点击「再测一次」可以重新开始

## 问题主题

1. **探索与归宿** - 你更愿意被哪种风吹散？
2. **记忆与自我** - 如果记忆是一种颜色，你希望它是？
3. **存在与影响** - 你愿意成为哪种影子？
4. **时间与选择** - 当时间静止，你希望停留在哪个瞬间？
5. **信仰与命运** - 你更相信命运掌握在谁手中？

## 测试

运行 API 测试：

```bash
python -m pytest tests/ -v
```

## 注意事项

1. **API 密钥** - 如需使用真实 AI 生成，请确保 `DEEPSEEK_API_KEY` 配置正确
2. **端口** - 默认端口为 9354，可通过 `.env` 文件修改
3. **数据隐私** - 本应用不会存储任何用户数据，所有数据仅在请求生命周期内使用
4. **网络要求** - 使用 AI 功能需要能够访问 DeepSeek API 的网络环境

## 开发说明

### 添加新问题

编辑 `backend/main.py` 中的 `questions` 列表，添加新的问题对象。

### 自定义命运判词模板

编辑 `backend/main.py` 中的 `AIService._build_prompt` 方法，修改提示词模板。

### 调整星图效果

编辑 `frontend/static/js/app.js` 中的 `drawResultStars` 方法，调整粒子参数、颜色和动画效果。

## 许可证

本项目仅供学习和个人使用。

---

**Astro Fate** - 让星辰揭示你内心的命运轨迹 ✨
