"""This module provides default configuration for CDL Journal Transfer"""
# cdl_journal_transfer/config.py

from configparser import ConfigParser, NoOptionError, NoSectionError
from pathlib import Path

import typer

from cdl_journal_transfer import (
    WRITE_ERROR,
    READ_ERROR,
    DIR_ERROR,
    FILE_ERROR,
    JSON_ERROR,
    SUCCESS,
    __app_name__,
    cli
)

CONFIG_DIR_PATH = Path(typer.get_app_dir(__app_name__))
CONFIG_FILE_PATH = CONFIG_DIR_PATH / "config.ini"

TEST_CONFIG_DIR_PATH = Path("./tests/tmp")
TEST_CONFIG_FILE_PATH = TEST_CONFIG_DIR_PATH / "config.ini"

CONFIG_SECTION = "config"

def get(key: str) -> str:
    try:
        return get_config().get(CONFIG_SECTION, key)
    except (NoOptionError, NoSectionError):
        return None

def get_server(server_name) -> dict:
    try:
        return get_config()[server_name]
    except KeyError:
        return None

def create(data_dir: Path) -> int:
    """Create the config file"""
    if cli.verbose() : typer.secho(f'Creating config file...')

    try:
        _config_path().touch(exist_ok=True)
        cfg = get_config()
        cfg[CONFIG_SECTION] = { "data_directory": data_dir }
        _write_config(cfg)
    except OSError:
        return FILE_ERROR

    return SUCCESS

def apply_options(**options) -> int:
    """Apply an arbitrary collection of key/value pairs to the config file"""
    cfg = get_config()

    for key, value in options.items():
        transformed_value = _transform_config_value(value)
        if transformed_value is None:
            continue
        if cli.verbose() : typer.echo(f'Applying config value "{key}" as "{transformed_value}"')
        cfg[CONFIG_SECTION][key] = transformed_value

    return _write_config(cfg)

def define_server(**server_info) -> int:
    """Saves a server configuration to config"""
    cfg = get_config()

    server_name = server_info.pop("name", None)

    if not server_name in cfg:
        cfg[server_name] = {}

    for key, value in server_info.items():
        cfg[server_name][key] = _transform_config_value(value)

    return _write_config(cfg)

def get_servers() -> list:
    cfg = get_config()
    ret = []

    for section_name in cfg.sections():
        if section_name == CONFIG_SECTION:
            continue
        else:
            section = cfg[section_name]

            ret.append({
                "name": section_name,
                "type": section.get("type"),
                "host": section.get("host"),
                "username": section.get("username"),
                "password": section.get("password")
            })
    return ret

def get_config() -> ConfigParser:
    """Fetches the current application config"""
    cfg = new_config()
    cfg.read(_config_path())
    return cfg

def new_config() -> ConfigParser:
    """Builds a new, empty ConfigParser"""
    return ConfigParser(allow_no_value=True)

def _config_path() -> Path:
    return TEST_CONFIG_FILE_PATH if cli.test() else CONFIG_FILE_PATH

def _transform_config_value(value: str) -> str:
    """Transforms config values, as needed"""
    return (str(value) if value is not None else None)

def _init_config_file(data_dir: Path) -> int:
    """
    Creates the config file.

    Must be run before any other config functions will work.
    """
    try:
        _config_path().touch(exist_ok=True)
        cfg = get_config()
        cfg[CONFIG_SECTION] = { "data_directory": data_dir }
        _write_config(cfg)
    except OSError:
        return FILE_ERROR

    return SUCCESS

def _write_config_value(key, value, section=CONFIG_SECTION) -> int:
    """Writes a single value to the config"""
    config_parser = get_config()
    config_parser[section][key] = value

    return _write_config(config_parser)

def _write_config(config_parser) -> int:
    """Writes the contents of a ConfigParser to the disk"""
    try:
        with _config_path().open("w") as file:
            config_parser.write(file)
    except OSError:
        return WRITE_ERROR

    return SUCCESS
