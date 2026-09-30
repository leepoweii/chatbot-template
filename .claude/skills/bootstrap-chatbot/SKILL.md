---
name: bootstrap-chatbot
description: One-time setup for a fresh chatbot-template clone — get the user onto their own repo, grill them for the full scope of what the chatbot should do, help them organize data/, and commit a working baseline. Use when CLAUDE.md still has "（尚未設定）" placeholders, or the user just cloned/forked chatbot-template.
---

# bootstrap-chatbot

一次性的起步流程。做完之後這支 skill 就不會再被叫到——之後的每個新功能許願走
`build-wish`，不會再回來這裡。

## Step 0 · 確認在自己的 repo 上

```bash
git remote -v
```

- 出現 `leepoweii/chatbot-template` → 還在範本上，先做下面這段
- 出現使用者自己的 repo → 跳到 Step 1

範本上要先幫使用者建自己的 repo。**問清楚 repo 要叫什麼、開在誰名下**（個人帳號還是公司
org）——這件事之後很難改，不要幫他決定：

```bash
gh repo create <他們的repo名> --template leepoweii/chatbot-template --private --clone
```

沒有 `gh` 權限時，請他到範本頁面按 **Use this template**，等他給新的 clone 路徑。

## Step 1 · Grill：問到邊界收斂，不是問兩題就結束

這步的目的不是填 `CLAUDE.md` 的兩個欄位，是**真的搞清楚這個 chatbot 的邊界**——後面
`build-wish` 每一次許願都是在這個邊界內動作，邊界沒問清楚，後面每次都要重新猜。

按「決策樹＋frontier」的方式問（參考 grill-me 手法）：**先問現在問得出來的所有題**（不
依賴其他還沒問的答案），每題附你的建議答案，一次全部列出來、等使用者一輪回完，再依答案
展開下一輪還沒問到的題。**能自己查的別問使用者**——例如「這個資料夾裡已經有什麼檔案」
自己去看，不要反過來問他。

第一輪通常問得出來的（不用等其他答案）：

```
❓ Q1 - 這個 chatbot 要回答什麼問題？
一句話就好，例如「回答關於 XX 專案優化紀錄表的問題」。

➡️ （你的建議，根據你對這個人/專案已知的脈絡給一個合理猜測）

---

❓ Q2 - 資料放哪？
用這個 repo 自帶的 data/，還是要指到一個已經存在的資料夾？

➡️ 沒有特殊理由就用 data/，之後要換也只是改 .env 的 HARNESS_CWD

---

❓ Q3 - 這個 chatbot 只有你自己用，還是要給同事/客戶用？
會決定後面要不要處理 LAN 曝露與密碼保護。

➡️ 先只有自己用，之後要開放區網再處理（見 README「部署到區網」段）
```

依 Q1/Q2 的答案，可能會展開第二輪（例如 Q1 若牽涉到會一直更新的資料 vs 固定不變的資料，
會影響要不要在 CLAUDE.md 裡寫「資料多久更新一次」）。**問到 frontier 淨空**（沒有還沒問
到、也不是等其他答案展開的題）才算完，別自己腦補邊界。

## Step 2 · 準備資料

- 選 `data/`：提醒使用者把文件丟進去（子資料夾也可以，PDF/Word/Excel/純文字都可以）
- 指到別的資料夾：改 `.env` 的 `HARNESS_CWD`；確認那個資料夾有沒有自己的 `CLAUDE.md`，
  沒有就模仿這份的骨架先建一份

## Step 3 · 寫回 CLAUDE.md

把 Step 1 問到的答案覆寫進 `CLAUDE.md` 的「這個 chatbot 是做什麼的」跟「資料在哪裡」兩段。

## Step 4 · 驗證

```bash
uv sync
uv run ruff check .
uv run pytest tests/ -v
uv run python run.py
```

實際問它一兩句話（用 Step 2 準備的真資料），確認真的答得出來，不只是「跑得起來」。

## Step 5 · Commit 一個乾淨的起點

**明確列出要加的檔案**（不要 `git add -A`／`.`，這個 repo 的 `.gitignore` 已經擋掉
`.venv`／`.env`，但養成明確列檔案的習慣，之後改別人專案時才不會失手加進不該進的東西）：

```bash
git add CLAUDE.md data/
git commit -m "Configure chatbot: <一句話帶過 Step 1 的答案>"
```

這一步做完，之後每個新功能許願都從這個乾淨的起點開一個新 branch——`build-wish` 接手。
