#!/usr/bin/env python3
import subprocess
import re
import logging
from pathlib import Path
import tomllib
import sys

# --- Logging Setup ---
log_path = Path(__file__).resolve().parent.parent / "logs" / "setup.log"
log_path.parent.mkdir(parents=True, exist_ok=True)
logging.basicConfig(
    filename=log_path,
    filemode='a',
    format='%(asctime)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

SECTION_MAP = {
    "feat": "### Added",
    "fix": "### Fixed",
    "docs": "### Changed",
    "chore": "### Changed"
}

def get_current_version():
    try:
        root_dir = Path(__file__).resolve().parent.parent
        pyproject_path = root_dir / "pyproject.toml"

        with open(pyproject_path, "rb") as f:
            data = tomllib.load(f)

        project_name = data["project"]["name"]
        version_file = root_dir / "src" / project_name / "__version__.py"

        with open(version_file, "r") as f:
            for line in f:
                if line.startswith("__version__"):
                    version = line.split("=")[1].strip().strip('"\'')
                    logging.info(f"Detected current version {version} from {version_file}")
                    return version

        raise ValueError(f"__version__ not found in {version_file}")

    except Exception as e:
        logging.error(f"Failed to retrieve version: {e}")
        raise

def get_recent_commits():
    result = subprocess.run(["git", "log", "@{u}..HEAD", "--pretty=format:%s"], capture_output=True, text=True)
    if result.returncode == 0:
        logging.info("Retrieved recent commits for changelog.")
        return result.stdout.strip().split("\n")
    else:
        logging.warning("No recent commits found for changelog.")
        return []

def parse_commit(msg):
    match = re.match(r"^(feat|fix|docs|chore)\(([\w\-]+)\): (.+)", msg)
    return match.groups() if match else (None, None, None)

def ensure_changelog_sections(changelog_lines, version):
    version_header = f"## [{version}]"
    if version_header not in ''.join(changelog_lines):
        changelog_lines.insert(0, "\n")
        changelog_lines.insert(0, f"{version_header}\n")
        for section in reversed(SECTION_MAP.values()):
            changelog_lines.insert(1, f"{section}\n\n")
        logging.info(f"Inserted new section headers for version {version}.")
    return changelog_lines

def collect_existing_entries(changelog_lines, version):
    collecting = False
    current_section = None
    existing = {section: set() for section in SECTION_MAP.values()}
    version_header = f"## [{version}]"

    for line in changelog_lines:
        if line.strip() == version_header:
            collecting = True
            continue
        if collecting:
            if line.startswith("## [") and line.strip() != version_header:
                break
            if line.strip() in existing:
                current_section = line.strip()
                continue
            if current_section and line.strip().startswith("- "):
                existing[current_section].add(line.strip())

    return existing

def update_changelog(version, commits):
    root_dir = Path(__file__).resolve().parent.parent
    changelog_path = root_dir / "CHANGELOG.md"
    changelog_lines = changelog_path.read_text().splitlines(keepends=True) if changelog_path.exists() else []

    changelog_lines = ensure_changelog_sections(changelog_lines, version)
    existing = collect_existing_entries(changelog_lines, version)
    added = {section: [] for section in SECTION_MAP.values()}

    for msg in commits:
        type_, scope, description = parse_commit(msg)
        if not type_:
            continue
        section = SECTION_MAP[type_]
        entry = f"- {type_}({scope}): {description}"
        if entry not in existing[section]:
            added[section].append(entry + "\n")

    if all(len(v) == 0 for v in added.values()):
        logging.info("No new changelog entries found.")
        print("[i] No new entries to add to changelog.")
        return

    # Inject new entries
    i = 0
    while i < len(changelog_lines):
        line = changelog_lines[i]
        if line.strip() == f"## [{version}]":
            i += 1
            while i < len(changelog_lines) and not changelog_lines[i].startswith("## ["):
                section_header = changelog_lines[i].strip()
                if section_header in added and added[section_header]:
                    i += 1
                    insert_point = i
                    while insert_point < len(changelog_lines) and changelog_lines[insert_point].strip().startswith("- "):
                        insert_point += 1
                    changelog_lines[insert_point:insert_point] = added[section_header]
                    added[section_header] = []
                else:
                    i += 1
        i += 1

    changelog_path.write_text("".join(changelog_lines))
    logging.info(f"Updated changelog for version {version}.")
    print(f"[✓] Changelog updated for version {version}")


def commit_changelog(version):
    try:
        subprocess.run(["git", "add", "."], check=True)
        subprocess.run(["git", "commit", "-m", f"chore: update changelog for v{version}"], check=True)
        logging.info("Committed changelog.")
        print(f"[✓] Committed changelog for version {version}")
    except subprocess.CalledProcessError as e:
        logging.error(f"Git commit failed: {e}")
        print("❌ Git commit failed.")
        sys.exit(1)

if __name__ == "__main__":
    try:
        version = get_current_version()
        commits = get_recent_commits()
        if commits:
            update_changelog(version, commits)
            commit_changelog(version)
        else:
            print("[i] No new commits to add to changelog.")
    except Exception as e:
        logging.exception("Failed to update changelog.")
        print(f"❌ Changelog update failed: {e}")
        sys.exit(1)
