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
        return
    for index in range(count):
        try:
            child = obj.getChildAtIndex(index)
        except Exception:
            continue
        if child is not None:
            yield child

def walk(root, limit=12000):
    stack = [root]
    seen = 0
    while stack and seen < limit:
        obj = stack.pop()
        seen += 1
        yield obj
        try:
            kids = list(children(obj))
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

focusable = []
documents = []
matches = []

for app in apps:
    for obj in walk(app):
        try:
            name = obj.name or ""
            role = obj.getRoleName()
            states = obj.getState()
            is_focusable = states.contains(pyatspi.STATE_FOCUSABLE)
            is_showing = states.contains(pyatspi.STATE_SHOWING)
            is_visible = states.contains(pyatspi.STATE_VISIBLE)
        except Exception:
            continue

        if role == "document web":
            documents.append(obj)

        if is_focusable and is_showing and is_visible:
            focusable.append((obj, role, name))

        if needle and needle in name.lower():
            matches.append((obj, role, name, is_focusable, is_showing, is_visible))

candidate = None
candidate_meta = None

for obj, role, name, is_focusable, is_showing, is_visible in matches:
    if is_focusable and is_showing and is_visible:
        candidate = obj
        candidate_meta = (role, name, "TARGET_MATCH")
        break

if candidate is None and documents:
    document = documents[0]
    for obj in walk(document, limit=6000):
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

if candidate is None and focusable:
    obj, role, name = focusable[0]
    candidate = obj
    candidate_meta = (role, name, "APP_FIRST_FOCUSABLE")

if candidate is None:
    emit({
        "status": "NO_FOCUSABLE_CONTENT",
        "needle": needle,
        "document_count": len(documents),
        "focusable_count": len(focusable),
        "matches": [{"role": r, "name": n, "focusable": f, "showing": s, "visible": v} for _, r, n, f, s, v in matches[:20]],
    })
    raise SystemExit(3)

role, name, source = candidate_meta
try:
    result = bool(candidate.queryComponent().grabFocus())
except Exception as exc:
    emit({"status": "GRAB_FOCUS_ERROR", "needle": needle, "role": role, "name": name, "source": source, "error": repr(exc)})
    raise SystemExit(4)

time.sleep(0.75)
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
    "document_count": len(documents),
    "focusable_count": len(focusable),
    "match_count": len(matches),
})
