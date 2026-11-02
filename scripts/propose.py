#!/usr/bin/env python3
"""Publish a bot-owned update branch and PR. Never update main or merge a PR."""
import json
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parents[1]
BRANCH = "automation/upstream-update"


def run(*args, check=True):
    result = subprocess.run(args, cwd=ROOT, text=True, capture_output=True)
    if check and result.returncode:
        raise RuntimeError(f"{args[0]} failed ({result.returncode}): {result.stderr.strip()}")
    return result


def main():
    # Only files produced by the updater may be included in this bot commit.
    changed = run("git", "status", "--porcelain", "--untracked-files=all").stdout.splitlines()
    if not changed:
        print("No update proposal needed.")
        return
    for entry in changed:
        path = entry[3:]
        if path != "sources.lock.json" and path != "docs/UPSTREAM-UPDATE.md" and not path.startswith(("vendor/", "dist/")):
            raise RuntimeError(f"Unexpected changed file; refusing bot commit: {path}")
    run("git", "config", "user.name", "github-actions[bot]")
    run("git", "config", "user.email", "41898282+github-actions[bot]@users.noreply.github.com")
    run("git", "checkout", "-B", BRANCH)
    run("git", "add", "sources.lock.json", "vendor", "dist", "docs/UPSTREAM-UPDATE.md")
    run("git", "commit", "-m", "chore(rules): propose upstream update")
    run("gh", "auth", "setup-git")
    # This branch belongs to this workflow. Its previous remote SHA is the lease.
    remote = run("git", "ls-remote", "--heads", "origin", f"refs/heads/{BRANCH}").stdout.strip()
    expected = remote.split()[0] if remote else ""
    run("git", "push", f"--force-with-lease=refs/heads/{BRANCH}:{expected}", "origin", f"HEAD:refs/heads/{BRANCH}")
    existing = json.loads(run("gh", "pr", "list", "--state", "open", "--head", BRANCH,
                              "--base", "main", "--json", "number").stdout)
    body = ROOT / "docs/UPSTREAM-UPDATE.md"
    if existing:
        result = run("gh", "pr", "edit", str(existing[0]["number"]), "--body-file", str(body))
    else:
        result = run("gh", "pr", "create", "--base", "main", "--head", BRANCH,
                     "--title", "chore(rules): review upstream changes", "--body-file", str(body))
    print(result.stdout)
    print("Candidate checks passed before push. Review CN additions; no automatic merge.")


if __name__ == "__main__":
    main()
