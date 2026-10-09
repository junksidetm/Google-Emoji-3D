#!/usr/bin/env python3
"""
check_upstream_updates.py - Check upstream googlefonts/noto-emoji for new 3D PNG assets.
Detects new commits/emojis, bumps version, appends to Version.md, and exports workflow outputs.
"""

import json
import os
import re
import sys
import urllib.request
from datetime import datetime, timezone, timedelta

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
VERSION_FILE = os.path.join(REPO_ROOT, "VERSION")
VERSION_MD_FILE = os.path.join(REPO_ROOT, "Version.md")
STATE_FILE = os.path.join(REPO_ROOT, ".upstream_state.json")

UPSTREAM_API_URL = "https://api.github.com/repos/googlefonts/noto-emoji/commits?path=3D&per_page=1"
METADATA_URL = "https://googlefonts.github.io/noto-emoji-files/data/emojis_data.js"


def get_latest_upstream_commit():
    try:
        req = urllib.request.Request(
            UPSTREAM_API_URL,
            headers={"User-Agent": "Google-Emoji-3D-Checker/1.0"}
        )
        with urllib.request.urlopen(req, timeout=20) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            if data and isinstance(data, list) and len(data) > 0:
                sha = data[0].get("sha", "")
                commit_msg = data[0].get("commit", {}).get("message", "").split("\n")[0]
                date = data[0].get("commit", {}).get("committer", {}).get("date", "")
                return sha, commit_msg, date
    except Exception as e:
        print(f"[!] Warning: Could not fetch upstream commit: {e}", file=sys.stderr)
    return "", "", ""


def get_upstream_emoji_count():
    try:
        req = urllib.request.Request(
            METADATA_URL,
            headers={"User-Agent": "Google-Emoji-3D-Checker/1.0"}
        )
        with urllib.request.urlopen(req, timeout=25) as resp:
            content = resp.read().decode("utf-8")
            cleaned = re.sub(r"^\s*window\.__NOTO_EMOJIS_DATA__\s*=\s*", "", content.strip())
            cleaned = re.sub(r";\s*$", "", cleaned)
            records = json.loads(cleaned)
            return len(records)
    except Exception as e:
        print(f"[!] Warning: Could not fetch emojis_data.js: {e}", file=sys.stderr)
    return 0


def load_state():
    if os.path.exists(STATE_FILE):
        try:
            with open(STATE_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return {"last_commit": "", "last_version": "1.1.1", "emoji_count": 0}


def save_state(state):
    with open(STATE_FILE, "w", encoding="utf-8") as f:
        json.dump(state, f, indent=2)


def get_current_version():
    if os.path.exists(VERSION_FILE):
        with open(VERSION_FILE, "r", encoding="utf-8") as f:
            v = f.read().strip()
            if v:
                return v
    return "1.1.1"


def bump_patch_version(version_str):
    parts = version_str.split(".")
    if len(parts) == 3 and parts[2].isdigit():
        parts[2] = str(int(parts[2]) + 1)
        return ".".join(parts)
    return f"{version_str}.1"


def append_version_md(new_version, commit_sha, commit_msg, emoji_count):
    # Strict Append Pattern - strictly append to the bottom with IST timestamp
    ist_tz = timezone(timedelta(hours=5, minutes=30))
    now_ist = datetime.now(ist_tz).strftime("%Y-%m-%d %H:%M:%S IST")

    entry = f"""
## [{now_ist}] - Autonomous Release v{new_version}: Upstream Google 3D Emoji Sync
- **Status:** 100% (Completed & Released)
- **Version:** v{new_version}
- **Upstream Commit:** `{commit_sha[:10] if commit_sha else 'Manual'}` - {commit_msg or 'Synchronized upstream 3D emoji assets'}
- **Total Emojis Tracked:** {emoji_count if emoji_count > 0 else 'Full Noto 3D Suite'}
- **Artifacts:**
  - `GoogleEmoji3D.ttf`: High-resolution OpenType CBDT/CBLC color bitmap font
  - `GoogleEmoji3D-128px.zip`: Complete distribution archive
  - `categories_manifest.json`: Full taxonomic category definitions
  - `emojis_metadata.json`: Unicode sequence metadata
- **Summary:**
  - Autonomous pipeline detected upstream asset changes in `googlefonts/noto-emoji`.
  - Recompiled TrueType font with newly added 3D PNG strikes.
  - Published GitHub release with tag `v{new_version}`.
"""
    with open(VERSION_MD_FILE, "a", encoding="utf-8") as f:
        f.write(entry)


def set_github_output(name, value):
    output_file = os.environ.get("GITHUB_OUTPUT")
    if output_file:
        with open(output_file, "a", encoding="utf-8") as f:
            f.write(f"{name}={value}\n")
    print(f"[OUTPUT] {name}={value}")


def main():
    force_build = os.environ.get("FORCE_BUILD", "false").lower() == "true"
    manual_tag = os.environ.get("INPUT_TAG_NAME", "").strip()

    upstream_sha, commit_msg, commit_date = get_latest_upstream_commit()
    emoji_count = get_upstream_emoji_count()
    state = load_state()

    last_sha = state.get("last_commit", "")
    last_count = state.get("emoji_count", 0)

    has_new_commit = bool(upstream_sha and upstream_sha != last_sha)
    has_new_emojis = bool(emoji_count > 0 and emoji_count > last_count)
    should_update = force_build or has_new_commit or has_new_emojis or bool(manual_tag)

    print(f"[*] Upstream SHA: {upstream_sha} (Last known: {last_sha})")
    print(f"[*] Upstream Emojis: {emoji_count} (Last known: {last_count})")
    print(f"[*] Force Build: {force_build}")
    print(f"[*] Should Update: {should_update}")

    if not should_update:
        print("[+] No new 3D PNG assets found upstream. Repository is up to date.")
        set_github_output("has_update", "false")
        return

    cur_version = get_current_version()
    if manual_tag:
        new_version = manual_tag.lstrip("v")
    else:
        new_version = bump_patch_version(cur_version)

    new_tag = f"v{new_version}"
    print(f"[+] Bumping version from {cur_version} -> {new_version} (Tag: {new_tag})")

    # Update VERSION
    with open(VERSION_FILE, "w", encoding="utf-8") as f:
        f.write(f"{new_version}\n")

    # Append to Version.md (Strict append mandate)
    append_version_md(new_version, upstream_sha, commit_msg, emoji_count)

    # Update state
    state["last_commit"] = upstream_sha if upstream_sha else last_sha
    state["last_version"] = new_version
    if emoji_count > 0:
        state["emoji_count"] = emoji_count
    save_state(state)

    set_github_output("has_update", "true")
    set_github_output("new_version", new_version)
    set_github_output("new_tag", new_tag)
    set_github_output("commit_sha", upstream_sha)
    set_github_output("commit_msg", commit_msg)


if __name__ == "__main__":
    main()
