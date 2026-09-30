"""Flask route 串接測試：mock 掉唯一的外部呼叫點（claude_harness），
驗證路由組出去的 session_id 邏輯跟回傳的 JSON 形狀是對的。"""
from unittest.mock import patch

import pytest

from chatbot_template.app import PROJECT_ROOT, create_app
from chatbot_template.claude_harness import ChatbotHarnessError


@pytest.fixture
def client():
    app = create_app(testing=True)
    app.config["SECRET_KEY"] = "test-secret"
    with app.test_client() as client:
        yield client


@patch("chatbot_template.app.call_claude_harness")
def test_starts_a_brand_new_session_when_client_sends_no_session_id(mock_call, client):
    mock_call.return_value = {"reply": "哈囉！", "session_id": "abc-123", "command": ["claude", "-p", "哈囉"]}

    r = client.post("/api/chat", json={"message": "哈囉", "session_id": None})

    assert mock_call.call_args.kwargs["session_id"] is None
    assert r.get_json()["session_id"] == "abc-123"


@patch("chatbot_template.app.call_claude_harness")
def test_resumes_exactly_the_session_id_the_client_sends(mock_call, client):
    mock_call.return_value = {"reply": "我記得", "session_id": "abc-123", "command": []}

    client.post("/api/chat", json={"message": "你還記得嗎", "session_id": "abc-123"})

    assert mock_call.call_args.kwargs["session_id"] == "abc-123"


@patch("chatbot_template.app.call_claude_harness")
def test_starting_a_second_session_does_not_touch_the_first(mock_call, client):
    mock_call.side_effect = [
        {"reply": "A 你好", "session_id": "session-a", "command": []},
        {"reply": "B 你好，這是新的", "session_id": "session-b", "command": []},
    ]

    client.post("/api/chat", json={"message": "我是A", "session_id": None})
    r2 = client.post("/api/chat", json={"message": "我是B", "session_id": None})

    assert mock_call.call_args_list[1].kwargs["session_id"] is None  # 開新的，不是 resume session-a
    assert r2.get_json()["session_id"] == "session-b"


@patch("chatbot_template.app.call_claude_harness")
def test_falls_back_to_project_root_when_harness_cwd_env_is_empty_string(mock_call, monkeypatch):
    monkeypatch.setenv("HARNESS_CWD", "")  # 這是 .env.example 沒填值時的實際狀態，不是「沒設」
    mock_call.return_value = {"reply": "ok", "session_id": "x", "command": []}

    app = create_app(testing=True)
    app.config["SECRET_KEY"] = "test-secret"
    with app.test_client() as client:
        client.post("/api/chat", json={"message": "hi"})

    # 預設要指到隨包的 CLAUDE.md + data/，不是隨便一個 tempdir
    assert mock_call.call_args.kwargs["cwd"] == PROJECT_ROOT
    assert mock_call.call_args.kwargs["cwd"] != ""


@patch("chatbot_template.app.call_claude_harness")
def test_harness_error_becomes_a_readable_500_not_a_stack_trace(mock_call, client):
    """非工程背景的人（例如種子自己）撞到沒登入/沒裝 CLI 時，前端要看得懂錯在哪，
    不是一片看不懂的 500 HTML 錯誤頁。"""
    mock_call.side_effect = ChatbotHarnessError("找不到 `claude` 指令，請先安裝並登入。")

    r = client.post("/api/chat", json={"message": "哈囉", "session_id": None})

    assert r.status_code == 500
    assert r.get_json()["error"] == "找不到 `claude` 指令，請先安裝並登入。"
