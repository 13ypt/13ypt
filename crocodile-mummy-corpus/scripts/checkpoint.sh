#!/usr/bin/env bash
# Merge all agent records into the master CSVs, then commit and push (persistence checkpoint).
set -euo pipefail
cd "$(dirname "$0")/.."
python3 scripts/merge.py
cd ..
git add crocodile-mummy-corpus
git commit -q -m "Corpus checkpoint: ${1:-merge agent records into master CSVs}

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>
Claude-Session: https://claude.ai/code/session_01W832qLo4XTQrAoftQ2hxrD" || echo "nothing to commit"
for i in 1 2 3 4; do git push -q -u origin claude/sharp-turing-iwlzmt && break || sleep $((2**i)); done
git log --oneline -1
