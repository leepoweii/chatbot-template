"""subprocess 呼叫 claude -p。mock 掉 subprocess.run（唯一允許 mock 的外部呼叫），
驗證我們組的指令列與 JSON 解析對不對，不在測試裡燒真實額度。

也驗證三種「非工程背景使用者最容易撞到」的失敗模式，都要變成看得懂的錯誤訊息，
不是一路往上炸的 Python traceback：沒裝 CLI、沒登入（輸出不是 JSON）、執行失敗。"""
import json
import subprocess
from unittest.mock import patch, MagicMock

import pytest

from chatbot_template.claude_harness import ChatbotHarnessError, call_claude_harness


@patch("chatbot_template.claude_harness.subprocess.run")
def test_first_call_has_no_resume_flag_and_returns_new_session_id(mock_run):
    mock_run.return_value = MagicMock(
        stdout=json.dumps({"result": "哈囉！", "session_id": "abc-123"}),
        returncode=0,
    )

    outcome = call_claude_harness("哈囉", session_id=None, cwd="/tmp/demo")

    command = mock_run.call_args.args[0]
    assert command == ["claude", "-p", "哈囉", "--output-format", "json"]
    assert mock_run.call_args.kwargs["cwd"] == "/tmp/demo"
    assert outcome["reply"] == "哈囉！"
    assert outcome["session_id"] == "abc-123"
    assert outcome["command"] == command


@patch("chatbot_template.claude_harness.subprocess.run")
def test_followup_call_resumes_the_given_session_id(mock_run):
    mock_run.return_value = MagicMock(
        stdout=json.dumps({"result": "我記得剛剛的哈囉", "session_id": "abc-123"}),
        returncode=0,
    )

    outcome = call_claude_harness("你還記得我剛剛說什麼嗎", session_id="abc-123", cwd="/tmp/demo")

    command = mock_run.call_args.args[0]
    assert command == [
        "claude", "-p", "你還記得我剛剛說什麼嗎",
        "--output-format", "json",
        "--resume", "abc-123",
    ]
    assert outcome["reply"] == "我記得剛剛的哈囉"
    assert outcome["session_id"] == "abc-123"


@patch("chatbot_template.claude_harness.subprocess.run")
def test_missing_cli_raises_a_friendly_error_not_a_raw_traceback(mock_run):
    mock_run.side_effect = FileNotFoundError()

    with pytest.raises(ChatbotHarnessError, match="claude"):
        call_claude_harness("哈囉", session_id=None, cwd="/tmp/demo")


@patch("chatbot_template.claude_harness.subprocess.run")
def test_non_json_stdout_raises_a_friendly_error_hinting_at_login(mock_run):
    """沒登入時 claude -p 常常在 stdout 印一段人話而不是 JSON——這是最容易撞到的情況。"""
    mock_run.return_value = MagicMock(stdout="Please run `claude login` first.\n", returncode=1)

    with pytest.raises(ChatbotHarnessError, match="登入"):
        call_claude_harness("哈囉", session_id=None, cwd="/tmp/demo")


@patch("chatbot_template.claude_harness.subprocess.run")
def test_timeout_raises_a_friendly_error(mock_run):
    mock_run.side_effect = subprocess.TimeoutExpired(cmd=["claude"], timeout=120)

    with pytest.raises(ChatbotHarnessError, match="逾時|timeout"):
        call_claude_harness("哈囉", session_id=None, cwd="/tmp/demo")
