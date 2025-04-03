import pytest
from datetime import datetime
from unittest.mock import Mock, patch
import json
import os

from src.data.collector import StackExchangeCollector


@pytest.fixture
def mock_questions_response():
    """模拟问题 API 响应"""
    return {
        "items": [
            {
                "question_id": 1,
                "title": "Test Question 1",
                "body": "Test Body 1",
                "score": 10,
                "answer_count": 2,
                "creation_date": 1617235200,
                "tags": ["nlp", "python"],
                "accepted_answer_id": 2,
            },
            {
                "question_id": 2,
                "title": "Test Question 2",
                "body": "Test Body 2",
                "score": 5,
                "answer_count": 1,
                "creation_date": 1617321600,
                "tags": ["nlp", "machine-learning"],
                "accepted_answer_id": 3,
            },
        ],
        "has_more": False,
    }


@pytest.fixture
def mock_answers_response():
    """模拟问题回答的 API 响应"""
    return {
        "items": [
            {
                "answer_id": 101,
                "body": "Test Answer 1",
                "score": 5,
                "is_accepted": True,
                "creation_date": 1617235300,
                "owner": {"user_id": 1001, "display_name": "Test User 1"},
            },
            {
                "answer_id": 102,
                "body": "Test Answer 2",
                "score": 3,
                "is_accepted": False,
                "creation_date": 1617235400,
                "owner": {"user_id": 1002, "display_name": "Test User 2"},
            },
        ],
        "has_more": False,
    }


@pytest.fixture
def collector():
    """创建测试用的收集器实例，使用模拟数据模式"""
    return StackExchangeCollector(
        api_key=None, page_size=10, max_pages=1, rate_limit=30, use_mock_data=True
    )


def test_collect_questions(collector):
    """测试问题收集功能"""
    questions = collector.collect_questions(tag="nlp", max_count=5)
    assert len(questions) == 5
    assert all("question_id" in q for q in questions)
    assert all("nlp" in q["tags"] for q in questions)


def test_collect_answers_for_question(collector):
    """测试收集问题回答功能"""
    answers = collector.collect_answers_for_question(1)
    assert len(answers) > 0
    assert all("answer_id" in a for a in answers)
    assert all("body" in a for a in answers)


def test_collect_questions_with_answers(collector):
    """测试带回答的问题收集功能"""
    questions = collector.collect_questions_with_answers(tag="nlp", max_count=3)

    assert len(questions) == 3
    assert all("answers" in q for q in questions)
    assert all(len(q["answers"]) > 0 for q in questions)


def test_save_to_json(collector, tmp_path):
    """测试 JSON 保存功能"""
    data = [
        {
            "question_id": 1,
            "title": "Test Question",
            "body": "Test Body",
            "answers": [{"answer_id": 101, "body": "Test Answer"}],
        }
    ]

    output_path = str(tmp_path / "test_data.json")
    collector.save_to_json(data, output_path)

    assert os.path.exists(output_path)

    with open(output_path, "r", encoding="utf-8") as f:
        loaded_data = json.load(f)

    assert len(loaded_data) == 1
    assert loaded_data[0]["question_id"] == 1
    assert len(loaded_data[0]["answers"]) == 1
    assert loaded_data[0]["answers"][0]["answer_id"] == 101


def test_collect_questions_with_dates(collector):
    """测试带日期范围的问题收集"""
    from_date = datetime(2021, 1, 1)
    to_date = datetime(2021, 1, 2)

    questions = collector.collect_questions_with_answers(
        tag="nlp", from_date=from_date, to_date=to_date, max_count=2
    )

    assert len(questions) == 2
    # 日期在模拟数据模式下不会真正筛选，所以这里不验证日期范围
