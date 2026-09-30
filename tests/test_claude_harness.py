"""subprocess 呼叫 claude -p。mock 掉 subprocess.run（唯一允許 mock 的外部呼叫），
驗證我們組的指令列與 JSON 解析對不對，不在測試裡燒真實額度。"""
import json
from unittest.mock import patch, MagicMock

from chatbot_template.claude_harness import call_claude_harness


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
