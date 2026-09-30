"""啟動前檢查：claude CLI 不在 PATH 上，要在伺服器啟動前就講清楚，
不要等使用者送出第一句話才在瀏覽器裡看到錯誤。"""
from unittest.mock import patch

from chatbot_template.preflight import check_claude_cli


@patch("chatbot_template.preflight.shutil.which", return_value="/usr/local/bin/claude")
def test_passes_silently_when_claude_is_on_path(mock_which):
    assert check_claude_cli() is None  # 不拋例外就是過


@patch("chatbot_template.preflight.shutil.which", return_value=None)
def test_raises_a_readable_message_when_claude_is_missing(mock_which):
    import pytest

    from chatbot_template.preflight import ClaudeCliMissingError

    with pytest.raises(ClaudeCliMissingError, match="claude"):
        check_claude_cli()
