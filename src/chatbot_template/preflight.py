"""啟動前檢查：只檢查 `claude` 在不在 PATH 上——這是最快出錯、也最容易解決的一種
問題，值得在伺服器啟動前就講清楚，不要等使用者在瀏覽器裡送出第一句話才發現。

（登入與否沒有在這裡檢查：那要真的燒一次額度呼叫才知道，交給 claude_harness 的
執行期錯誤處理去講，別在每次啟動 server 就先燒一次錢。）"""
import shutil


class ClaudeCliMissingError(RuntimeError):
    """訊息本身就是給使用者看的。"""


def check_claude_cli() -> None:
    if shutil.which("claude") is None:
        raise ClaudeCliMissingError(
            "找不到 `claude` 指令。請先安裝 Claude Code CLI "
            "（https://docs.anthropic.com/en/docs/claude-code）、"
            "登入（`claude login`），並確認它在 PATH 上，再重新啟動這個服務。"
        )
