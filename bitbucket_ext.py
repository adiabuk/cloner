#!/usr/bin/env python

import bitbucket


def do_bb(username, password):

    try:
        from urllib.parse import quote
    except ImportError:
        from urllib.parse import quote

    oauth_key = None
    oauth_secret = None
    _verbose = False
    owner = username

    bucket = bitbucket.BitBucket(
        username=username,
        password=password,
        oauth_key=oauth_key,
        oauth_secret=oauth_secret,
        verbose=_verbose,
    )

    user = bucket.user(owner)
    repos = sorted(user.repositories(), key=lambda repo: repo.get("name"))
    urls = []

    for repo in repos:
        owner_url = quote(owner)
        slug = repo.get('slug')
        slug_url = quote(slug)
        url = "git@bitbucket.org:%s/%s.git" % (owner_url, slug_url)
        urls.append(url)
    return urls
