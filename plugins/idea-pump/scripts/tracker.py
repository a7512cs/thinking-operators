#!/usr/bin/env python3
"""解題 session 追蹤器：記錄 55 個思考運算子的使用狀態。

資料夾：從當下目錄往上找 `solve-sessions/`（跟 git 找 .git 同一招）；
`start` 找不到時會在當下目錄建立。每個資料夾同一時間只允許一場 active session。

指令：
  start "<問題一句話>"     開新 session（該資料夾已有 active 會拒絕）
  triage <類型>            記錄分診結果，印出建議家族順序
  ask <id...>              標記為「詢問中」
  used <id...>             標記為「已用」
  skip <id...>             標記為「跳過」
  status                   吐一行目前狀態
  unused                   列出還沒用的運算子（依分診家族優先序）
  end                      結束 active session
  resume                   撈回最近一場未結束的 session
  list                     列出這個資料夾的所有 session
"""
import json
import re
import sys
import unicodedata
from datetime import datetime
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
OPERATORS_FILE = SCRIPT_DIR.parent / "references" / "operators.json"
DATA_DIR_NAME = "solve-sessions"

STATES = {"unused": "未用", "asking": "詢問中", "used": "已用", "skipped": "跳過"}

WORKSHEET_TEMPLATE = """# 解題單：{problem}

- 日期：{date}
- 分診：（待填）

## 問題一句話（目標 − 現狀）

{problem}

## 過程（運算子 → 候選 → 選擇）

## 收斂方案

## 下一步驗證

## 結果回填（事後）

"""


def die(msg):
    print(msg)
    sys.exit(1)


def load_catalog():
    with open(OPERATORS_FILE, encoding="utf-8") as f:
        return json.load(f)


def find_data_dir():
    """從 cwd 往上找 solve-sessions/，找不到回 None。"""
    d = Path.cwd()
    while True:
        cand = d / DATA_DIR_NAME
        if cand.is_dir():
            return cand
        if d == d.parent:
            return None
        d = d.parent


def require_data_dir():
    data = find_data_dir()
    if data is None:
        die(f"當下目錄（含上層）沒有 {DATA_DIR_NAME}/。用 start \"<問題>\" 開第一場。")
    return data


def active_file(data):
    return data / ".active"


def load_active(data):
    af = active_file(data)
    if not af.exists():
        die("這個資料夾沒有 active session。用 start \"<問題>\" 開新的，或 resume 撈回舊的。")
    slug = af.read_text(encoding="utf-8").strip()
    state_file = data / slug / "state.json"
    if not state_file.exists():
        die(f"active 指向的 session 不存在：{slug}（.active 已失效，請刪掉 {af} 後 resume）")
    with open(state_file, encoding="utf-8") as f:
        return slug, json.load(f)


def save_state(data, slug, state):
    with open(data / slug / "state.json", "w", encoding="utf-8") as f:
        json.dump(state, f, ensure_ascii=False, indent=2)


def make_slug(problem):
    cleaned = []
    for ch in problem:
        if ch.isalnum() or unicodedata.category(ch).startswith("Lo"):
            cleaned.append(ch)
        else:
            cleaned.append("-")
    slug = re.sub(r"-+", "-", "".join(cleaned)).strip("-")[:20] or "untitled"
    return f"{datetime.now():%Y-%m-%d}-{slug}"


def cmd_start(problem):
    data = find_data_dir()
    if data is None:
        data = Path.cwd() / DATA_DIR_NAME
        data.mkdir()
        # .active 是暫存檔，自帶 gitignore 讓使用者零設定
        (data / ".gitignore").write_text(".active\n", encoding="utf-8")
    if active_file(data).exists():
        die(
            f"這個資料夾已有 active session（{active_file(data).read_text(encoding='utf-8').strip()}）。"
            "先 end 它，或用 resume 繼續。"
        )
    catalog = load_catalog()
    slug = make_slug(problem)
    if (data / slug).exists():
        slug = f"{slug}-{datetime.now():%H%M}"
    (data / slug).mkdir()
    state = {
        "problem": problem,
        "slug": slug,
        "created": datetime.now().isoformat(timespec="seconds"),
        "triage": None,
        "ops": {op["id"]: "unused" for op in catalog["operators"]},
        "ended": False,
    }
    save_state(data, slug, state)
    worksheet = data / slug / "worksheet.md"
    worksheet.write_text(
        WORKSHEET_TEMPLATE.format(problem=problem, date=f"{datetime.now():%Y-%m-%d}"),
        encoding="utf-8",
    )
    active_file(data).write_text(slug, encoding="utf-8")
    print(f"session 開始：{slug}")
    print(f"worksheet：{worksheet.resolve()}")
    print(status_line(slug, state, catalog))


def cmd_triage(kind):
    catalog = load_catalog()
    if kind not in catalog["triage"]:
        die(f"分診類型要是其中之一：{'、'.join(catalog['triage'])}")
    data = require_data_dir()
    slug, state = load_active(data)
    state["triage"] = kind
    save_state(data, slug, state)
    t = catalog["triage"][kind]
    fam_names = {f["id"]: f"{f['zh']}（{f['question']}）" for f in catalog["families"]}
    print(f"分診＝{t['zh']}。建議家族順序：")
    if not t["families"]:
        print("（不適用——這不是運算子清單能解的題，明講並指路後 end。）")
    for fid in t["families"]:
        print(f"  {fam_names[fid]}")


