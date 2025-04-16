import os
import requests

def create_github_repo():
    username = os.getenv("GITHUB_USERNAME")
    token = os.getenv("GITHUB_TOKEN")
    repo_name = os.getenv("REPO_NAME")
    description = os.getenv("REPO_DESCRIPTION", "")
    private = False  # Enforce public repo

    if not username or not token or not repo_name:
        raise ValueError("GITHUB_USERNAME, GITHUB_TOKEN, and REPO_NAME must be set in the environment.")

    url = "https://api.github.com/user/repos"
    headers = {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github+json"
    }
    payload = {
        "name": repo_name,
        "description": description,
        "private": private
    }

    response = requests.post(url, headers=headers, json=payload)

    if response.status_code == 201:
        repo_url = response.json()["html_url"]
        print(f"✅ Repository created successfully: {repo_url}")
    else:
        print(f"❌ Failed to create repository: {response.status_code}")
        print(response.json())

if __name__ == "__main__":
    create_github_repo()
