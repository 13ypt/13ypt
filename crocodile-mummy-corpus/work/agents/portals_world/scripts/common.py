"""Shared helpers for the portals_world API sweep.

- polite HTTP session (>= 1 s between requests by default)
- raw JSON saving (small responses only)
- search_log appends through the project validator rec.py
"""
import json
import os
import subprocess
import sys
import time

import requests

AGENT = "portals_world"
HERE = os.path.dirname(os.path.abspath(__file__))
AGENT_DIR = os.path.dirname(HERE)
RAW = os.path.join(AGENT_DIR, "raw")
PROJECT = os.path.dirname(os.path.dirname(os.path.dirname(AGENT_DIR)))  # /home/user/13ypt
REC = os.path.join(PROJECT, "crocodile-mummy-corpus", "scripts", "rec.py")

UA = "Mozilla/5.0 (research survey of museum crocodile mummies; contact via Claude Code agent)"

_session = requests.Session()
_session.headers.update({"User-Agent": UA})
_last = [0.0]


def get(url, params=None, pause=1.1, headers=None, timeout=60, **kw):
    wait = pause - (time.time() - _last[0])
    if wait > 0:
        time.sleep(wait)
    try:
        r = _session.get(url, params=params, headers=headers, timeout=timeout, **kw)
    except Exception as exc:  # network error
        _last[0] = time.time()
        return None, str(exc)
    _last[0] = time.time()
    return r, None


def save_raw(name, data):
    os.makedirs(RAW, exist_ok=True)
    path = os.path.join(RAW, name)
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(data, fh, ensure_ascii=False, indent=1)
    return path


def rec(kind, records):
    if isinstance(records, dict):
        records = [records]
    payload = "\n".join(json.dumps(r, ensure_ascii=False) for r in records) + "\n"
    p = subprocess.run([sys.executable, REC, AGENT, kind], input=payload, text=True,
                       capture_output=True, cwd=PROJECT)
    sys.stdout.write(p.stdout)
    sys.stderr.write(p.stderr)
    return p.returncode


def log(country, language, db, query, result, institution="", notes=""):
    return rec("search_log", {
        "country": country, "language": language, "database_or_search_engine": db,
        "query": query, "institution_checked": institution or "UNKNOWN",
        "result": result, "notes": notes or "UNKNOWN",
    })
