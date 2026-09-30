"""借用 Claude Code harness 本身的 session continuity 做記憶：真的用 subprocess
呼叫 `claude -p`，不用自己刻 append history。cwd 指到哪個資料夾，Claude 就讀那個
資料夾的 CLAUDE.md 當索引——這就是「agentic search」的全部：資料夾即知識庫。"""
import json
import subprocess


def call_claude_harness(message: str, session_id: str | None, cwd: str) -> dict:
    command = ["claude", "-p", message, "--output-format", "json"]
    if session_id:
        command += ["--resume", session_id]

    result = subprocess.run(command, cwd=cwd, capture_output=True, text=True, timeout=120)
    parsed = json.loads(result.stdout)

    return {
        "command": command,
        "reply": parsed["result"],
        "session_id": parsed["session_id"],
    }
