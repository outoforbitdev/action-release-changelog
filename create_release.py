import os
import re
import sys
import requests
import subprocess

def release_exists(repo, tag_name, token):
    url = f"https://api.github.com/repos/{repo}/releases/tags/{tag_name}"
    headers = {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github.v3+json"
    }
    response = requests.get(url, headers=headers)
    return response.status_code == 200

def create_github_release(repo, tag_name, token, body=None, draft=True, prerelease=False,):
    if release_exists(repo, tag_name, token):
        print(f"Release with tag {tag_name} already exists.")
        return None
    url = f"https://api.github.com/repos/{repo}/releases"
    headers = {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github.v3+json"
    }
    data = {
        "tag_name": tag_name,
        "name": tag_name,
        "body": body or "",
        "draft": draft,
        "prerelease": prerelease
    }
    response = requests.post(url, json=data, headers=headers)
    return response.json()
    
def write_release_to_output(release_version, release_link):
    write_to_summary(f"## Release Created\n\n- [{release_version}]({release_link})\n\n")

def release_version(github_token, changelog_file, draft, should_write_to_summary, dry_run, repo_name):
    first_version = find_first_changelog_version(changelog_file)
    if first_version[0] != "v":
        first_version = f"v{first_version}"
    print(f"First version found: {first_version}")
    
    if first_version:
        if repo_name and not dry_run:
            release_response = create_github_release(repo_name, first_version, github_token, f"Release {first_version}", draft)
            print(release_response)
            if should_write_to_summary:
                write_release_to_output(first_version, release_response["html_url"])
        else:
            print("Could not determine repository name.")

def write_to_summary(content):
    step_summary_path = os.getenv("GITHUB_STEP_SUMMARY")
    if step_summary_path:
        with open(step_summary_path, "a") as summary_file:
            summary_file.write(content)

def find_first_changelog_version(changelog_path="CHANGELOG.md"):
    version_pattern = re.compile(r'^#{1,2} (\d+\.\d+\.\d+)')
    
    with open(changelog_path, 'r', encoding='utf-8') as file:
        for line in file:
            match = version_pattern.match(line.strip())
            if match:
                return match.group(1)
    
    return None  # Return None if no version is found

if __name__ == "__main__":
    github_token = sys.argv[1]
    changelog_file = sys.argv[2]
    draft = sys.argv[3]
    should_write_to_summary = sys.argv[4]
    dry_run = sys.argv[5]
    repository = sys.argv[6]
    release_version(github_token, changelog_file, draft, should_write_to_summary, dry_run, repository)
