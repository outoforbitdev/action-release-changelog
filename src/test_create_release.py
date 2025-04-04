import os
import unittest
from unittest.mock import MagicMock, mock_open, patch
from create_release import create_github_release, find_first_changelog_version, get_last_version, release_exists, release_version, write_dry_run_to_summary, write_release_to_summary, write_to_output_variable, write_to_summary

class MockRelease:
    __draft = False
    @property
    def draft(self):
        return self.__draft
    
    @draft.setter
    def draft(self, value):
        self.__draft = value

    
    @property
    def tag_name(self):
        return "v1.2.3"
    
    @property
    def created_at(self):
        return 1

    @property
    def html_url(self):
        return "https://github.com"

class MockPaginatedList:
    __total_count = 1

    @property
    def totalCount(self):
        return len(self.__elements)
    
    __elements = [ MockRelease() ]

    def set_elements(self, elements):
        self.__elements = elements

    def __iter__(self):
        yield from self.__elements

def is_version_one_two_three(version):
    if version == "v1.2.3":
        return MockRelease()
    return None

def get_mock_repo():
    mock_repo = MagicMock()
    mock_repo.get_releases.return_value = MockPaginatedList()
    mock_repo.create_git_release.return_value = MockRelease()
    return mock_repo

def get_empty_mock_repo():
    mock_repo = MagicMock()
    mock_paginated_list = MockPaginatedList()
    mock_paginated_list.set_elements([])
    mock_repo.get_releases.return_value = mock_paginated_list
    mock_repo.create_git_release.return_value = MockRelease()
    return mock_repo


class TestFindFirstChangelogVersion(unittest.TestCase):
    @patch("builtins.open", new_callable=mock_open, read_data="# v1.2.3")
    def test_find_first_changelog_version_header_one(self, mock_file):
        version = find_first_changelog_version("CHANGELOG.md")
        self.assertEqual(version, "1.2.3")

    @patch("builtins.open", new_callable=mock_open, read_data="## v1.2.3")
    def test_find_first_changelog_version_header_two(self, mock_file):
        version = find_first_changelog_version("CHANGELOG.md")
        self.assertEqual(version, "1.2.3")

    @patch("builtins.open", new_callable=mock_open, read_data="")
    def test_find_first_changelog_version_error(self, mock_file):
        with self.assertRaises(Exception):
            find_first_changelog_version("CHANGELOG.md")

class TestReleaseExists(unittest.TestCase):
    def test_release_exists_true(self):
        mock_repo = get_mock_repo()
        self.assertTrue(release_exists(mock_repo, "v1.2.3"))

    def test_release_exists_false(self):
        mock_repo = get_mock_repo()
        self.assertFalse(release_exists(mock_repo, "v1.2.4"))
        self

    def test_release_exists_no_repos(self):
        mock_repo = get_empty_mock_repo()
        self.assertFalse(release_exists(mock_repo, "v1.2.4"))
    
    def test_release_exists_draft_and_exists(self):
        mock_repo = get_mock_repo()
        one_two_three_release = MockRelease()
        one_two_three_release_draft = MockRelease()
        one_two_three_release_draft.draft = True
        mock_paginated_list = MockPaginatedList()
        mock_paginated_list.set_elements([one_two_three_release_draft, one_two_three_release])
        mock_repo.get_releases.return_value = mock_paginated_list
        self.assertTrue(release_exists(mock_repo, "v1.2.3"))

    def test_release_exists_draft(self):
        mock_repo = get_mock_repo()
        release = MockRelease()
        release.draft = True
        mock_paginated_list = MockPaginatedList()
        mock_paginated_list.set_elements([release])
        mock_repo.get_releases.return_value = mock_paginated_list
        self.assertFalse(release_exists(mock_repo, "v1.2.3"))

