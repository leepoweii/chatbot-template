# CLAUDE.md — 路由 + 這個 chatbot 的知識庫索引

> 這份是 Claude 每次回答問題前會讀到的「目錄」，也是**啟動路由**：
> CLAUDE.md 只負責判斷現在該做什麼、呼叫哪支 skill，實際邏輯都寫在 skill 裡。

## 啟動路由

- 下面「這個 chatbot 是做什麼的」還寫著「（尚未設定）」→ 呼叫 `bootstrap-chatbot` skill
  （一次性起步：確認在自己的 repo 上、grill 到邊界收斂、準備資料、commit 一個乾淨的起點）
- 已經設定好了，使用者許願要加新功能／改東西 → 呼叫 `build-wish` skill
  （worktree + subagent 實作 + dev server 讓使用者點測，才 merge）
- 使用者是在問這個 chatbot 索引的問題（不是要改功能）→ 直接照下面「這個 chatbot 是做什麼的」
  ／「資料在哪裡」回答，不用呼叫 skill

## 這個 chatbot 是做什麼的
（尚未設定——`bootstrap-chatbot` skill 會引導你填這段）

## 資料在哪裡
- `data/` — （尚未設定）

## 回答風格
- 找不到答案就明講找不到，不要用猜的
- 回答時盡量講出資料是從哪個檔案找到的

## 開發慣例（`build-wish` 加新功能時照這個，讓每次許願長出來的東西風格一致）

- **檔案配置**：`src/chatbot_template/` 下一個關注點一支檔案（`app.py` 路由、
  `claude_harness.py` 呼叫 claude CLI 的膠水層、`preflight.py` 啟動前檢查、
  `security.py` 曝露/認證檢查）；`tests/test_<module>.py` 跟 `src/` 底下的模組 1:1 對應。
- **函式命名依回傳型態分工**：
  - `check_*`：純檢查，過了什麼都不做（如 `check_claude_cli`）
  - `*_warning`：回傳一句警告字串或 `None`，**不會**擋住流程（如 `lan_exposure_warning`）
  - `require_*`：條件不滿足就 `raise`，會擋住流程（如 `require_basic_auth_if_exposed`）
- **例外類別**：`<名詞>Error` 繼承 `RuntimeError`，**訊息本身就是要給使用者看的那句話**，
  不是給工程師 debug 用的堆疊資訊（如 `ChatbotHarnessError`、`ClaudeCliMissingError`）。
- **API route**：`/api/<動詞-名詞>`（如 `/api/chat`），POST body 用 `snake_case` 欄位。
- **環境變數**：`UPPER_SNAKE_CASE`，`.env.example` 用註解分段、每個變數旁邊寫一句話說明
  什麼時候才需要改它（不是每個變數都要碰）。
- **新 skill**：放 `.claude/skills/<動詞-名詞>/SKILL.md`（如 `bootstrap-chatbot`、
  `build-wish`），命名是祈使動詞開頭，一眼看出「呼叫這支會做什麼動作」。
- **commit message**：祈使句、講「為什麼」不是「做了什麼」（程式碼本身看得出做了什麼）。
