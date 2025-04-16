#!/bin/bash

set -e

# === 🗂 Setup paths ===

cd "$(dirname "$0")"
PROJECT_ROOT=$(dirname "$PWD")
LOG_DIR="$PROJECT_ROOT/logs"
LOG_FILE="$LOG_DIR/setup.log"

mkdir -p "$LOG_DIR"
touch "$LOG_FILE"

# === 📝 Log function ===

log() {
    echo "$(date '+%Y-%m-%d %H:%M:%S') | $1" | tee -a "$LOG_FILE"
}

# Redirect all output to log
exec > >(tee -a "$LOG_FILE") 2>&1

# === 🛡️ Helper functions ===

abort() {
    log "❌ $1"
    cleanup
    exit 1
}

require_command() {
    command -v "$1" >/dev/null 2>&1 || abort "'$1' is required but not installed."
}

cleanup() {
    if [ -d "$PROJECT_ROOT/.git.bak" ]; then
        log "🧹 Restoring .git from backup..."
        rm -rf "$PROJECT_ROOT/.git"
        mv "$PROJECT_ROOT/.git.bak" "$PROJECT_ROOT/.git"
    fi

    if [ "$REPO_CREATED" = true ]; then
        log "🧨 Deleting GitHub repo due to failure..."
        curl -s -X DELETE -u "$GITHUB_USERNAME:$GITHUB_TOKEN" "https://api.github.com/repos/$GITHUB_USERNAME/$REPO_NAME"
    fi
}

# === ✅ Pre-checks ===

log "🔍 Verifying environment..."

PYTHON_VERSION=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
[[ "${PYTHON_VERSION%%.*}" -lt 3 ]] && abort "Python 3 is required. Found version: $PYTHON_VERSION"

ping -c 1 api.github.com >/dev/null 2>&1 || abort "Unable to reach GitHub. Check your network."

cd "$PROJECT_ROOT"
REPO_NAME=$(basename "$PROJECT_ROOT")

# === 📝 Check Git config for author ===

GIT_USER_NAME=$(git config --global user.name)
GIT_USER_EMAIL=$(git config --global user.email)

if [[ -z "$GIT_USER_NAME" ]]; then
    log "🔧 Git author name is not set."
    read -p "Enter your Git author name: " GIT_USER_NAME
    git config --global user.name "$GIT_USER_NAME"
fi

if [[ -z "$GIT_USER_EMAIL" ]]; then
    log "🔧 Git author email is not set."
    read -p "Enter your Git author email: " GIT_USER_EMAIL
    git config --global user.email "$GIT_USER_EMAIL"
fi

log "Git author name and email set to: $GIT_USER_NAME <$GIT_USER_EMAIL>"

# === 🔐 GitHub Auth ===

read -p "Enter your GitHub username: " GITHUB_USERNAME
read -s -p "Enter your GitHub personal access token: " GITHUB_TOKEN
echo ""

log "🔑 Validating GitHub token..."
TOKEN_CHECK=$(curl -s -o /dev/null -w "%{http_code}" -u "$GITHUB_USERNAME:$GITHUB_TOKEN" https://api.github.com/user)
[[ "$TOKEN_CHECK" != "200" ]] && abort "Invalid GitHub credentials or token."

# === 🌐 Environment Setup ===

export GITHUB_USERNAME
export GITHUB_TOKEN
export REPO_NAME
export REPO_DESCRIPTION="Created from project '$REPO_NAME'"
export REPO_PRIVATE=false
REPO_CREATED=false

# === 📡 Create GitHub repo ===

log "📡 Creating GitHub repository..."
python3 scripts/create_github_repo.py || abort "Python script failed to create repo."
REPO_CREATED=true

# === 🧠 Check local Git ===

if [ -d ".git" ]; then
    log "⚠️ Detected existing Git repository."

    if git remote get-url origin >/dev/null 2>&1; then
        log "🔗 Testing existing remote connection..."
        git ls-remote origin &>/dev/null || log "⚠️ Warning: Remote origin is unreachable or invalid."
    fi

    read -p "Do you want to replace the existing Git repo with a fresh one? [y/N]: " confirm
    if [[ "$confirm" =~ ^[Yy]$ ]]; then
        log "💾 Backing up current .git directory..."
        mv .git .git.bak
    else
        log "🛑 Aborting. Project was not modified."
        exit 0
    fi
fi

# === 🔧 Init + Push ===

log "📁 Initializing new Git repository..."

git config --global --add safe.directory "$PROJECT_ROOT"
git init
git branch -M main  # 👈 Rename default branch to 'main'
git add .
git commit -m "Initial commit"

REMOTE_URL="git@github.com:$GITHUB_USERNAME/$REPO_NAME.git"

git remote add origin "$REMOTE_URL"

log "🚀 Pushing code to GitHub..."
git push -u origin main

# === ✅ Final Cleanup ===

log "🧹 Removing backup .git directory..."
rm -rf .git.bak

log "✅ Setup complete. Repo available at: $REMOTE_URL"
