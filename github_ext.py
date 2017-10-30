#!/usr/bin/env python

from __future__ import print_function
from platform import python_version_tuple
from github import Github

def do_gh(username, password):
    github = Github(username, password)
    get_repos = github.get_user().get_repos
    return get_repos()
