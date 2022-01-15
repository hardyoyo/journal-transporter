"""This module provides access to the data directory"""
# cdl_journal_transfer/database.py

import configparser
from pathlib import Path
import shutil

import typer

from cdl_journal_transfer import WRITE_ERROR, SUCCESS, __app_name__, config, cli

def get_database_path() -> Path:
    """Return the current path to the data directory"""
    return config.get("data_directory")

def create() -> int:
    """Create the data directory"""
    db_path = Path(get_database_path())

    try:
        styled_data_dir = typer.style(str(db_path), fg=typer.colors.YELLOW)
        if cli.verbose() : typer.secho(f'Creating data directory at {styled_data_dir}')

        db_path.mkdir(exist_ok=True)
        (db_path / "data").mkdir(exist_ok=True)

        # Remove the "current" directory and remake it
        current_dir = db_path / "current"
        if current_dir.is_symlink():
            current_dir.unlink()
        elif current_dir.is_dir():
            shutil.rmtree(current_dir)

        current_dir.mkdir()

        return SUCCESS
    except OSError:
        return WRITE_ERROR
