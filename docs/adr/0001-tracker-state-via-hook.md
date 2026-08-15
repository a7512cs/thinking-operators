# 0001 — 運算子狀態用全域 UserPromptSubmit hook 回報

日期：2026-08-15
狀態：已採用

## 背景

solve 流程橫跨多輪問答，需要「哪些運算子已用／詢問中／未用」的狀態在整場 session 不亂。
需求方明確要求「一定不會亂」——不能依賴 AI 記得每輪呼叫腳本。

## 決策

plugin 自帶 `hooks/hooks.json`（UserPromptSubmit hook）。使用者每送出一句話，
`statusline.sh` 從 cwd 往上找 `solve-sessions/.active`（跟 git 找 `.git` 同一邏輯）：
找到就跑 `tracker.py status` 把一行 🧮 狀態注入 context；找不到就靜默 exit 0。
狀態的唯一事實來源是 `state.json`（腳本寫入），AI 只是搬運工。

## 替代方案

- **SKILL.md 紀律**（要求 AI 每輪呼叫 tracker）：簡單，但 AI 漏跑一次狀態就漂移，不符「一定不會亂」。
- **純 prose、零狀態**：狀態活在對話上下文與 worksheet 裡，
  沒有 cwd 問題，但 55 招的已用/未用計數靠 AI 重讀重算會漂——同樣不符需求。
- **不追蹤**：加時賽（找未用招）與「剩多少招」的回報都做不到。

## 後果

- 這個 hook 裝了 plugin 之後**在所有專案的每句話**都會跑——所以 statusline.sh 必須快、
  且找不到 active session 時零輸出零干擾（純目錄向上檢查就退出）。
- session 狀態壞掉時，修該資料夾 `solve-sessions/` 裡的 `state.json`／刪 `.active` 即可，不影響其他專案。
