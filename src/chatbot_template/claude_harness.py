"""借用 Claude Code harness 本身的 session continuity 做記憶：真的用 subprocess
呼叫 `claude -p`，不用自己刻 append history。cwd 指到哪個資料夾，Claude 就讀那個
資料夾的 CLAUDE.md 當索引——這就是「agentic search」的全部：資料夾即知識庫。

錯誤處理刻意做得比較囉唆：這個 template 是給非工程背景的人改的，沒裝 CLI／沒登入／
執行逾時這三種最容易撞到的情況，都要變成看得懂的一句話，不是一路往上炸的 traceback。"""
import json
import subprocess


class ChatbotHarnessError(RuntimeError):
    """claude -p 執行失敗時的統一錯誤，訊息本身就是給使用者看的（不是給工程師 debug 用）。"""


def call_claude_harness(message: str, session_id: str | None, cwd: str) -> dict:
    command = ["claude", "-p", message, "--output-format", "json"]
    if session_id:
        command += ["--resume", session_id]

    try:
        result = subprocess.run(command, cwd=cwd, capture_output=True, text=True, timeout=120)
    except FileNotFoundError:
        raise ChatbotHarnessError(
            "找不到 `claude` 指令。請先安裝 Claude Code CLI "
            "（https://docs.anthropic.com/en/docs/claude-code）並確認它在 PATH 上。"
        )
    except subprocess.TimeoutExpired:
        raise ChatbotHarnessError("claude -p 執行逾時（超過 120 秒）。請稍後再試一次。")

    try:
        parsed = json.loads(result.stdout)
    except json.JSONDecodeError:
        hint = (result.stdout or result.stderr or "").strip()[:200]
        raise ChatbotHarnessError(
            "claude -p 沒有回傳預期的 JSON，最常見原因是還沒登入——"
            "請在終端機執行 `claude` 確認能不能正常對話、需要的話先跑 `claude login`。"
            + (f"\n\n實際輸出：{hint}" if hint else "")
        )

    return {
        "command": command,
        "reply": parsed["result"],
        "session_id": parsed["session_id"],
    }
