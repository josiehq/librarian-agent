"""Narnia CLI entrypoint."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from narnia.config import load_config, save_config
from narnia.git_ops import (
    detect_repos,
    git_write_all,
    git_clone_repo,
    git_pull_all,
    git_init_repo,
)
from narnia.errors import NarniaError, ConfigError, AuthError

EXIT_OK = 0
EXIT_PARTIAL = 1
EXIT_CONFIG = 2
EXIT_AUTH = 3


def cmd_see(args: argparse.Namespace) -> int:
    cfg = load_config()
    print(f"Working directory : {cfg.working_directory}")
    print(f"Git binary        : {cfg.git_binary}")
    print(f"Default branch    : {cfg.default_branch}")
    return EXIT_OK


def cmd_change(args: argparse.Namespace) -> int:
    path = Path(args.path).expanduser().resolve()
    if not path.exists() or not path.is_dir():
        raise ConfigError(f"Invalid directory: {path}")

    cfg = load_config()
    cfg.working_directory = str(path)
    save_config(cfg)

    print(f"Working directory updated to: {path}")
    return EXIT_OK


def cmd_write(args: argparse.Namespace) -> int:
    cfg = load_config()
    repos = detect_repos(Path(cfg.working_directory))

    if not repos:
        print("No git repositories found.")
        return EXIT_OK

    failures = 0
    for repo in repos:
        try:
            git_write_all(repo, cfg, dry_run=args.dry_run, verbose=args.verbose)
        except AuthError as e:
            print(f"[AUTH ERROR] {repo}: {e}")
            return EXIT_AUTH
        except Exception as e:
            failures += 1
            print(f"[FAIL] {repo}: {e}")

    if failures:
        print(f"Completed with {failures} failures.")
        return EXIT_PARTIAL

    print("All repositories updated successfully.")
    return EXIT_OK


def cmd_grab(args: argparse.Namespace) -> int:
    cfg = load_config()
    git_clone_repo(
        repo_url=args.repo_url,
        target_root=Path(cfg.working_directory),
        force=args.force,
    )
    return EXIT_OK


def cmd_pull(args: argparse.Namespace) -> int:
    cfg = load_config()
    repos = detect_repos(Path(cfg.working_directory))

    for repo in repos:
        try:
            git_pull_all(repo, cfg)
        except Exception as e:
            print(f"[FAIL] {repo}: {e}")

    return EXIT_OK


def cmd_create(args: argparse.Namespace) -> int:
    cfg = load_config()
    project_name = args.name.strip()

    if not project_name:
        raise ConfigError("Project name cannot be empty")

    target = Path(cfg.working_directory) / project_name
    if target.exists():
        raise ConfigError(f"Target already exists: {target}")

    git_init_repo(target, cfg)
    print(f"Created new repository at {target}")
    return EXIT_OK


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="narnia",
        description="NARNIA — deterministic git workflow accelerator",
    )

    sub = parser.add_subparsers(dest="command", required=True)

    p = sub.add_parser("see", help="Show current configuration")
    p.set_defaults(func=cmd_see)

    p = sub.add_parser("change", help="Change working directory")
    p.add_argument("path", help="New working directory")
    p.set_defaults(func=cmd_change)

    p = sub.add_parser("write", help="Commit and push all changes")
    p.add_argument("--dry-run", action="store_true", help="Do not modify anything")
    p.add_argument("--verbose", action="store_true", help="Verbose git output")
    p.set_defaults(func=cmd_write)

    p = sub.add_parser("grab", help="Clone a repository into the working directory")
    p.add_argument("repo_url", help="Repository URL")
    p.add_argument("--force", action="store_true", help="Overwrite existing directory")
    p.set_defaults(func=cmd_grab)

    p = sub.add_parser("pull", help="Pull latest changes for all repositories")
    p.set_defaults(func=cmd_pull)

    p = sub.add_parser("create", help="Create a new blank git repository")
    p.add_argument("name", help="New project name")
    p.set_defaults(func=cmd_create)

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    try:
        exit_code = args.func(args)
    except NarniaError as e:
        print(f"[ERROR] {e}")
        exit_code = EXIT_CONFIG
    except KeyboardInterrupt:
        print("Interrupted.")
        exit_code = EXIT_PARTIAL

    return exit_code


def run(argv: list[str] | None = None) -> int:
    """Helper for external callers (Go MCP, tower CLI)."""
    return main(argv)


if __name__ == "__main__":
    sys.exit(main())
