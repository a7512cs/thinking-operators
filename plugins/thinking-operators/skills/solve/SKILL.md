---
name: solve
description: 問答式解題：分診 → 選家族 → 每回合兩招生候選 → 收斂（只手動觸發）
disable-model-invocation: true
---

# solve — 思考運算子問答解題

把本檔所在目錄記為 `SKILL_DIR`：

- **TRACKER**＝`SKILL_DIR/../../scripts/tracker.py`（用 `python3` 跑；不帶參數會印用法）
- **運算子總表**＝`SKILL_DIR/../../references/operators.md`（開場必讀）
- 185 條原始清單＝`SKILL_DIR/../../references/sources.md`（需要更多例子才讀）

## 鐵律（全程適用）

1. 一回合最多呈現 **2 個運算子**。
2. 每次跑 TRACKER 後，把它印出的 🧩 狀態行**原封不動**轉給使用者。
3. 候選必須貼著使用者的問題寫成**具體做法**（一個運算子 **4 個候選**；AskUserQuestion 自帶 Other，使用者看到共 5 個選項），寫定義的複述不算候選。
4. 所有選擇用 AskUserQuestion 呈現——工具內建「Other」，使用者永遠可以自由輸入。

## 步驟

### 0. 開場

- 使用者帶 `--resume` 或說要繼續上次 → `python3 TRACKER resume`，跳到上次進度。
- 否則進步驟 1。
- 讀 operators.md 進 context。
- 完成準則：🧩 狀態行已出現在對話裡（resume 時）。

### 1. 問題釐清（拷問式）

先弄懂問題，才准開跑運算子：

1. 分析使用者的問題陳述哪裡站不住：模糊詞、缺脈絡（誰？何時開始？多嚴重？試過什麼？為什麼現在要解？）、目標不明、或其實混了好幾個問題。
2. 針對站不住的地方提問（一輪最多 3 個問題；選項明確用 AskUserQuestion，開放的就直接問）。問到你能自己把問題完整說出來為止——可以多輪。
3. 用自己的話把問題**重述**成「**目標 − 現狀**」的一句話，用 AskUserQuestion 請使用者確認（確認／要修改）。
4. 使用者確認後：`python3 TRACKER start "<那句話>"`。

- 完成準則：使用者明確確認你重述的問題，session 已建立、狀態行已轉出。

### 2. 分診

- AskUserQuestion 單選：你卡的是哪種卡？
  沒點子（no-idea）／沒原因（no-cause）／沒決定（no-decision）／做不到（cant-do）／沒資訊（no-info）／都不是——人際、政治、危機類（not-applicable）。
- `python3 TRACKER triage <型>`，把印出的家族順序留著給步驟 3 用。
- **not-applicable** → 直說這不是運算子清單能解的題，指路（找利害關係人談、走危機 SOP、先收集資訊），`python3 TRACKER end`，流程結束。
- 完成準則：triage 已記錄。

### 3. 選家族

- 取 triage 建議順序的前 4 個家族，AskUserQuestion 多選（label＝家族字，description＝觸發問句），讓使用者挑 1–3 個。
- 完成準則：使用者選定家族。

### 4. 回合（核心循環）

選完家族就直接開跑——回合數與每回合招數依鐵律 1 固定，向使用者確認數量不是流程的一部分。

**第一個回合開始前**，先提示使用者一次（之後不重複）：
「每題都可以在 Other 自由輸入你的想法；如果選項都不好，在 Other 打『跳過』，這招就會被跳過。」

對選定家族依序處理。一個回合固定五步：

1. 取該家族 2 個未用運算子：`python3 TRACKER ask <id1> <id2>`。
2. 對照 operators.md 的定義與例子，替**使用者的問題**各生 4 個具體候選。
3. AskUserQuestion 一次兩題（每題＝一個運算子，`multiSelect: true`，選項＝4 個候選；工具自帶 Other，使用者看到共 5 個）。
4. 落帳：被選中或使用者 Other 輸入想法的 → 用 Edit 記進 worksheet「過程」段，`python3 TRACKER used <id>`；使用者在 Other 表示「跳過」「都不好」或該題沒有收穫的 → `python3 TRACKER skip <id>`。
5. **回合收尾（每回合必做）**：把落帳後 TRACKER 印出的最新一行 🧩 狀態，貼在給使用者的訊息裡（放在下一回合提問之前）。狀態行沒貼出，這回合就不算結束。

- 完成準則：選定家族的運算子出完，或使用者說「夠了／收斂」——且每個回合都以 🧩 狀態行收尾。

### 5. 收斂

- 彙整 worksheet 裡的候選，用 **ver-1 兩兩擂台**或 **ver-3 多想一層**幫使用者收成 1–3 個方案（AskUserQuestion 決選；記得 `TRACKER used ver-1`／`ver-3`）。
- 用 Edit 寫入 worksheet「收斂方案」與「下一步驗證」——下一步要具體到「做什麼實驗、查什麼數據，才知道方案可行」。
- 完成準則：使用者選定方案，或明說「沒有可行解」。

### 6. 加時賽（僅在無可行解時）

- `python3 TRACKER unused` → 依印出的順序取下一個未用家族，回到步驟 4。
- 完成準則：有解，或使用者喊停。

### 7. 收場

- `python3 TRACKER end`；貼出 worksheet 路徑；提醒使用者事後回填「結果」欄（方案最後有沒有用）。
- 完成準則：end 已跑、路徑已給。

## 落盤位置

**使用者當下資料夾**的 `solve-sessions/<slug>/worksheet.md`——tracker start 會建好骨架並印出絕對路徑；「過程」「收斂方案」「下一步驗證」由你隨流程用 Edit 填入。tracker 從 cwd 往上找 `solve-sessions/`，所以在專案子目錄跑也能接上同一場。每個資料夾同一時間只有一場 active session。
