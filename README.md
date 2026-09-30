# chatbot-template

一個「資料夾即知識庫」的 agentic search chatbot 起手式。不用向量資料庫、不用 embedding
——記憶跟檢索全部交給 Claude Code harness 自己管：後端只是 subprocess 呼叫 `claude -p`，
cwd 指到一個有 `CLAUDE.md` 當索引的資料夾，Claude 自己會去讀資料回答問題。

延伸自 [llm-memory-101](https://github.com/leepoweii/llm-memory-101) 情境 3（`claude -p` +
`--resume` 做 session 記憶），把它包成一個可以直接拿去改的 chatbot 骨架。

## 改成你自己的 chatbot

在這個資料夾裡開 `claude`，跟它說一句話（例如「幫我設定這個 chatbot」）——`CLAUDE.md`
最上面是路由，會自動呼叫 `bootstrap-chatbot` skill 引導你：確認你是不是還在範本上（是
的話先幫你建自己的 repo）、問到「這個 chatbot 要做什麼」的邊界收斂、幫你把資料準備好、
最後 commit 一個乾淨的起點。

設定好之後，之後每次想加新功能都直接跟 `claude` 說你想要什麼——`build-wish` skill 會
接手：開一個獨立的 worktree／branch 讓 subagent 動手做、做完起一個 dev server 讓你自己
點過一輪，你確認堪用才會合併回來。main 分支永遠是最後一個你確認過能動的版本。

## 跑起來

```bash
uv sync
uv run python run.py
```

開 http://127.0.0.1:5050——不用另外建 `.env`，預設值就能跑（下面「換成你自己的知識庫」再說明要改什麼）。

需要本機已裝好且登入過 [Claude Code CLI](https://docs.anthropic.com/en/docs/claude-code)
（`claude` 指令要在 PATH 上）。沒裝好會在啟動時直接報錯，不用等你送出第一句話才發現。
**每次呼叫都會真的燒 Claude 額度**，示範前抓一下大概成本。

## 換成你自己的知識庫

```bash
cp .env.example .env
```

`.env` 的 `HARNESS_CWD` 留空時，預設指到這個 repo 自己的根目錄（也就是這份 `CLAUDE.md` +
`data/`）。要換成別的資料夾——例如你自己另外整理的一份客戶資料——把 `HARNESS_CWD` 指過去，
並確保那個資料夾裡也有一份 `CLAUDE.md` 當索引就好，程式碼不用改。改完 `.env` 要重啟服務
（環境變數只在啟動時讀一次）。

## 部署到區網讓同事連（跟課堂教的一樣）

改 `.env`：

```bash
cp .env.example .env
# 編輯 .env：HOST=0.0.0.0
```

`HOST` 一旦不是 `127.0.0.1`，就是開放給整個網段連——這時候**必須**二選一，否則直接拒絕啟動：
- 設 `BASIC_AUTH_PASSWORD`（推薦；帳號固定是 `welly`，同事連上會被問密碼）
- 或明確設 `ALLOW_INSECURE_LAN=true`（你確定這個網路安全、不想要密碼）

這個檢查是刻意做成「擋住裸奔的組合」，不是自動幫你上鎖——你還是要自己決定要不要設密碼。

## 測試 + Lint

```bash
uv run ruff check .
uv run pytest tests/ -v
```

測試全部是 mock 掉 `subprocess.run` 的單元測試，跑測試不會打真實 API、不燒額度。
`build-wish` 每次許願完成前都會跑這兩個，兩個都要乾淨才算做完。

## 架構

```
.claude/skills/
├── bootstrap-chatbot/   # 一次性起步：範本偵測、grill 邊界、準備資料、commit 乾淨起點
└── build-wish/          # 每次新功能許願：worktree + subagent 實作 + dev server 點測 + 才 merge
src/chatbot_template/
├── claude_harness.py   # 膠水層：subprocess 呼叫 claude -p，處理 --resume，錯誤訊息看得懂
├── preflight.py         # 啟動前檢查 claude CLI 在不在 PATH 上
├── security.py          # LAN 曝露檢查＋Basic Auth（見上面「部署到區網」）
├── app.py               # 單一路由 Flask app
├── templates/index.html
└── static/{style.css,app.js}
data/                    # 你的知識庫文件放這裡
CLAUDE.md                # 啟動路由 + 知識庫索引 + 開發慣例（Claude 每次都會讀）
tests/                   # 對應 claude_harness / app / preflight / security 四支測試
```
