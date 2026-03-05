from __future__ import annotations

from pathlib import Path
from typing import Literal

from albert_code.core.paths.global_paths import ALBERT_CODE_HOME, GlobalPath
from albert_code.core.paths.local_config_walk import walk_local_config_dirs_all
from albert_code.core.trusted_folders import trusted_folders_manager

_config_paths_locked: bool = True


class ConfigPath(GlobalPath):
    @property
    def path(self) -> Path:
        if _config_paths_locked:
            raise RuntimeError("Config path is locked")
        return super().path


def _resolve_config_path(basename: str, type: Literal["file", "dir"]) -> Path:
    cwd = Path.cwd()
    is_folder_trusted = trusted_folders_manager.is_trusted(cwd)
    if not is_folder_trusted:
        return ALBERT_CODE_HOME.path / basename
    if type == "file":
        if (candidate := cwd / ".albert-code" / basename).is_file():
            return candidate
    elif type == "dir":
        if (candidate := cwd / ".albert-code" / basename).is_dir():
            return candidate
    return ALBERT_CODE_HOME.path / basename


def _discover_local_config_dirs_all(
    root: Path,
) -> tuple[tuple[Path, ...], tuple[Path, ...], tuple[Path, ...]]:
    if not trusted_folders_manager.is_trusted(root):
        return ((), (), ())
    return walk_local_config_dirs_all(root)


def discover_local_tools_dirs(root: Path) -> list[Path]:
    return list(_discover_local_config_dirs_all(root)[0])


def discover_local_skills_dirs(root: Path) -> list[Path]:
    return list(_discover_local_config_dirs_all(root)[1])


def discover_local_agents_dirs(root: Path) -> list[Path]:
    return list(_discover_local_config_dirs_all(root)[2])


def unlock_config_paths() -> None:
    global _config_paths_locked
    _config_paths_locked = False


CONFIG_FILE = ConfigPath(lambda: _resolve_config_path("config.toml", "file"))
CONFIG_DIR = ConfigPath(lambda: CONFIG_FILE.path.parent)
PROMPTS_DIR = ConfigPath(lambda: _resolve_config_path("prompts", "dir"))
HISTORY_FILE = ConfigPath(lambda: _resolve_config_path("history", "file"))
