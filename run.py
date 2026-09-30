import os
import sys

from dotenv import load_dotenv

load_dotenv()

from chatbot_template.app import create_app  # noqa: E402
from chatbot_template.preflight import ClaudeCliMissingError, check_claude_cli  # noqa: E402
from chatbot_template.security import lan_exposure_warning, require_basic_auth_if_exposed  # noqa: E402

if __name__ == "__main__":
    host = os.environ.get("HOST", "127.0.0.1")
    port = int(os.environ.get("PORT", "5050"))

    try:
        check_claude_cli()
        require_basic_auth_if_exposed(
            host=host,
            auth_password=os.environ.get("BASIC_AUTH_PASSWORD"),
            allow_insecure=os.environ.get("ALLOW_INSECURE_LAN", "").lower() == "true",
        )
    except (ClaudeCliMissingError, RuntimeError) as e:
        print(f"\n啟動失敗：{e}\n", file=sys.stderr)
        sys.exit(1)

    warning = lan_exposure_warning(host)
    if warning:
        print(f"\n{warning}\n")

    create_app().run(host=host, port=port, debug=True)
