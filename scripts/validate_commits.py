#!/usr/bin/env python3
import subprocess
import re
import sys
import logging
from pathlib import Path

# --- Logging Setup ---
log_path = Path(__file__).resolve().parent.parent / "logs" / "setup.log"
log_path.parent.mkdir(parents=True, exist_ok=True)
logging.basicConfig(
    filename=log_path,
    filemode='a',
    format='%(asctime)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# --- Constants ---
VALID_TYPES = {"feat", "fix", "docs", "chore"}
PROJECT_ROOT = Path(__file__).resolve().parent
SRC_DIR = PROJECT_ROOT / "src"
VALID_SCOPES = {p.stem for p in SRC_DIR.glob("*.py") if p.stem != "__init__"}
VALID_SCOPES.add("general")
COMMIT_RE = re.compile(r"^(feat|fix|docs|chore)\(([\w\-]+)\): .+")

def get_recent_commits():
    try:
        commits = subprocess.check_output(
            ["git", "log", "@{push}..HEAD", "--pretty=format:%s"],
            stderr=subprocess.DEVNULL
        ).decode("utf-8").splitlines()
        logging.info("Fetched unpushed commits.")
        return commits
    except subprocess.CalledProcessError:
        commits = subprocess.check_output(
            ["git", "log", "--pretty=format:%s"]
        ).decode("utf-8").splitlines()
        logging.warning("No upstream push found. Validating all commits.")
        return commits

def validate_commit(msg):
    match = COMMIT_RE.match(msg)
    if not match:
        return f"❌ Invalid format: {msg}"
    type_, scope = match.groups()
    if type_ not in VALID_TYPES:
        return f"❌ Invalid type '{type_}' in: {msg}"
    if scope not in VALID_SCOPES:
        return f"❌ Invalid scope '{scope}' in: {msg} (allowed: {', '.join(sorted(VALID_SCOPES))})"
    return None

def main():
    logging.info("Starting commit validation.")
    print("🔍 Validating commit messages...")
    failures = []

    for msg in get_recent_commits():
        error = validate_commit(msg)
        if error:
            logging.warning(error)
            failures.append(error)

    if failures:
        for f in failures:
            print(f)
        print("\n🚫 Push aborted. Fix commit messages and try again.")
        logging.warning("Commit validation failed.")
        sys.exit(1)
    else:
        print("✅ All commit messages are valid!")
        logging.info("All commit messages passed validation.")

if __name__ == "__main__":
    main()
