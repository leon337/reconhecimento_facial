#!/usr/bin/env python3
import json
import os
import sys
import time

import pyatspi

needle = (sys.argv[1] if len(sys.argv) > 1 else "").strip().lower()
evidence = os.environ.get("EVIDENCE", "")
log_path = os.path.join(evidence, "N3-atspi-focus-probes.log") if evidence else None

def emit(payload):
    line = json.dumps(payload, ensure_ascii=False)
    print(line, flush=True)
    if log_path:
        with open(log_path, "a", encoding="utf-8") as fh:
            fh.write(line + "\n")

def children(obj):
    try:
        count = obj.childCount
    except Exception:
        return []
    out = []
    for index in range(count):
        try:
            child = obj.getChildAtIndex(index)
        except Exception:
            continue
        if child is not None:
            out.append(child)
    return out

def walk(root, limit):
    stack = [root]
    seen = 0
    while stack and seen < limit:
        obj = stack.pop()
        seen += 1
        yield obj, seen
        try:
            kids = children(obj)
        except Exception:
            kids = []
        stack.extend(reversed(kids))

desktop = pyatspi.Registry.getDesktop(0)
apps = []
for app in children(desktop):
    try:
        name = app.name or ""
    except Exception:
        name = ""
    if "chrome" in name.lower() or "chromium" in name.lower():
        apps.append(app)

if not apps:
    emit({"status": "NO_CHROME_APPLICATION", "needle": needle})
    raise SystemExit(2)

candidate = None
candidate_meta = None
first_document = None
scanned = 0

for app in apps:
    for obj, count in walk(app, limit=3000):
        scanned += 1
        try:
            name = obj.name or ""
            role = obj.getRoleName()
            states = obj.getState()
            is_focusable = states.contains(pyatspi.STATE_FOCUSABLE)
            is_showing = states.contains(pyatspi.STATE_SHOWING)
            is_visible = states.contains(pyatspi.STATE_VISIBLE)
        except Exception:
            continue

        if first_document is None and role == "document web":
            first_document = obj

        if needle and needle in name.lower() and is_focusable and is_showing and is_visible:
            candidate = obj
            candidate_meta = (role, name, "TARGET_MATCH")
            break
    if candidate is not None:
        break

if candidate is None and first_document is not None:
    for obj, count in walk(first_document, limit=800):
        scanned += 1
        try:
            name = obj.name or ""
            role = obj.getRoleName()
            states = obj.getState()
            if states.contains(pyatspi.STATE_FOCUSABLE) and states.contains(pyatspi.STATE_SHOWING) and states.contains(pyatspi.STATE_VISIBLE):
                candidate = obj
                candidate_meta = (role, name, "DOCUMENT_FIRST_FOCUSABLE")
                break
        except Exception:
            continue

if candidate is None:
    emit({
        "status": "NO_FOCUSABLE_CONTENT",
        "needle": needle,
        "scanned": scanned,
        "document_found": first_document is not None,
    })
    raise SystemExit(3)

role, name, source = candidate_meta
try:
    result = bool(candidate.queryComponent().grabFocus())
except Exception as exc:
    emit({
        "status": "GRAB_FOCUS_ERROR",
        "needle": needle,
        "role": role,
        "name": name,
        "source": source,
        "scanned": scanned,
        "error": repr(exc),
    })
    raise SystemExit(4)

time.sleep(0.6)
try:
    focused = candidate.getState().contains(pyatspi.STATE_FOCUSED)
except Exception:
    focused = False

emit({
    "status": "FOCUS_REQUESTED",
    "needle": needle,
    "role": role,
    "name": name,
    "source": source,
    "grab_focus_result": result,
    "focused_after": focused,
    "scanned": scanned,
})
