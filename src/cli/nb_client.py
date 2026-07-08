#!/usr/bin/env python3
"""nb_client.py — Nano Banana (Gemini image) client: API call, daily ledger, manual web-app fallback contract."""

import base64
import json
import os
import shutil
import urllib.error
import urllib.request
from datetime import date
from pathlib import Path

MODELS = {
    "nb": "gemini-2.5-flash-image",  # free tier workhorse
    "nb2": "gemini-3.1-flash-image",  # tighter free quota — hard cases only
    "nb-lite": "gemini-3.1-flash-lite-image",
}
SOFT_CAP = {"nb": 450, "nb2": 15, "nb-lite": 450}
_ROOT = Path(__file__).resolve().parents[2]
OUTPUT_DIR = _ROOT / "output"
LEDGER_PATH = OUTPUT_DIR / "nb-ledger.json"
INBOX = OUTPUT_DIR / "nb-inbox"  # guides + prompts waiting for a manual web run
OUTBOX = OUTPUT_DIR / "nb-outbox"  # NB results (API or manual) — postproc reads here
_ENDPOINT = "https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={key}"


def _api_key():
    key = os.environ.get("GEMINI_API_KEY")
    if not key:
        raise SystemExit("GEMINI_API_KEY not set — export it or use --manual (web-app fallback).")
    return key


def _ledger_load():
    if LEDGER_PATH.exists():
        return json.loads(LEDGER_PATH.read_text())
    return {}


def _ledger_bump(alias):
    ledger = _ledger_load()
    day = ledger.setdefault(str(date.today()), {})
    day[alias] = day.get(alias, 0) + 1
    LEDGER_PATH.parent.mkdir(parents=True, exist_ok=True)
    LEDGER_PATH.write_text(json.dumps(ledger, indent=2))
    count = day[alias]
    if count > SOFT_CAP[alias]:
        print(f"[WARN] {alias}: {count} calls today — past soft cap {SOFT_CAP[alias]}.")
    return count


def _image_part(path):
    data = Path(path).read_bytes()
    encoded = base64.b64encode(data).decode()
    return {"inline_data": {"mime_type": "image/png", "data": encoded}}


def _request(alias, parts):
    key = _api_key()
    url = _ENDPOINT.format(model=MODELS[alias], key=key)
    body = {"contents": [{"parts": parts}]}
    payload = json.dumps(body).encode()
    req = urllib.request.Request(url, payload, {"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=180) as resp:
            return json.load(resp)
    except urllib.error.HTTPError as err:
        detail = err.read().decode()[:300]
        if err.code == 429:
            raise RuntimeError(f"{alias}: free quota do dia esgotada (429) — use --manual ou aguarde o reset (meia-noite Pacific). {detail}") from err
        raise RuntimeError(f"{alias}: HTTP {err.code} — {detail}") from err


def _extract_image(alias, response):
    candidates = response.get("candidates", [])
    image_bytes = None
    parts = candidates[0]["content"]["parts"] if candidates else []
    for part in parts:
        inline = part.get("inlineData") or part.get("inline_data")
        if inline:
            image_bytes = base64.b64decode(inline["data"])
    if image_bytes is None:
        raise RuntimeError(f"{alias}: no image in response — {json.dumps(response)[:300]}")
    return image_bytes


def generate(prompt, out_path, guide_path=None, alias="nb"):
    """One NB call; saves the returned PNG to out_path and bumps the ledger."""
    parts = [{"text": prompt}]
    if guide_path:
        parts.append(_image_part(guide_path))
    response = _request(alias, parts)
    image_bytes = _extract_image(alias, response)
    out = Path(out_path)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_bytes(image_bytes)
    count = _ledger_bump(alias)
    print(f"[OK] {out}  ({alias} #{count} today)")
    return out


def drop_manual(stem, prompt, guide_path):
    """Manual fallback: stage guide+prompt in the inbox; user runs the web app and saves to the outbox."""
    INBOX.mkdir(parents=True, exist_ok=True)
    OUTBOX.mkdir(parents=True, exist_ok=True)
    guide_dst = INBOX / f"{stem}_guide.png"
    shutil.copyfile(guide_path, guide_dst)
    prompt_dst = INBOX / f"{stem}_prompt.txt"
    prompt_dst.write_text(prompt, encoding="utf-8")
    print(f"[MANUAL] staged: {guide_dst}\n         prompt: {prompt_dst}")
    expected = OUTBOX / f"{stem}.png"
    print(f"         → web app: attach guide, paste prompt, save result as {expected}")
    return guide_dst


def collect_manual(stem):
    """NB results for a stem already dropped in the outbox (API or manual)."""
    return sorted(OUTBOX.glob(f"{stem}*.png"))
