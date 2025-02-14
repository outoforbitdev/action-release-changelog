# action-release-changelog
A GitHub Action designed to create a release based on the most recent changelog entry. 

<p>
  <a href="https://github.com/outoforbitdev/action-release-changelog/actions?query=workflow%3ATest">
    <img alt="Test build states" src="https://github.com/outoforbitdev/action-release-changelog/workflows/Test/badge.svg">
  </a>
  <a href="https://github.com/outoforbitdev/action-release-changelog/actions?query=workflow%3ARelease+branch%3Amaster">
    <img alt="Release build states" src="https://github.com/outoforbitdev/action-release-changelog/workflows/Release/badge.svg">
  </a>
  <a href="https://securityscorecards.dev/viewer/?uri=github.com/outoforbitdev/action-release-changelog">
    <img alt="OpenSSF Scorecard" src="https://api.securityscorecards.dev/projects/github.com/outoforbitdev/action-release-changelog/badge">
  </a>
  <a href="https://github.com/outoforbitdev/action-release-changelog/releases/latest">
    <img alt="Latest github release" src="https://img.shields.io/github/v/release/outoforbitdev/action-release-changelog?logo=github">
  </a>
  <a href="https://github.com/outoforbitdev/action-release-changelog/issues">
    <img alt="Open issues" src="https://img.shields.io/github/issues/outoforbitdev/action-release-changelog?logo=github">
  </a>
</p>

## Inputs

| Name | Description | Required | Default |
|------|-------------|----------|---------|
| `github-token` | GitHub token with permissions to create a release (`content: write`). | :white_check_mark: | N/A |
| `repository` | The name of the repository to create the release in (e.g. `outoforbitdev/action-release-changelog`). | :white_check_mark: | N/A |
| `changelog-file` | Filepath of the changelog file. | :x: | `./CHANGELOG.md` |
| `draft` | Create a draft release. | :x: | `true` |
| `write-to-summary` | Write to the workflow summary. | :x: | `true` |
| `dry-run` | Dry run the action without creating a real release. | :x: | `false` |

## Outputs

| Name | Description |
|------|-------------|
| `version-short` | Short version of the release (`X.X.X`). |
| `version-long` | Long version of the release (`vX.X.X`). |
| `last-version` | Last released version. |
| `release-link` | Link to the created release. |


## Usage

To use this action in your GitHub workflow, add the following step to your .github/workflows/release.yml file:
```yml
jobs:
  release:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout repository
        uses: actions/checkout@v3
      
      - name: Create Release from Changelog
        uses: outoforbitdev/action-release-changelog@latest
        with:
          github-token: ${{ secrets.GITHUB_TOKEN }}
          repository: ${{ github.repository }}
          changelog-file: "./CHANGELOG.md"
          draft: "true"
          write-to-summary: "true"
          dry-run: "false"
```
