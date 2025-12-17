"""Deterministic changelog generator for NARNIA.

This module produces a *baseline*, non-AI commit message derived purely
from git state. It is intentionally boring, stable, and offline.

Any LLM-based enhancement MUST wrap or post-process this output and
must never replace it.
"""

from __future__ import annotations

import subprocess
from pathlib import Path
from typing import Dict, Tuple


def _run_git(args: list[str], repo: Path) -> str:
    proc = subprocess.run(
        ["git", *args],
        cwd=repo,
        capture_output=True,
        text=True,
        check=False,
    )

    if proc.returncode != 0:
        raise RuntimeError(proc.stderr.strip() or "git command failed")

    return proc.stdout


def _parse_numstat(repo: Path) -> Tuple[int, int, int, int]:
    """
    Returns:
        added_lines, removed_lines, files_added, files_removed
    """
    out = _run_git(["diff", "--numstat"], repo)

    added_lines = 0
    removed_lines = 0
    files_added = 0
    files_removed = 0

    for line in out.splitlines():
        if not line.strip():
            continue

        a, d, path = line.split("\t", 2)

        if a.isdigit():
            added_lines += int(a)
        if d.isdigit():
            removed_lines += int(d)

        if path.startswith("/dev/null"):
            files_removed += 1
        elif a.isdigit() and d == "0":
            files_added += 1

    return added_lines, removed_lines, files_added, files_removed


def _parse_file_changes(repo: Path) -> Dict[str, int]:
    out = _run_git(["diff", "--name-status"], repo)

    summary = {"A": 0, "M": 0, "D": 0}

    for line in out.splitlines():
        if not line.strip():
            continue
        status, _ = line.split("\t", 1)
        if status in summary:
            summary[status] += 1

    return summary


def generate_changelog(repo: Path) -> str:
    """Generate a deterministic commit message describing current changes."""
    project = repo.name

    added_lines, removed_lines, files_added, files_removed = _parse_numstat(repo)
    file_summary = _parse_file_changes(repo)

    lines = [
        f"Update {project}",
        "",
        "Change summary:",
        f"- Lines added   : {added_lines}",
        f"- Lines removed : {removed_lines}",
        f"- Files added   : {files_added}",
        f"- Files removed : {files_removed}",
        "",
        "File changes:",
        f"- Modified : {file_summary['M']}",
        f"- Added    : {file_summary['A']}",
        f"- Deleted  : {file_summary['D']}",
    ]

    return "\n".join(lines)
