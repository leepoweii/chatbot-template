---
name: build-wish
description: Turn one feature wish into an isolated, tested, reviewable change — new branch in a worktree, subagent implements with small commits, dev server to click-test before merging. Use for any post-bootstrap change to a chatbot-template-based project (the user already has a working baseline from bootstrap-chatbot).
---

# build-wish

每個許願都在一個隔離的 worktree／branch 裡完成，main 永遠是最後一個確認能動的狀態
——這是防呆機制，不是流程負擔：vibe coding 最常見的死法是「改 A 壞了 B、回不去」，
這支 skill 存在就是為了讓「回不去」這件事不會發生。

## Step 0 · 確認起點乾淨

```bash
git status --short
```

有未 commit 的東西 → 先問使用者要不要先處理掉（commit 或捨棄），別把舊的未完成狀態
一起帶進新 worktree。

## Step 1 · 收斂許願（不用整套 grill，抓到能動手的程度就好）

使用者一句話許願之後，只在**會影響怎麼做**的地方追問（不是走完整 frontier 那套）——
例如許願含糊到有兩種合理做法時才問，許願本身夠具體就直接進 Step 2。

## Step 2 · 開 worktree，dispatch 去實作

```bash
git worktree add ../chatbot-template-wish-<slug> -b wish/<slug>
```

用 `Agent` 工具、`isolation: "worktree"`，把許願原文＋這個專案的 `CLAUDE.md` 脈絡交給它。
**明確要求它照 TDD 小步前進、每過一個小階段就 commit 一次**（紅→綠→commit，不要憋到全部
做完才一次 commit——中途出事才有回頭路）。commit 只 `git add` 明確列出的檔案。

過程中 subagent 若回報判斷性的選擇（不是單純是非題，而是「有兩三種做法、各有取捨」）→
用 `decision-form` skill 開一個網頁，把選項＋取捨列清楚，讓使用者選＋留言，結果存 JSON
餵回去繼續做。簡單是非題直接問，別為了一兩題也開網頁。

## Step 3 · 驗證

在那個 worktree 裡：

```bash
uv run ruff check .
uv run pytest tests/ -v
```

兩個都要過。lint 不是風格潔癖——這個 repo 之後可能被非工程背景的人（或另一個 agent）
繼續改，乾淨的 import／沒有死變數，是下一個人（或下一次許願）比較好接手的基本條件。

## Step 4 · 起 dev server 讓使用者實際點看看

跟 main 的 dev server 用不同 port（避免衝突）：

```bash
cd ../chatbot-template-wish-<slug>
PORT=5051 uv run python run.py
```

給使用者連結，讓他真的點過一輪再決定要不要留。**這步不能省**——測試綠燈不代表功能
順手好用，只有人親自點過才知道。

## Step 5 · 回報

用 `show-me` skill 彙整：這次做了什麼、commit log（讓使用者看到是一步步做的，不是一坨
黑箱）、dev server 連結、還有沒有已知的取捨/限制。

## Step 6 · 收尾

問使用者三選一：
- **合併**：`git merge wish/<slug>` 回 main，`git worktree remove` 清掉這個 worktree
- **繼續改**：留著 worktree，下一輪許願接著在這個 branch 上做
- **捨棄**：`git worktree remove --force`，branch 留著或刪掉都行，main 完全沒受影響

**別自動合併**——這是「使用者確認過、覺得堪用」才進 main 的關卡，不是做完就自動進。
