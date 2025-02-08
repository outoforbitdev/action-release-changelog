#!/bin/sh -l

github_token=$1
changelog_file=$2
draft=$3
write_to_summary=$4
dry_run=$5

python create_release.py github_token changelog_file draft write_to_summary dry_run
