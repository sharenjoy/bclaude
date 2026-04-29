#!/usr/bin/env python3
import subprocess
import sys

def detect_remote():
    try:
        result = subprocess.run(
            ["git", "remote", "-v"],
            capture_output=True, text=True, check=True
        )
    except subprocess.CalledProcessError:
        print("ERROR not a git repository or no remotes configured")
        sys.exit(1)

    lines = result.stdout.strip().splitlines()
    if not lines:
        print("ERROR no remotes found — run 'git remote add origin <url>' first")
        sys.exit(1)

    # Use the first fetch remote
    for line in lines:
        if "(fetch)" not in line:
            continue
        url = line.split()[1]
        if "github.com" in url:
            print(f"GITHUB {url}")
            return
        if "gitlab.com" in url or "gitlab" in url:
            print(f"GITLAB {url}")
            return

    print(f"ERROR remote type not recognized (not GitHub or GitLab): {lines[0].split()[1]}")
    sys.exit(1)

if __name__ == "__main__":
    detect_remote()
