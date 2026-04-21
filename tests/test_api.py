import pytest
from fastapi.testclient import TestClient
from backend.main import app, analyze_behaviors, BehaviorData

client = TestClient(app)


class TestQuestionsAPI:
    """测试问题相关 API"""

    def test_get_questions(self):
        """测试获取问题列表"""
        response = client.get("/api/questions")
        
        assert response.status_code == 200
        data = response.json()
        
        assert "questions" in data
        questions = data["questions"]
        
        assert len(questions) == 5
        
        for q in questions:
            assert "id" in q
            assert "text" in q
            assert "options" in q
            assert "theme" in q
            assert len(q["options"]) == 4
            
            for option in q["options"]:
                assert "id" in option
                assert "text" in option

    def test_first_question_structure(self):
        """测试第一个问题的结构"""
        response = client.get("/api/questions")
        data = response.json()
        first_question = data["questions"][0]
        
        assert first_question["id"] == 1
        assert first_question["text"] == "你更愿意被哪种风吹散？"
        assert first_question["theme"] == "探索与归宿"


class TestBehaviorAnalysis:
    """测试行为数据分析逻辑"""

    def test_analyze_behaviors_thoughtful(self):
        """测试深思熟虑型行为分析"""
        behaviors = [
            BehaviorData(question_id=1, duration_seconds=6.0, switch_count=2, final_choice="A"),
            BehaviorData(question_id=2, duration_seconds=7.0, switch_count=3, final_choice="B"),
            BehaviorData(question_id=3, duration_seconds=5.5, switch_count=1, final_choice="C"),
            BehaviorData(question_id=4, duration_seconds=6.5, switch_count=2, final_choice="D"),
            BehaviorData(question_id=5, duration_seconds=5.0, switch_count=1, final_choice="A"),
        ]
        
        result = analyze_behaviors(behaviors)
        
        assert result["avg_duration"] == 6.0
        assert result["total_switches"] == 9
        assert "深思熟虑" in result["behavior_traits"]
        assert "追求完美" in result["behavior_traits"]
        assert "谨慎型决策" in result["decision_style"]

    def test_analyze_behaviors_intuitive(self):
        """测试直觉型行为分析"""
        behaviors = [
            BehaviorData(question_id=1, duration_seconds=1.0, switch_count=0, final_choice="A"),
            BehaviorData(question_id=2, duration_seconds=1.5, switch_count=0, final_choice="B"),
            BehaviorData(question_id=3, duration_seconds=2.0, switch_count=0, final_choice="C"),
            BehaviorData(question_id=4, duration_seconds=1.8, switch_count=0, final_choice="D"),
            BehaviorData(question_id=5, duration_seconds=2.2, switch_count=0, final_choice="A"),
        ]
        
        result = analyze_behaviors(behaviors)
        
        assert result["avg_duration"] == 1.7
        assert result["total_switches"] == 0
        assert "直觉敏锐" in result["behavior_traits"]
        assert "坚定果断" in result["behavior_traits"]
        assert "直觉型决策" in result["decision_style"]

    def test_analyze_behaviors_balanced(self):
        """测试平衡型行为分析"""
        behaviors = [
            BehaviorData(question_id=1, duration_seconds=4.0, switch_count=1, final_choice="A"),
            BehaviorData(question_id=2, duration_seconds=3.5, switch_count=2, final_choice="B"),
            BehaviorData(question_id=3, duration_seconds=4.5, switch_count=1, final_choice="C"),
            BehaviorData(question_id=4, duration_seconds=3.0, switch_count=0, final_choice="D"),
            BehaviorData(question_id=5, duration_seconds=4.0, switch_count=1, final_choice="A"),
        ]
        
        result = analyze_behaviors(behaviors)
        
        assert result["avg_duration"] == 3.8
        assert result["total_switches"] == 5
        assert "平衡和谐" in result["behavior_traits"]
        assert "平衡型决策" in result["decision_style"]


