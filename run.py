import sys

from dotenv import load_dotenv

load_dotenv()

from chatbot_template.app import create_app  # noqa: E402
from chatbot_template.preflight import ClaudeCliMissingError, check_claude_cli  # noqa: E402

if __name__ == "__main__":
    try:
        check_claude_cli()
    except ClaudeCliMissingError as e:
        print(f"\n啟動失敗：{e}\n", file=sys.stderr)
        sys.exit(1)

    create_app().run(host="127.0.0.1", port=5050, debug=True)
