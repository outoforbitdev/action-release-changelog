import os
import re
import sys
from github import Github, Auth, Repository
import subprocess

def release_version(
        github_token: str, 
        changelog_file: str, 
        draft: str, 
        should_write_to_summary: str, 
        dry_run: str, 
        repo_name: str):
    client = get_github_client(github_token)
    try:
        first_version = find_first_changelog_version(changelog_file)
        short_version = first_version
        long_version = f"v{short_version}"
        write_to_output_variable("short_version", short_version)
        write_to_output_variable("long_version", long_version)

        repo = client.get_repo(repo_name)
        last_version = get_last_version(repo)
        write_to_output_variable("last_version", last_version)
        
        if not dry_run:
                release = create_github_release(repo, long_version, github_token, f"Release {first_version}", draft)
                if should_write_to_summary:
                    write_release_to_summary(first_version, release.html_url)
    except Exception as e:
        client.close()
        raise e
    client.close()

def get_github_client(github_token: str):
    auth = Auth.Token(github_token)
    client = Github(auth=auth)
    return client

def find_first_changelog_version(changelog_path="CHANGELOG.md"):
    version_pattern = re.compile(r'^#{1,2} (v*)(\d+\.\d+\.\d+)')
    
    with open(changelog_path, 'r', encoding='utf-8') as file:
        for line in file:
            match = version_pattern.match(line.strip())
            if match:
                return match.group(2)
    
    error("No version found in changelog")

def error(message):
    raise Exception(message)

def get_last_version(repo: Repository):
    print(repo.get_releases())
    if repo.get_releases().totalCount == 0:
        return None
    return repo.get_latest_release().tag_name

def create_github_release(repo: Repository, tag_name: str, body: str=None, draft: bool=True, prerelease: bool=False,):
    if release_exists(repo, tag_name):
        error(f"Release {tag_name} already exists")
    release = repo.create_git_tag_and_release(tag=tag_name, tag_message=body, draft=draft, prerelease=prerelease)
    return release

def release_exists(repo, tag_name):
    release = repo.get_release(tag_name)
    return release is not None
    
def write_release_to_summary(release_version, release_link):
    write_to_summary(f"## Release Created\n\n- [{release_version}]({release_link})\n\n")

def write_to_summary(content):
    step_summary_path = os.getenv("GITHUB_STEP_SUMMARY")
    if step_summary_path:
        with open(step_summary_path, "a") as summary_file:
            summary_file.write(content)

def write_to_output_variable(variable_name: str, value: str):
    with open(os.environ["GITHUB_OUTPUT"], "a") as output:
        output.write(f"{variable_name}={value}\n")

if __name__ == "__main__":
    github_token = sys.argv[1]
    changelog_file = sys.argv[2]
    draft = sys.argv[3]
    should_write_to_summary = sys.argv[4]
    dry_run = sys.argv[5]
    repo_name = sys.argv[6]
    release_version(github_token, changelog_file, draft, should_write_to_summary, dry_run, repo_name)