class TestCreateGithubRelease(unittest.TestCase):
    def test_create_github_release_exists(self):
        mock_repo = get_mock_repo()
        with self.assertRaises(Exception):
            create_github_release(mock_repo, "v1.2.3", "body", draft=True, prerelease=False)

    def test_create_github_release_success(self):
        mock_repo = get_mock_repo()
        create_github_release(mock_repo, "v1.2.4", "body", draft=True, prerelease=False)

class TestGetLastVersion(unittest.TestCase):
    def test_get_last_version_exists(self):
        mock_repo = get_mock_repo()
        version = get_last_version(mock_repo)
        self.assertEqual(version, "v1.2.3")

    def test_get_last_version_none_exist(self):
        mock_repo = get_empty_mock_repo()
        version = get_last_version(mock_repo)
        self.assertIsNone(version)

class TestWriteToOutputVariable(unittest.TestCase):
    @patch("builtins.open", new_callable=mock_open)
    @patch.dict(os.environ, {"GITHUB_OUTPUT": "output.txt"})
    def test_write_to_output_variable(self, mock_file):
        write_to_output_variable("test_var", "test_value")
        mock_file().write.assert_called_with("test_var=\"test_value\"\n")

class TestWriteToSummary(unittest.TestCase):
    @patch("builtins.open", new_callable=mock_open)
    @patch.dict(os.environ, {"GITHUB_STEP_SUMMARY": "summary.txt"})
    def test_write_to_summary(self, mock_file):
        write_to_summary("content")
        mock_file().write.assert_called_with("content")

    @patch("builtins.open", new_callable=mock_open)
    @patch.dict(os.environ, {"GITHUB_STEP_SUMMARY": "summary.txt"})
    def test_write_release_to_summary(self, mock_file):
        write_release_to_summary("v1.2.3", "https://github.com")
        mock_file().write.assert_called_with("## Release Created\n\n- [v1.2.3](https://github.com)\n\n")

    @patch("builtins.open", new_callable=mock_open)
    @patch.dict(os.environ, {"GITHUB_STEP_SUMMARY": "summary.txt"})
    def test_write_dry_run_to_summary(self, mock_file):
        write_dry_run_to_summary("v1.2.3")
        mock_file().write.assert_called_with("## Dry Run\n\n Release v1.2.3 would have been created\n\n")