def mark(ids, new_state):
    catalog = load_catalog()
    data = require_data_dir()
    slug, state = load_active(data)
    bad = [i for i in ids if i not in state["ops"]]
    if bad:
        die(f"不認識的運算子 id：{'、'.join(bad)}（見 operators.json）")
    for i in ids:
        state["ops"][i] = new_state
    save_state(data, slug, state)
    print(status_line(slug, state, catalog))


def status_line(slug, state, catalog):
    counts = {k: 0 for k in STATES}
    for v in state["ops"].values():
        counts[v] += 1
    total = len(state["ops"])
    fam_ops = {}
    for op in catalog["operators"]:
        fam_ops.setdefault(op["family"], []).append(op["id"])
    frags = []
    for fam in catalog["families"]:
        ids = fam_ops[fam["id"]]
        touched = sum(1 for i in ids if state["ops"][i] != "unused")
        if touched:
            frags.append(f"{fam['zh']}{touched}/{len(ids)}")
    fam_part = " ".join(frags) if frags else "尚未動用任何運算子"
    return (
        f"🧩 {slug}｜已用{counts['used']} 詢問中{counts['asking']} "
        f"跳過{counts['skipped']} 剩{counts['unused']}/{total}｜{fam_part}"
    )


def cmd_status():
    data = require_data_dir()
    slug, state = load_active(data)
    print(status_line(slug, state, load_catalog()))


def cmd_unused():
    catalog = load_catalog()
    data = require_data_dir()
    slug, state = load_active(data)
    ops_by_id = {op["id"]: op for op in catalog["operators"]}
    fam_order = [f["id"] for f in catalog["families"]]
    if state["triage"] and catalog["triage"][state["triage"]]["families"]:
        pref = catalog["triage"][state["triage"]]["families"]
        fam_order = pref + [f for f in fam_order if f not in pref]
    fam_names = {f["id"]: f["zh"] for f in catalog["families"]}
    any_left = False
    for fid in fam_order:
        left = [
            ops_by_id[i]
            for i in state["ops"]
            if ops_by_id[i]["family"] == fid and state["ops"][i] == "unused"
        ]
        if left:
            any_left = True
            names = "、".join(f"{o['id']} {o['name']}" for o in left)
            print(f"{fam_names[fid]}：{names}")
    if not any_left:
        print("55 招全部用過了。")


def cmd_end():
    catalog = load_catalog()
    data = require_data_dir()
    slug, state = load_active(data)
    state["ended"] = True
    save_state(data, slug, state)
    active_file(data).unlink()
    print(f"session 結束：{slug}")
    print(status_line(slug, state, catalog))
    print(f"worksheet：{(data / slug / 'worksheet.md').resolve()}（記得事後回填「結果」）")


def cmd_resume():
    data = require_data_dir()
    if active_file(data).exists():
        die(f"這個資料夾已有 active session：{active_file(data).read_text(encoding='utf-8').strip()}")
    candidates = sorted(
        (d for d in data.iterdir() if (d / "state.json").exists()),
        key=lambda d: d.name,
        reverse=True,
    )
    for d in candidates:
        with open(d / "state.json", encoding="utf-8") as f:
            state = json.load(f)
        if not state["ended"]:
            active_file(data).write_text(d.name, encoding="utf-8")
            print(f"resume：{d.name}（問題：{state['problem']}）")
            print(status_line(d.name, state, load_catalog()))
            return
    die("這個資料夾沒有未結束的 session 可以 resume。")


def cmd_list():
    data = require_data_dir()
    found = False
    for d in sorted(data.iterdir()):
        state_file = d / "state.json"
        if not state_file.exists():
            continue
        with open(state_file, encoding="utf-8") as f:
            state = json.load(f)
        found = True
        flag = "已結束" if state["ended"] else "進行中"
        print(f"{d.name}｜{flag}｜{state['problem']}")
    if not found:
        print("這個資料夾還沒有任何 session。")


def main():
    args = sys.argv[1:]
    if not args:
        die(__doc__.strip())
    cmd, rest = args[0], args[1:]
    if cmd == "start":
        if not rest:
            die('用法：start "<問題一句話>"')
        cmd_start(" ".join(rest))
    elif cmd == "triage":
        if len(rest) != 1:
            die("用法：triage <no-idea|no-cause|no-decision|cant-do|no-info|not-applicable>")
        cmd_triage(rest[0])
    elif cmd in ("ask", "used", "skip"):
        if not rest:
            die(f"用法：{cmd} <運算子id...>")
        mark(rest, {"ask": "asking", "used": "used", "skip": "skipped"}[cmd])
    elif cmd == "status":
        cmd_status()
    elif cmd == "unused":
        cmd_unused()
    elif cmd == "end":
        cmd_end()
    elif cmd == "resume":
        cmd_resume()
    elif cmd == "list":
        cmd_list()
    else:
        die(f"不認識的指令：{cmd}\n\n{__doc__.strip()}")


if __name__ == "__main__":
    main()
