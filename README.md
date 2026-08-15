# thinking-operators

> 繁體中文說明：[README.zh-TW.md](./README.zh-TW.md)

A question-and-answer problem-solving engine for Claude Code.
When you are stuck on a problem, it walks you through a solving flow:
clarify the problem, pick fitting thinking moves from 55 "thinking operators"
(12 families: add, subtract, multiply, divide, reverse, substitute, morph, time,
reframe, resources, diverge, verify), generate concrete ideas for you to choose from,
then converge on a plan. A tracker script records the state of every operator.
Each time you send a message, a hook prints one 🧩 status line — you and the AI never lose track.

The 55 operators are merged from 8 classic checklists:

- Osborn Checklist
- SCAMPER
- The Twelve Methods (和田十二法 / 創意十二訣)
- TRIZ 40 inventive principles
- SIT — Systematic Inventive Thinking ("Inside the Box")
- Pólya's heuristics from "How to Solve It"
- Dokushozaru's "Problem Solving Compendium" + "Idea Compendium" (読書猿)
- General mental models (Munger, Farnam Street, etc.)

## Install

```bash
claude plugin marketplace add a7512cs/thinking-operators
claude plugin install thinking-operators@thinking-operators
```

No folder setup needed.

To ship an update as a developer: commit → push →
`claude plugin marketplace update thinking-operators` → uninstall/install.

## Usage

Open Claude Code in the folder where you want to solve a problem:

```
/thinking-operators:solve            # typing /solve fuzzy-matches it
/thinking-operators:solve --resume   # continue the unfinished session in this folder
```

Manual trigger only (`disable-model-invocation: true`) — it never fires on its own.

## Where your data goes

The first session creates `./solve-sessions/` in your current folder.
Each session gets a sub-folder with `worksheet.md` and `state.json`.
Scripts search upward from the current directory for `solve-sessions/`
(like git finds `.git`), so sub-directories work too.
One active session per folder.

Committing `solve-sessions/` to git is your choice (`.active` is auto-gitignored).
Note: worksheets contain your problem text — be careful in public repos.

## Layout

```
.claude-plugin/marketplace.json      marketplace definition
plugins/thinking-operators/
├── .claude-plugin/plugin.json
├── skills/solve/SKILL.md            the Q&A flow
├── references/operators.json        55 operators, machine-readable (single source of truth)
├── references/operators.md          55 operators, human-readable
├── references/sources.md            all 185 original items from 8 classic checklists
├── scripts/tracker.py               session state tracking
├── scripts/statusline.sh            UserPromptSubmit hook: prints status only when a session is active
└── hooks/hooks.json
CONTEXT.md                           glossary
docs/adr/                            decision records
```

## Limits

- The skill content (operators, prompts, status line) is written in Traditional Chinese.
  The conversation itself follows your language.
- macOS / Linux (the hook is a bash script). Windows untested.
- Fill in the worksheet's "result" section afterwards — it builds your own record of
  which operators actually helped.
