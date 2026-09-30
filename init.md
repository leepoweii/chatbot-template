# 啟動精靈——只跑一次

這個 repo 剛 clone 下來，`CLAUDE.md` 還沒設定完成。照下面步驟引導使用者把它設定成他要的
chatbot；**設定完成後，把這份 `init.md` 刪掉，並且把 `CLAUDE.md` 最上面 `@init.md` 那一行
拿掉**——這份檔案跟這行 import 只用這一次，設定完就是雜訊。

## Step 1 · 問清楚

問使用者兩件事：
1. 這個 chatbot 要回答什麼問題？（一句話就好，例如「回答關於 XX 專案優化紀錄表的問題」）
2. 資料要放哪：用這個 repo 自帶的 `data/` 資料夾，還是要指到一個已經存在的資料夾？

## Step 2 · 準備資料

- 選 `data/`：提醒使用者把文件丟進去（子資料夾也可以，Claude 讀得動 PDF/Word/Excel/純文字）。
- 指到別的資料夾：把 `.env` 的 `HARNESS_CWD` 改指過去；檢查那個資料夾裡有沒有自己的
  `CLAUDE.md`——沒有就先幫他在那邊建一份最簡單的索引（模仿這份 `CLAUDE.md` 的骨架就好）。

## Step 3 · 寫回 CLAUDE.md

把 Step 1 問到的答案，覆寫進 `CLAUDE.md` 的「這個 chatbot 是做什麼的」跟「資料在哪裡」兩段
（取代「尚未設定」的預留字）。「回答風格」那段是通用預設，沒特別需求就留著。

## Step 4 · 清場

1. 刪除這份 `init.md`
2. 把 `CLAUDE.md` 最上面的 `@init.md` 那一行拿掉
3. 跟使用者說可以 `uv run python run.py` 試跑了（要先 `uv sync` 跟 `cp .env.example .env`）
