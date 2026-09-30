"""單一路由的 chatbot：把訊息丟給 claude -p，cwd 指到 HARNESS_CWD（預設是這個專案
自己的根目錄——那裡的 CLAUDE.md + data/ 就是隨包附的示範知識庫）。要換成你自己的
知識庫，改 .env 的 HARNESS_CWD 指到別的資料夾就好——那個資料夾自己要有 CLAUDE.md
當索引，Claude 會自己去讀。"""
import os
from pathlib import Path

from flask import Flask, jsonify, render_template, request

from chatbot_template.claude_harness import ChatbotHarnessError, call_claude_harness

PROJECT_ROOT = str(Path(__file__).resolve().parent.parent.parent)


def create_app(testing: bool = False) -> Flask:
    app = Flask(__name__)
    app.config["SECRET_KEY"] = os.environ.get("FLASK_SECRET_KEY", "dev-only-not-secret")
    app.config["TESTING"] = testing

    harness_cwd = os.environ.get("HARNESS_CWD") or PROJECT_ROOT

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