class TestSubmitAPI:
    """测试提交答案 API"""

    def test_submit_valid_data(self):
        """测试提交有效数据"""
        payload = {
            "behaviors": [
                {"question_id": 1, "duration_seconds": 3.0, "switch_count": 1, "final_choice": "A"},
                {"question_id": 2, "duration_seconds": 4.0, "switch_count": 2, "final_choice": "B"},
                {"question_id": 3, "duration_seconds": 2.5, "switch_count": 0, "final_choice": "C"},
                {"question_id": 4, "duration_seconds": 5.0, "switch_count": 1, "final_choice": "D"},
                {"question_id": 5, "duration_seconds": 3.5, "switch_count": 2, "final_choice": "A"},
            ],
            "choices": ["A", "B", "C", "D", "A"]
        }
        
        response = client.post("/api/submit", json=payload)
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["success"] == True
        assert "fortune" in data
        assert "star_count" in data
        assert "behavior_analysis" in data
        
        assert len(data["fortune"]) > 0
        assert 5 <= data["star_count"] <= 12
        
        analysis = data["behavior_analysis"]
        assert "avg_duration" in analysis
        assert "total_switches" in analysis
        assert "behavior_traits" in analysis
        assert "decision_style" in analysis

    def test_submit_incomplete_data(self):
        """测试提交不完整数据"""
        payload = {
            "behaviors": [
                {"question_id": 1, "duration_seconds": 3.0, "switch_count": 1, "final_choice": "A"},
                {"question_id": 2, "duration_seconds": 4.0, "switch_count": 2, "final_choice": "B"},
                {"question_id": 3, "duration_seconds": 2.5, "switch_count": 0, "final_choice": "C"},
            ],
            "choices": ["A", "B", "C"]
        }
        
        response = client.post("/api/submit", json=payload)
        
        assert response.status_code == 400
        data = response.json()
        
        assert "detail" in data

    def test_submit_empty_data(self):
        """测试提交空数据"""
        payload = {
            "behaviors": [],
            "choices": []
        }
        
        response = client.post("/api/submit", json=payload)
        
        assert response.status_code == 400


class TestFrontendStaticFiles:
    """测试前端静态文件"""

    def test_index_page(self):
        """测试主页加载"""
        response = client.get("/")
        
        assert response.status_code == 200
        assert "text/html" in response.headers["content-type"]
        
        content = response.text
        assert "Astro Fate" in content
        assert "命运星图" in content

    def test_css_file(self):
        """测试 CSS 文件加载"""
        response = client.get("/static/css/style.css")
        
        assert response.status_code == 200
        assert "text/css" in response.headers["content-type"]

    def test_js_file(self):
        """测试 JavaScript 文件加载"""
        response = client.get("/static/js/app.js")
        
        assert response.status_code == 200
        assert "javascript" in response.headers["content-type"]


class TestUseCases:
    """用户场景测试"""

    def test_complete_flow(self):
        """测试完整流程：获取问题 -> 提交答案"""
        response = client.get("/api/questions")
        assert response.status_code == 200
        questions = response.json()["questions"]
        assert len(questions) == 5
        
        behaviors = []
        choices = []
        for i, q in enumerate(questions):
            behaviors.append({
                "question_id": q["id"],
                "duration_seconds": 2.5 + i,
                "switch_count": i % 3,
                "final_choice": q["options"][0]["id"]
            })
            choices.append(q["options"][0]["id"])
        
        submit_payload = {
            "behaviors": behaviors,
            "choices": choices
        }
        
        submit_response = client.post("/api/submit", json=submit_payload)
        assert submit_response.status_code == 200
        
        result = submit_response.json()
        assert result["success"] == True
        assert len(result["fortune"]) > 0
        assert 5 <= result["star_count"] <= 12

    def test_different_decision_styles(self):
        """测试不同决策风格的输出"""
        test_cases = [
            {
                "name": "谨慎型",
                "behaviors": [
                    {"question_id": 1, "duration_seconds": 8.0, "switch_count": 3, "final_choice": "A"},
                    {"question_id": 2, "duration_seconds": 7.0, "switch_count": 2, "final_choice": "B"},
                    {"question_id": 3, "duration_seconds": 9.0, "switch_count": 4, "final_choice": "C"},
                    {"question_id": 4, "duration_seconds": 6.0, "switch_count": 2, "final_choice": "D"},
                    {"question_id": 5, "duration_seconds": 7.5, "switch_count": 3, "final_choice": "A"},
                ],
                "choices": ["A", "B", "C", "D", "A"]
            },
            {
                "name": "直觉型",
                "behaviors": [
                    {"question_id": 1, "duration_seconds": 1.0, "switch_count": 0, "final_choice": "A"},
                    {"question_id": 2, "duration_seconds": 1.5, "switch_count": 0, "final_choice": "B"},
                    {"question_id": 3, "duration_seconds": 0.8, "switch_count": 0, "final_choice": "C"},
                    {"question_id": 4, "duration_seconds": 1.2, "switch_count": 0, "final_choice": "D"},
                    {"question_id": 5, "duration_seconds": 0.9, "switch_count": 0, "final_choice": "A"},
                ],
                "choices": ["A", "B", "C", "D", "A"]
            }
        ]
        
        for test_case in test_cases:
            response = client.post("/api/submit", json={
                "behaviors": test_case["behaviors"],
                "choices": test_case["choices"]
            })
            
            assert response.status_code == 200, f"{test_case['name']} 测试失败"
            data = response.json()
            
            assert data["success"] == True
            assert len(data["fortune"]) > 0
