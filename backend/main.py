import os
import json
import httpx
import asyncio
from fastapi import FastAPI, HTTPException, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(title="Astro Fate - 命运星图应用", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

static_dir = os.path.join(os.path.dirname(__file__), "..", "frontend", "static")
app.mount("/static", StaticFiles(directory=static_dir), name="static")

questions = [
    {
        "id": 1,
        "text": "你更愿意被哪种风吹散？",
        "options": [
            {"id": "A", "text": "海风，带着咸湿与远方"},
            {"id": "B", "text": "山风，裹着松香与古老"},
            {"id": "C", "text": "晚风，牵着暮光与平静"},
            {"id": "D", "text": "夜风，藏着星辰与秘密"}
        ],
        "theme": "探索与归宿"
    },
    {
        "id": 2,
        "text": "如果记忆是一种颜色，你希望它是？",
        "options": [
            {"id": "A", "text": "暮色紫，朦胧而神秘"},
            {"id": "B", "text": "琥珀金，温暖而珍贵"},
            {"id": "C", "text": "深海蓝，深邃而宁静"},
            {"id": "D", "text": "极光绿，变幻而永恒"}
        ],
        "theme": "记忆与自我"
    },
    {
        "id": 3,
        "text": "你愿意成为哪种影子？",
        "options": [
            {"id": "A", "text": "树的影子，庇护过路的旅人"},
            {"id": "B", "text": "云的影子，追逐风的足迹"},
            {"id": "C", "text": "水的影子，倒映天空的广阔"},
            {"id": "D", "text": "山的影子，沉默而坚定"}
        ],
        "theme": "存在与影响"
    },
    {
        "id": 4,
        "text": "当时间静止，你希望停留在哪个瞬间？",
        "options": [
            {"id": "A", "text": "日出的第一缕光，充满希望"},
            {"id": "B", "text": "午后的阳光与茶，安详宁静"},
            {"id": "C", "text": "雨后的彩虹，历经风雨"},
            {"id": "D", "text": "漫天繁星的深夜，无限可能"}
        ],
        "theme": "时间与选择"
    },
    {
        "id": 5,
        "text": "你更相信命运掌握在谁手中？",
        "options": [
            {"id": "A", "text": "自己，每一步都是选择"},
            {"id": "B", "text": "星辰，宇宙有其秩序"},
            {"id": "C", "text": "缘分，相遇自有注定"},
            {"id": "D", "text": "未知，一切皆有可能"}
        ],
        "theme": "信仰与命运"
    }
]

class BehaviorData(BaseModel):
    question_id: int
    duration_seconds: float
    switch_count: int
    final_choice: Optional[str] = None

class SubmissionRequest(BaseModel):
    behaviors: List[BehaviorData]
    choices: List[str]

class AIService:
    def __init__(self):
        self.api_key = os.getenv("DEEPSEEK_API_KEY", "")
        self.api_url = os.getenv("DEEPSEEK_API_URL", "https://api.deepseek.com/v1/chat/completions")
        self.model = os.getenv("DEEPSEEK_MODEL", "deepseek-chat")
    
    async def generate_fortune(self, behavior_analysis: dict, choices: List[str]) -> str:
        prompt = self._build_prompt(behavior_analysis, choices)
        
        if not self.api_key or self.api_key == "your_deepseek_api_key_here":
            return self._generate_mock_fortune(behavior_analysis, choices)
        
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }
        
        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": "你是一位神秘的命运解读师，擅长通过隐喻和诗意的语言揭示一个人的内心世界和命运轨迹。你的语言应该充满东方神秘色彩，同时保持现代诗歌的韵律。"},
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.85,
            "max_tokens": 500
        }
        
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(self.api_url, headers=headers, json=payload)
                response.raise_for_status()
                result = response.json()
                return result["choices"][0]["message"]["content"]
        except Exception as e:
            print(f"AI API error: {e}")
            return self._generate_mock_fortune(behavior_analysis, choices)
    
    def _build_prompt(self, behavior_analysis: dict, choices: List[str]) -> str:
        choices_with_questions = []
        for i, choice in enumerate(choices):
            q = questions[i]
            option_text = next((opt["text"] for opt in q["options"] if opt["id"] == choice), "")
            choices_with_questions.append(f"第{i+1}题 '{q['text']}' 选择了: {option_text}")
        
        prompt = f"""
请根据以下用户的行为数据和选择，生成一段充满隐喻色彩的命运判词。

用户选择详情：
{chr(10).join(choices_with_questions)}

行为数据分析：
- 平均每题思考时间：{behavior_analysis['avg_duration']:.1f} 秒
- 总选项切换次数：{behavior_analysis['total_switches']} 次
- 行为特征：{behavior_analysis['behavior_traits']}
- 决策风格：{behavior_analysis['decision_style']}

请以一位神秘命运解读师的口吻，用富有诗意和隐喻的语言，创作一段命运判词。要求：
1. 包含东方神秘元素（星辰、命运、轮回、缘分等）
2. 结合用户的行为特征和选择
3. 语言优美，富有节奏感
4. 字数控制在200-400字
5. 不要直接提及"行为数据"或"思考时间"等技术术语，而是用隐喻的方式暗示

请直接输出命运判词内容。
"""
        return prompt
    
    def _generate_mock_fortune(self, behavior_analysis: dict, choices: List[str]) -> str:
        traits = behavior_analysis['behavior_traits']
        
        fortunes = [
            """
你是夜空中那颗最亮的星，闪烁着独特的光芒。你的命运如同水流，看似平静却蕴含无穷力量。那些你犹豫过的瞬间，如晨露般珍贵，它们是宇宙为你留下的指引。

你的选择展现了一颗敏感而富有智慧的心。就像古人所说："谋定而后动，知止而有得。" 你的每一次停顿，都是与内心对话的契机；每一次转向，都是命运新的可能。

星辰为你指引，微风为你送行。你的命运掌握在自己的双手之中，每一次选择都是一次新的出发。相信你的直觉，它是你灵魂深处的古老智慧。
            """,
            """
在命运的星盘中，你是那位善于观察的智者。你的选择如同四季的更替，自然而优雅。你对待每一个决定的审慎，是你最珍贵的品质。

就像月亮有阴晴圆缺，你的人生也会有起有落。但正如古人云："山重水复疑无路，柳暗花明又一村。" 你所经历的每一次犹豫，每一次思索，都是命运在为你铺路。

你的星图上有数颗璀璨的星点在闪烁，它们代表着你的勇气、智慧与善良。保持这份初心，你的命运将如星辰般永恒闪耀。
            """
        ]
        
        return fortunes[0] if "谨慎" in traits or "深思熟虑" in traits else fortunes[1]

