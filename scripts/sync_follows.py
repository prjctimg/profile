#!/usr/bin/env python3
"""Sync follows across prjctimg, skchr, and iseeheaven accounts.

Ensures all three accounts follow the same set of users by using
prjctimg's following list as the source of truth.
"""

import json
import os
import sys
import urllib.request


API = "https://api.github.com"


def api_request(url, token, method="GET"):
    """Make an authenticated GitHub API request."""
    req = urllib.request.Request(url, method=method)
    req.add_header("Authorization", f"Bearer {token}")
    req.add_header("Accept", "application/vnd.github+json")
    req.add_header("X-GitHub-Api-Version", "2022-11-28")
    try:
        with urllib.request.urlopen(req) as resp:
            return json.loads(resp.read()), resp.status
    except urllib.error.HTTPError as e:
        return None, e.code


def get_following(token):
    """Get list of users the authenticated user follows."""
    following = []
    url = f"{API}/user/following?per_page=100"
    while url:
        data, status = api_request(url, token)
        if status != 200 or not data:
            break
        following.extend([u["login"] for u in data])
        # Check for next page via Link header — fall back to manual pagination
        url = None
        for header_val in []:
            pass
        # Simple: just use page param
    # Re-do with simple pagination
    following = []
    page = 1
    while True:
        data, status = api_request(f"{API}/user/following?per_page=100&page={page}", token)
        if status != 200 or not data:
            break
        following.extend([u["login"] for u in data])
        if len(data) < 100:
            break
        page += 1
    return following


def is_following(username, token):
    """Check if the authenticated user follows username."""
    _, status = api_request(f"{API}/user/following/{username}", token)
    return status == 204


def follow_user(username, token):
    """Follow a user. Returns True on success."""
    _, status = api_request(f"{API}/user/following/{username}", token, method="PUT")
    return status == 204


def sync_account(source_following, target_token, dry_run=False):
    """Ensure target follows all users in source_following. Returns count of new follows."""
    followed = 0
    skipped = 0

    for user in source_following:
        if is_following(user, target_token):
            skipped += 1
            continue

        if dry_run:
            print(f"  [dry-run] Would follow @{user}")
            followed += 1
            continue

        if follow_user(user, target_token):
            print(f"  Followed @{user}")
            followed += 1
        else:
            print(f"  Failed to follow @{user}")

    print(f"  Result: {followed} followed, {skipped} already following")
    return followed


def main():
    dry_run = "--dry-run" in sys.argv

    source_token = os.environ.get("SOURCE_TOKEN", "")
    skchr_token = os.environ.get("SKCHR_TOKEN", "")
    iseeheaven_token = os.environ.get("ISEEHEAVEN_TOKEN", "")

    if not source_token:
        print("Error: SOURCE_TOKEN not set", file=sys.stderr)
        sys.exit(1)

    print("Fetching prjctimg's following list...")
    source_following = get_following(source_token)
    print(f"prjctimg follows {len(source_following)} users")

    if skchr_token:
        print("\n--- Syncing follows for @skchr ---")
        sync_account(source_following, skchr_token, dry_run)
    else:
        print("\nSkipping skchr: SKCHR_TOKEN not set")

    if iseeheaven_token:
        print("\n--- Syncing follows for @iseeheaven ---")
        sync_account(source_following, iseeheaven_token, dry_run)
    else:
        print("\nSkipping iseeheaven: ISEEHEAVEN_TOKEN not set")

    print("\nDone!")


if __name__ == "__main__":
    main()
