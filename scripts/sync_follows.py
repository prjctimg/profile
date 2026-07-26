#!/usr/bin/env python3
"""Sync follows across prjctimg, skchr, and iseeheaven accounts.

Ensures all three accounts follow the same set of users by using
prjctimg's following list as the source of truth.
"""

import json
import subprocess
import sys


def get_following(username, token):
    """Get list of users that username follows."""
    following = []
    page = 1
    while True:
        result = subprocess.run(
            [
                "gh", "api", "paginate",
                f"/users/{username}/following?per_page=100&page={page}",
                "-H", "Accept: application/vnd.github+json",
            ],
            capture_output=True, text=True,
            env={"GH_TOKEN": token, "PATH": subprocess.check_output(["which", "gh"]).strip().decode() + ":" + __import__("os").environ["PATH"]},
        )
        if result.returncode != 0:
            break
        users = json.loads(result.stdout) if result.stdout.strip() else []
        if not users:
            break
        following.extend([u["login"] for u in users])
        page += 1
    return following


def is_following(target, token):
    """Check if the authenticated user follows target."""
    result = subprocess.run(
        [
            "gh", "api", f"/user/following/{target}",
            "-f", "X-GitHub-Api-Version=2022-11-28",
        ],
        capture_output=True, text=True,
        env={"GH_TOKEN": token, "PATH": subprocess.check_output(["which", "gh"]).strip().decode() + ":" + __import__("os").environ["PATH"]},
    )
    return result.returncode == 0


def follow_user(target, token):
    """Follow a user."""
    result = subprocess.run(
        [
            "gh", "api", f"/user/following/{target}",
            "--method", "PUT",
            "-f", "X-GitHub-Api-Version=2022-11-28",
        ],
        capture_output=True, text=True,
        env={"GH_TOKEN": token, "PATH": subprocess.check_output(["which", "gh"]).strip().decode() + ":" + __import__("os").environ["PATH"]},
    )
    return result.returncode == 0


def sync_account(source_following, target_username, target_token, dry_run=False):
    """Ensure target follows all users in source_following."""
    print(f"\n--- Syncing follows for @{target_username} ---")
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

    source_token = __import__("os").environ.get("SOURCE_TOKEN", "")
    target_skchr_token = __import__("os").environ.get("SKCHR_TOKEN", "")
    target_iseeheaven_token = __import__("os").environ.get("ISEEHEAVEN_TOKEN", "")

    if not source_token:
        print("Error: SOURCE_TOKEN not set", file=sys.stderr)
        sys.exit(1)

    print("Fetching prjctimg's following list...")
    result = subprocess.run(
        [
            "gh", "api", "paginate",
            "/user/following?per_page=100",
            "-H", "Accept: application/vnd.github+json",
        ],
        capture_output=True, text=True,
        env={"GH_TOKEN": source_token, "PATH": subprocess.check_output(["which", "gh"]).strip().decode() + ":" + __import__("os").environ["PATH"]},
    )

    if result.returncode != 0:
        print(f"Error fetching following list: {result.stderr}", file=sys.stderr)
        sys.exit(1)

    source_following = [u["login"] for u in json.loads(result.stdout)]
    print(f"prjctimg follows {len(source_following)} users")

    if target_skchr_token:
        sync_account(source_following, "skchr", target_skchr_token, dry_run)
    else:
        print("\nSkipping skchr: SKCHR_TOKEN not set")

    if target_iseeheaven_token:
        sync_account(source_following, "iseeheaven", target_iseeheaven_token, dry_run)
    else:
        print("\nSkipping iseeheaven: ISEEHEAVEN_TOKEN not set")

    print("\nDone!")


if __name__ == "__main__":
    main()
