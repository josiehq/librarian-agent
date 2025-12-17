"""NARNIA configuration handling.

Responsibilities:
- Load and validate persistent user configuration
- Provide sane defaults on first run
- Never prompt the user interactively
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path
import tomllib

try:
    import tomli_w
except ImportError:  # Fallback to a minimal writer if tomli_w is unavailable
    tomli_w = None

from .errors import ConfigError

APP_NAME = "narnia"
CONFIG_DIR = Path(os.environ.get("XDG_CONFIG_HOME", Path.home() / ".config")) / APP_NAME
CONFIG_FILE = CONFIG_DIR / "config.toml"


@dataclass
class NarniaConfig:
    working_directory: str
    git_binary: str
    default_branch: str


DEFAULT_CONFIG = NarniaConfig(
    working_directory=str(Path.home() / "DEV"),
    git_binary="/usr/bin/git",
    default_branch="main",
)


def _dump_toml(data: dict) -> str:
    """Minimal TOML writer for simple string-only configs.

    Avoids adding an extra dependency (tomli_w) when not available.
    """

    def escape(value: str) -> str:
        return value.replace("\\", "\\\\").replace("\"", "\\\"")

    lines = [f'{key} = "{escape(str(value))}"' for key, value in data.items()]
    return "\n".join(lines) + "\n"


def load_config() -> NarniaConfig:
    """
    Load configuration from disk. If it does not exist, create it with defaults.
    """
    if not CONFIG_FILE.exists():
        CONFIG_DIR.mkdir(parents=True, exist_ok=True)
        save_config(DEFAULT_CONFIG)
        return DEFAULT_CONFIG

    try:
        with CONFIG_FILE.open("rb") as f:
            raw = tomllib.load(f)
    except Exception as e:
        raise ConfigError(f"Failed to read config file: {e}")

    try:
        return NarniaConfig(
            working_directory=raw["working_directory"],
            git_binary=raw.get("git_binary", DEFAULT_CONFIG.git_binary),
            default_branch=raw.get("default_branch", DEFAULT_CONFIG.default_branch),
        )
    except KeyError as e:
        raise ConfigError(f"Missing config key: {e}")


def save_config(cfg: NarniaConfig) -> None:
    """
    Persist configuration to disk.
    """
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)

    data = {
        "working_directory": cfg.working_directory,
        "git_binary": cfg.git_binary,
        "default_branch": cfg.default_branch,
    }

    try:
        if tomli_w:
            with CONFIG_FILE.open("wb") as f:
                tomli_w.dump(data, f)
        else:
            # Write using lightweight TOML formatter to avoid hard dependency
            CONFIG_FILE.write_text(_dump_toml(data), encoding="utf-8")
    except Exception as e:
        raise ConfigError(f"Failed to write config: {e}")
