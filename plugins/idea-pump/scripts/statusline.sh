#!/bin/bash
# UserPromptSubmit hook：從 cwd 往上找 solve-sessions/.active，
# 有 active session 才吐一行狀態，否則靜默退出。
dir="$PWD"
while :; do
  if [ -f "$dir/solve-sessions/.active" ]; then
    SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
    exec /usr/bin/env python3 "$SCRIPT_DIR/tracker.py" status
  fi
  [ "$dir" = "/" ] && exit 0
  dir="$(dirname "$dir")"
done
