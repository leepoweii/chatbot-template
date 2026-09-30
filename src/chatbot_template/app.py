"""單一路由的 chatbot：把訊息丟給 claude -p，cwd 指到 HARNESS_CWD（預設是這個專案
自己的根目錄——那裡的 CLAUDE.md + data/ 就是隨包附的示範知識庫）。要換成你自己的
知識庫，改 .env 的 HARNESS_CWD 指到別的資料夾就好——那個資料夾自己要有 CLAUDE.md
當索引，Claude 會自己去讀。"""
import hmac
import os
from pathlib import Path

from flask import Flask, Response, jsonify, render_template, request

from chatbot_template.claude_harness import ChatbotHarnessError, call_claude_harness

PROJECT_ROOT = str(Path(__file__).resolve().parent.parent.parent)
BASIC_AUTH_USER = "welly"


def create_app(testing: bool = False) -> Flask:
    app = Flask(__name__)
    app.config["SECRET_KEY"] = os.environ.get("FLASK_SECRET_KEY", "dev-only-not-secret")
    app.config["TESTING"] = testing

    harness_cwd = os.environ.get("HARNESS_CWD") or PROJECT_ROOT
    basic_auth_password = os.environ.get("BASIC_AUTH_PASSWORD")

    @app.before_request
    def enforce_basic_auth():
        """只在設了 BASIC_AUTH_PASSWORD 時才擋——本機/loopback 用途完全不受影響。
        見 security.require_basic_auth_if_exposed：綁區網 IP 卻沒設這個會直接拒絕啟動。"""
        if not basic_auth_password:
            return None
        auth = request.authorization
        ok = auth and auth.username == BASIC_AUTH_USER and hmac.compare_digest(
            auth.password or "", basic_auth_password
        )
        if not ok:
            return Response(
                "需要登入才能使用這個 chatbot。",
                401,
                {"WWW-Authenticate": 'Basic realm="chatbot-template"'},
            )
        return None

    @app.get("/")
    def index():
        return render_template("index.html")

    @app.post("/api/chat")
    def chat():
        """Client-driven on purpose：前端自己決定要不要帶 session_id，伺服器完全無狀態，
        這樣才能在同一個分頁裡開多個獨立 session、切換著問。"""
        message = request.json["message"]
        session_id = request.json.get("session_id")
        try:
            outcome = call_claude_harness(message, session_id=session_id, cwd=harness_cwd)
        except ChatbotHarnessError as e:
            return jsonify(error=str(e)), 500
        return jsonify(outcome)

    return app
