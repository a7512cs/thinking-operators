# thinking-operators

問答式解題引擎（Claude Code plugin）。當你卡在一個問題上，它用問答帶你走一遍解題流程：
先把問題釐清，再從 55 個「思考運算子」（12 家族：加減乘除反代變時問資散驗）裡挑合適的思路，
逐招生出具體點子讓你選，最後收斂成方案。tracker 腳本記錄每招的使用狀態，
你每次送出訊息時 hook 自動回報一行 🧩 狀態——人和 AI 都不會亂。

這 55 招整併自八份經典清單：

- 奧斯本檢核表（Osborn Checklist）
- SCAMPER 奔馳法
- 和田十二法（創意十二訣）
- TRIZ 40 個發明原理
- SIT 系統性創新思考（《盒內思考》）
- Pólya《怎樣解題》解題啟發法
- 讀書猿《問題解決大全》＋《點子大全》
- 通用思維模型（蒙格、Farnam Street 等）

## 安裝

```bash
claude plugin marketplace add a7512cs/thinking-operators
claude plugin install thinking-operators@thinking-operators
```

不用預先建立任何資料夾。

開發者改完程式碼要讓已安裝的 plugin 更新：marketplace 快照是從 GitHub 拉的，
所以流程是 **commit → push →** `claude plugin marketplace update thinking-operators` **→ uninstall/install 重裝**。

## 用法

在你想解題的資料夾開一個 Claude Code session，輸入：

```
/thinking-operators:solve            # 打 /solve 會模糊比對到
/thinking-operators:solve --resume   # 繼續這個資料夾上次未結束的 session
```

- 只能手動觸發（`disable-model-invocation: true`），不會在平常工作時自己跳出來。

## 解題單存在哪？

**在你跑指令的資料夾**：第一場 session 會建立 `./solve-sessions/`，
之後每場一個子資料夾（`worksheet.md` ＋ `state.json`）。
腳本會從當下目錄往上找 `solve-sessions/`（跟 git 找 `.git` 同一邏輯），
所以在專案的子目錄裡也能接上同一場 session。每個資料夾同一時間只有一場 active。

要不要把 `solve-sessions/` commit 進你的 git 由你決定（`.active` 暫存檔已自動 gitignore）。
**注意：worksheet 含你的問題原文，公開 repo 請自行留意。**

## 結構

```
.claude-plugin/marketplace.json      marketplace 定義
plugins/thinking-operators/
├── .claude-plugin/plugin.json
├── skills/solve/SKILL.md            問答流程
├── references/operators.json        55 招機讀版（tracker 與 SKILL 的單一事實來源）
├── references/operators.md          55 招人讀版
├── references/sources.md            185 條原始清單全文（延伸閱讀）
├── scripts/tracker.py               session 狀態追蹤（start/triage/ask/used/skip/status/unused/end/resume/list）
├── scripts/statusline.sh            UserPromptSubmit hook：有 active session 才吐狀態行
└── hooks/hooks.json
CONTEXT.md                           詞彙表
docs/adr/                            決策紀錄
```

## 限制

- macOS / Linux（hook 是 bash script）；Windows 未測試。
- 解題單的「結果回填」欄請事後補：累積「哪招真的救過我」的資料。