class TestReleaseVersion(unittest.TestCase):
    @patch("create_release.get_github_client")
    @patch("create_release.find_first_changelog_version", return_value="1.2.3")
    @patch("create_release.get_last_version", return_value="v1.2.2")
    @patch("create_release.release_exists", return_value=False)
    @patch("create_release.create_github_release")
    @patch("create_release.write_to_output_variable")
    @patch("create_release.write_dry_run_to_summary")
    @patch("create_release.write_release_to_summary")
    @patch("create_release.write_to_summary")
    def test_release_version(self, 
                                        mock_write_summary,
                                        mock_write_release_summary, 
                                        mock_write_dry_run_summary, 
                                        mock_output, 
                                        mock_create_release, 
                                        mock_release_exists, 
                                        mock_get_last_version, 
                                        mock_find_version, 
                                        mock_get_client):
        mock_repo = MagicMock()
        mock_get_client.return_value.get_repo.return_value = mock_repo
        
        release_version("token", "CHANGELOG.md", draft=True, should_write_to_summary=True, dry_run=False, repo_name="test_repo")
        
        mock_output.assert_any_call("version-short", "1.2.3")
        mock_output.assert_any_call("version-long", "v1.2.3")
        mock_output.assert_any_call("last-version", "v1.2.2")
        mock_write_summary.assert_not_called()
        mock_create_release.assert_called_with(mock_repo, "v1.2.3", draft=True)
        mock_write_release_summary.assert_called_with("v1.2.3", mock_create_release.return_value.html_url)
        mock_write_dry_run_summary.assert_not_called()
    
    @patch("create_release.get_github_client")
    @patch("create_release.find_first_changelog_version", return_value="1.2.3")
    @patch("create_release.get_last_version", return_value="v1.2.3")
    @patch("create_release.release_exists", return_value=True)
    @patch("create_release.create_github_release")
    @patch("create_release.write_to_output_variable")
    @patch("create_release.write_dry_run_to_summary")
    @patch("create_release.write_release_to_summary")
    @patch("create_release.write_to_summary")
    def test_release_version_no_change(self, 
                                        mock_write_summary,
                                        mock_write_release_summary, 
                                        mock_write_dry_run_summary, 
                                        mock_output, 
                                        mock_create_release, 
                                        mock_release_exists, 
                                        mock_get_last_version, 
                                        mock_find_version, 
                                        mock_get_client):
        mock_repo = MagicMock()
        mock_get_client.return_value.get_repo.return_value = mock_repo
        
        release_version("token", "CHANGELOG.md", draft=True, should_write_to_summary=True, dry_run=False, repo_name="test_repo")

        mock_output.assert_any_call("last-version", "v1.2.3")
        mock_write_summary.assert_called_with("## No Changes\n\nVersion in changelog (v1.2.3) already exists as a release\n\n")
        mock_create_release.assert_not_called()
        mock_write_release_summary.assert_not_called()
        mock_write_dry_run_summary.assert_not_called()

    @patch("create_release.get_github_client")
    @patch("create_release.find_first_changelog_version", return_value="1.2.3")
    @patch("create_release.get_last_version", return_value="v1.2.2")
    @patch("create_release.release_exists", return_value=False)
    @patch("create_release.create_github_release")
    @patch("create_release.write_to_output_variable")
    @patch("create_release.write_dry_run_to_summary")
    @patch("create_release.write_release_to_summary")
    @patch("create_release.write_to_summary")
    def test_release_version_dry_run(self, 
                                        mock_write_summary,
                                        mock_write_release_summary, 
                                        mock_write_dry_run_summary, 
                                        mock_output, 
                                        mock_create_release, 
                                        mock_release_exists, 
                                        mock_get_last_version, 
                                        mock_find_version, 
                                        mock_get_client):
        mock_repo = MagicMock()
        mock_get_client.return_value.get_repo.return_value = mock_repo
        
        release_version("token", "CHANGELOG.md", draft=True, should_write_to_summary=True, dry_run=True, repo_name="test_repo")
        
        mock_output.assert_any_call("version-short", "1.2.3")
        mock_output.assert_any_call("version-long", "v1.2.3")
        mock_output.assert_any_call("last-version", "v1.2.2")
        mock_write_summary.assert_not_called()
        mock_create_release.assert_not_called()
        mock_write_release_summary.assert_not_called()
        mock_write_dry_run_summary.assert_called_once()
        
    @patch("create_release.get_github_client")
    @patch("create_release.find_first_changelog_version", return_value="1.2.3")
    @patch("create_release.get_last_version", return_value="v1.2.2")
    @patch("create_release.release_exists", return_value=False)
    @patch("create_release.create_github_release")
    @patch("create_release.write_to_output_variable")
    @patch("create_release.write_dry_run_to_summary")
    @patch("create_release.write_release_to_summary")
    @patch("create_release.write_to_summary")
    def test_release_version_no_summary(self, 
                                        mock_write_summary,
                                        mock_write_release_summary, 
                                        mock_write_dry_run_summary, 
                                        mock_output, 
                                        mock_create_release, 
                                        mock_release_exists, 
                                        mock_get_last_version, 
                                        mock_find_version, 
                                        mock_get_client):
        mock_repo = MagicMock()
        mock_get_client.return_value.get_repo.return_value = mock_repo
        
        release_version("token", "CHANGELOG.md", draft=True, should_write_to_summary=False, dry_run=False, repo_name="test_repo")
        
        mock_output.assert_any_call("version-short", "1.2.3")
        mock_output.assert_any_call("version-long", "v1.2.3")
        mock_output.assert_any_call("last-version", "v1.2.2")
        mock_write_summary.assert_not_called()
        mock_create_release.assert_called_once()
        mock_write_release_summary.assert_not_called()
        mock_write_dry_run_summary.assert_not_called()

