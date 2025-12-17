"""
Git operations layer for NARNIA.

Responsibilities:
- git / gh interactions
- Deterministic, non-interactive behavior
- Auth delegated to existing git/gh config
"""

from __future__ import annotations

import subprocess
from pathlib import Path
from typing import List

from .errors import NarniaError, AuthError
from .changelog import generate_changelog


def _run(cmd: list[str], cwd: Path | None = None, verbose: bool = False) -> str:
    if verbose:
        print(f"$ {' '.join(cmd)}")

    try:
        proc = subprocess.run(
            cmd,
            cwd=cwd,
            capture_output=True,
            text=True,
            check=False,
        )
    except FileNotFoundError as e:
        raise NarniaError(f"Command not found: {cmd[0]}") from e

    if proc.returncode != 0:
        stderr = proc.stderr.strip()
        if "authentication" in stderr.lower() or "permission" in stderr.lower():
            raise AuthError(stderr)
        raise NarniaError(stderr or "Command failed")

    return proc.stdout.strip()


def detect_repos(root: Path) -> List[Path]:
    repos: List[Path] = []

    if not root.exists():
        return repos

    for path in root.iterdir():
        if path.is_dir() and (path / ".git").exists():
            repos.append(path)

    return repos


def git_init_repo(target: Path, cfg) -> None:
    """Create a new GitHub repository via gh, then clone it locally."""
    repo_name = target.name

    _run(["gh", "auth", "status"], verbose=False)

    _run([
        "gh",
        "repo",
        "create",
        repo_name,
        "--private",
        "--confirm",
    ])

    _run([
        "gh",
        "repo",
        "clone",
        repo_name,
        str(target),
    ])

    _run([
        cfg.git_binary,
        "checkout",
        "-B",
        cfg.default_branch,
    ], cwd=target)


def git_clone_repo(repo_url: str, target_root: Path, force: bool = False) -> None:
    name = repo_url.rstrip("/").split("/")[-1]
    target = target_root / name

    if target.exists():
        if not force:
            raise NarniaError(f"Target exists: {target}")
        # destructive overwrite
        for item in target.iterdir():
            if item.is_dir():
                for sub in item.rglob("*"):
                    if sub.is_file():
                        sub.unlink()
                item.rmdir()
            else:
                item.unlink()
        target.rmdir()

    _run([
        "git",
        "clone",
        repo_url,
        str(target),
    ])


def git_pull_all(repo: Path, cfg) -> None:
    _run([
        cfg.git_binary,
        "pull",
        "--ff-only",
    ], cwd=repo)


def git_write_all(repo: Path, cfg, dry_run: bool = False, verbose: bool = False) -> None:
    status = _run([
        cfg.git_binary,
        "status",
        "--porcelain",
    ], cwd=repo)

    if not status:
        return

    message = generate_changelog(repo)

    if dry_run:
        print(f"[DRY RUN] {repo.name}\n{message}")
        return

    _run([
        cfg.git_binary,
        "add",
        "-A",
    ], cwd=repo, verbose=verbose)

    _run([
        cfg.git_binary,
        "commit",
        "-m",
        message,
    ], cwd=repo, verbose=verbose)

    _run([
        cfg.git_binary,
        "push",
    ], cwd=repo, verbose=verbose)