def analyze_behaviors(behaviors: List[BehaviorData]) -> dict:
    durations = [b.duration_seconds for b in behaviors]
    switches = [b.switch_count for b in behaviors]
    
    avg_duration = sum(durations) / len(durations)
    total_switches = sum(switches)
    
    traits = []
    if avg_duration > 5:
        traits.append("深思熟虑")
    if avg_duration < 3:
        traits.append("直觉敏锐")
    if total_switches > 5:
        traits.append("追求完美")
    if total_switches == 0:
        traits.append("坚定果断")
    
    if not traits:
        traits.append("平衡和谐")
    
    decision_style = ""
    if avg_duration > 5 and total_switches > 3:
        decision_style = "谨慎型决策，倾向于全面考量后再做选择"
    elif avg_duration < 3 and total_switches < 2:
        decision_style = "直觉型决策，跟随内心的第一反应"
    else:
        decision_style = "平衡型决策，理性与直觉并重"
    
    return {
        "avg_duration": avg_duration,
        "total_switches": total_switches,
        "behavior_traits": "、".join(traits),
        "decision_style": decision_style
    }

ai_service = AIService()

@app.get("/")
async def index():
    index_path = os.path.join(static_dir, "index.html")
    return FileResponse(index_path)

@app.get("/api/questions")
async def get_questions():
    return JSONResponse(content={"questions": questions})

@app.post("/api/submit")
async def submit_answers(request: SubmissionRequest):
    if len(request.behaviors) != 5 or len(request.choices) != 5:
        raise HTTPException(status_code=400, detail="需要完成所有5道题目")
    
    behavior_analysis = analyze_behaviors(request.behaviors)
    
    fortune = await ai_service.generate_fortune(behavior_analysis, request.choices)
    
    star_count = min(max(int(behavior_analysis['total_switches'] + 3), 5), 12)
    
    return JSONResponse(content={
        "success": True,
        "fortune": fortune.strip(),
        "star_count": star_count,
        "behavior_analysis": behavior_analysis
    })

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 9354))
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=True)
