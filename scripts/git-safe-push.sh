#!/bin/bash
set -euo pipefail

echo "[*] Validating commits..."
python3 validate_commits.py

echo "[*] Updating changelog..."
python3 update_changelog.py

echo "[*] Pushing changes..."
git push
