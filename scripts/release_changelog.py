import re
from datetime import datetime
from pathlib import Path

CHANGELOG_FILE = Path("CHANGELOG.md")
VERSION_FILE = Path("src/gavins_v1_template/__version__.py")  # Update with your actual path if needed

def get_current_version():
    # Read the version from __version__.py
    version_globals = {}
    with open(VERSION_FILE) as f:
        exec(f.read(), version_globals)
    return version_globals.get("__version__", None)

def release_changelog(version: str):
    changelog = CHANGELOG_FILE.read_text()

    # Extract unreleased section
    unreleased_match = re.search(
        r"## \[Unreleased\](.*?)(?=## \[|$)",
        changelog,
        re.DOTALL
    )
    if not unreleased_match:
        print("❌ No 'Unreleased' section found.")
        return

    unreleased_content = unreleased_match.group(1).strip()

    # Skip if unreleased section is empty
    if not unreleased_content or all(section.strip() == "" or section.strip() == "### Added\n\n### Changed\n\n### Fixed" for section in unreleased_content.split("\n\n")):
        print("⚠️ 'Unreleased' section is empty. Nothing to release.")
        return

    # Format the new version block
    today = datetime.today().strftime("%Y-%m-%d")
    release_block = f"## [{version}] - {today}\n{cleaned_content.strip()}\n\n"

    # Replace 'Unreleased' section with a fresh template
    new_unreleased = "## [Unreleased]\n\n### Added\n\n### Changed\n\n### Fixed\n\n"
    new_changelog = re.sub(
        r"## \[Unreleased\].*?(?=## \[|$)",
        new_unreleased,
        changelog,
        flags=re.DOTALL
    )

    # Insert new version block below new unreleased section
    insert_position = new_changelog.find("## [Unreleased]") + len(new_unreleased)
    final_changelog = (
        new_changelog[:insert_position] +
        "\n" + release_block +
        new_changelog[insert_position:]
    )

    CHANGELOG_FILE.write_text(final_changelog.strip() + "\n")
    print(f"✅ Released version {version} in CHANGELOG.md")

if __name__ == "__main__":
    version = get_current_version()
    if version:
        release_changelog(version)
    else:
        print("❌ Version not found in __version__.py")
