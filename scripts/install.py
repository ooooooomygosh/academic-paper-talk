#!/usr/bin/env python3
"""Install the Codex skill, preserving existing installations unless --force is set."""
import argparse
from datetime import datetime, timezone
import os
from pathlib import Path
import shutil
import tempfile

NAME = 'artifact-template-academic-paper-talk'
SOURCE = Path(__file__).resolve().parents[1] / 'skills' / NAME


def install(skills_dir, force=False):
    skills_dir = Path(skills_dir).expanduser().resolve()
    target = skills_dir / NAME
    if target.is_symlink():
        raise ValueError(f'Refusing to replace a symlink: {target}')
    if target.exists() and not force:
        raise FileExistsError(f'Already installed: {target}. Use --force to back up and update.')
    skills_dir.mkdir(parents=True, exist_ok=True)
    backup = None
    with tempfile.TemporaryDirectory(prefix='.paper-talk-install-', dir=skills_dir) as temp:
        staged = Path(temp) / NAME
        shutil.copytree(SOURCE, staged, ignore=shutil.ignore_patterns('__pycache__', '*.pyc', '.DS_Store'))
        if target.exists():
            stamp = datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S%fZ')
            backup = skills_dir.parent / 'skill-backups' / f'{NAME}-{stamp}'
            backup.parent.mkdir(parents=True, exist_ok=True)
            target.rename(backup)
        try:
            staged.rename(target)
        except OSError:
            if backup and not target.exists():
                backup.rename(target)
            raise
    return target, backup


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    default = Path(os.environ.get('CODEX_HOME', str(Path.home() / '.codex'))) / 'skills'
    parser.add_argument('--skills-dir', type=Path, default=default)
    parser.add_argument('--force', action='store_true')
    args = parser.parse_args()
    try:
        target, backup = install(args.skills_dir, args.force)
    except (OSError, ValueError) as error:
        parser.exit(1, f'{error}\n')
    print(f'Installed: {target}')
    if backup:
        print(f'Previous installation backed up: {backup}')


if __name__ == '__main__':
    main()
