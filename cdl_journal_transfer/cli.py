"""This module provides the CDL Journal Transfer CLI app"""
# cdl_journal_transfer/cli.py

from pathlib import Path
from typing import Optional
from enum import Enum
import getpass

import typer

from cdl_journal_transfer import __app_name__, __version__, ERRORS, config, database
from cdl_journal_transfer.transfer.transfer_handler import TransferHandler

class ConnectionType(str, Enum):
    ssh = "ssh"
    http = "http"

app = typer.Typer()
state = { "verbose": False, "test": False }

# CLI options
def build_option(required: bool = False, default = None, tag: str = "", shortcut: str = None, help: str = None, **opts):
    # Remove Nones from tags
    args = list(filter(None, [tag, shortcut]))

    return typer.Option(
        ... if required else default,
        *args,
        help=help,
        **opts
    )

def opt_data_directory(required: bool = False, default: Path = Path(typer.get_app_dir(__app_name__))):
    return build_option(
        required,
        default,
        "--data-directory",
        "--d",
        "Path to data directory location"
    )

def opt_source(required: bool = False, default: str = None, help: str = "Name of an already-defined source server to use (see define-server)"):
    return build_option(
        required,
        default,
        "--source",
        "-s",
        help
    )

def opt_target(required: bool = False, default: str = None, help: str = "Name of an already-defined target server to use (see define-server)"):
    return build_option(
        required,
        default,
        "--target",
        "-t",
        help
    )

def opt_keep(default: bool = None):
    return build_option(
        False,
        default,
        "--keep / --discard",
        "-k / -K",
        "Should the dataset from this transfer be kept? This could use a lot of disk space"
    )

def opt_keep_max(default: int = None):
    return build_option(
        False,
        default,
        "--keep-max",
        None,
        "If --keep is true, how many transfers should be kept? Older transfer will be discarded."
    )

def verbose() -> bool:
    return state["verbose"]

def test() -> bool:
    return state["test"]

# Commands
@app.command()
def init(
    data_directory: Optional[str] = opt_data_directory()
) -> None:
    """
    Initialize the application for use. Must be called first.

    This command should be called before all else.
    It creates the data directory and config file, so is required before
    any other configuration.
    """
    data_dir = config.TEST_CONFIG_DIR_PATH if test() else Path(data_directory)
    data_dir.mkdir(exist_ok=True)

    config_init_error = config.create(data_dir)
    if config_init_error:
        typer.secho(
            f'ERROR: Creating config file failed with "{ERRORS[config_init_error]}"',
            fg = typer.colors.RED
        )
        raise typer.Exit(1)
    if verbose() : typer.secho("Config file: Success!", fg=typer.colors.GREEN)

    db_init_error = database.create()
    if db_init_error:
        typer.secho(
            f'ERROR: Creating database failed with "{ERRORS[db_init_error]}"',
            fg=typer.colors.RED
        )
        raise typer.Exit(1)
    else:
        if verbose() : typer.secho("Data directory: Success!", fg=typer.colors.GREEN)
        typer.secho("\nApplication initialized!", fg=typer.colors.GREEN)
        typer.echo("\nYou can now configure the application with configure and/or define-server.\nUse flag --help for more info.\n")

@app.command()
def configure(
    data_directory: Optional[str] = opt_data_directory(default=None),
    default_source: Optional[str] = opt_source(
        help="Name of an already-defined source server to use by default (see define-server)"
    ),
    default_target: Optional[str] = opt_target(
        help="Name of an already-defined target server to use by default (see define-server)"
    ),
    keep: Optional[bool] = opt_keep(),
    keep_max: Optional[int] = opt_keep_max()
) -> None:
    """
    Apply configuration options.

    These options will be used as default values for initiate-transfer, unless different options are provided
    """
    typer.secho("Applying options", bg=typer.colors.BLUE) if verbose() else None
    config.apply_options(**locals())

    if data_directory is not None:
        database.create()


@app.command()
def define_server(
    name: str = typer.Argument(
        ...,
        help="Name of the server to create or update"
    ),
    host: str = typer.Option(
        None,
        "--host",
        "-h",
        help="The server's URL or hostname that can be used to access it from this machine"
    ),
    type: Optional[ConnectionType] = typer.Option(
        ConnectionType.http,
        "--type",
        "-t",
        help="Method that should be used to connect to the server"
    ),
    username: Optional[str] = typer.Option(
        None,
        "--user",
        "-u",
        help="Username of a user authorized to access the information"
    ),
    password: Optional[str] = typer.Option(
        None,
        "--password",
        "-p",
        help="Password of a user authorized to access the information"
    ),
    port: Optional[int] = typer.Option(
        None,
        "--port",
        help="The port to which the client should connect"
    )
) -> None:
    """
    Defines a server that can be referenced later as a source or destination.

    If NAME already exists in the config (case sensitive), this command
    will update that server rather than creating a new one.
    """
    type = type.value
    result = config.define_server(**locals())
    if ERRORS.get(result, False):
        typer.secho(f'ERROR: An error occurred: {ERRORS[result]}', fg=typer.colors.RED)
    else:
        typer.secho("Server configuration saved", fg=typer.colors.BLACK, bg=typer.colors.GREEN)
        if verbose():
            typer.echo(f'\nName: {name}')
            typer.echo(f'Type: {connection_type}')
            typer.echo(f'Host: {host}')
            if username : typer.echo(f'User: {username}')
            if password : typer.echo(f'Password: {password}')

            typer.secho(
                f'\nYou can reference this server by passing its name ({name}) as the ' +
                f'--source or --destination options of a relevant command.'
            )

@app.command()
def delete_server(
    name: str = typer.Argument(
        ...,
        help="Name of the server you wish to delete"
    ),
    force: Optional[bool] = typer.Option(
        False,
        "--force",
        "-f",
        help="Perform delete without confirmation prompt"
    )
) -> None:
    """
    Deletes a server configuration.
    """
    cfg = config.get_config()
    if cfg.has_section(name):
        if not force:
            dewit = typer.prompt("Are you sure? (y/n)")
            if not dewit == "y":
                typer.secho("Aborted!", fg=typer.colors.MAGENTA)
                raise typer.Exit(0)

        cfg.remove_section(name)
        config._write_config(cfg)
        typer.secho(f"Server '{name}' deleted.", fg=typer.colors.YELLOW)
    else:
        typer.secho(f"ERROR: Server with name '{name}' not found", fg=typer.colors.RED)

@app.command()
def get_servers() -> None:
    """
    Displays all configured servers that can be referenced as sources or targets for transfer.
    """
    defined_servers = config.get_servers()
    server_count = len(defined_servers)

    typer.secho(f'Listing {server_count} server {"entry" if server_count == 1 else "entries"}:', bg=typer.colors.BLUE)

    for index, server_def in enumerate(defined_servers):
        typer.secho(f'\n#{index + 1}', bold=True)
        for index, key in enumerate(server_def):
            value = server_def[key]
            if key == "password":
                value = "*****" if value else ""

            typer.secho(f"{key.capitalize()}: {value}")

@app.command()
def get_config() -> None:
    """
    Displays the current application configuration.
    """
    cfg = config.get_config()[config.CONFIG_SECTION]

    for key in cfg:
        value = cfg[key]
        styled_key = typer.style(key, fg=typer.colors.MAGENTA)
        typer.secho(f'{styled_key}: {value}')

@app.async_command()
async def fetch_data(
    data_directory: Optional[str] = opt_data_directory(default = config.get("data_directory")),
    source: Optional[str] = opt_source(default = config.get("default_source")),
    keep: Optional[bool] = opt_keep(default = config.get("keep")),
    keep_max: Optional[int] = opt_keep_max(default = config.get("keep_max"))
) -> None:
    """
    Fetches journal data from a source server and stores it in the data directory.
    """
    errors = []
    source_def = config.get_server(source)

    if source_def == None : errors.append(f'Source server "{source}" is not defined')

    if len(errors) > 0:
        typer.secho("\n".join(errors), fg=typer.colors.RED)
        raise typer.Exit(1)

    handler = TransferHandler(config.get("data_directory"), source=source_def)
    result = await handler.get_journals()

@app.async_command()
async def transfer_data(
    data_directory: Optional[str] = opt_data_directory(default = config.get("data_directory")),
    target: Optional[str] = opt_target(default = config.get("default_target"))
) -> None:
    """
    Puts most recently imported journal data and transfers it to a source server.
    """
    errors = []
    target_def = config.get_server(target)

    if target_def == None : errors.append(f'Target server "{target}" is not defined')

    if len(errors) > 0:
        typer.secho("\n".join(errors), fg=typer.colors.RED)
        raise typer.Exit(1)

    handler = TransferHandler(config.get("data_directory"), target=target_def)
    result = await handler.put_journals()

@app.async_command()
async def transfer(
    data_directory: Optional[str] = opt_data_directory(default = config.get("data_directory")),
    source: Optional[str] = opt_source(default = config.get("default_source")),
    target: Optional[str] = opt_target(default = config.get("default_target")),
    keep: Optional[bool] = opt_keep(default = config.get("keep")),
    keep_max: Optional[int] = opt_keep_max(default = config.get("keep_max"))
) -> None:
    """
    WIP!! Initiates a transfer.
    Where the sausage gets made.
    The real meal deal.
    Where the deals get sausaged.
    Sausage.
    """
    errors = []
    source_def = config.get_server(source)
    target_def = config.get_server(target)

    if source_def == None : errors.append(f'Source server "{source}" is not defined')
    if target_def == None : errors.append(f'Target server "{target}" is not defined')

    if len(errors) > 0:
        typer.secho("\n".join(errors), fg=typer.colors.RED)
        raise typer.Exit(1)

    typer.echo("We did it! (or, at least, we're going to pretend like we did)")

# Callbacks
def _version_callback(value: bool) -> None:
    if value:
        output = f"{__app_name__} version {__version__}" if verbose() else f"{__app_name__} v{__version__}"
        typer.echo(output)
        raise typer.Exit()

def _verbose_callback(value: bool) -> None:
    if value:
        state["verbose"] = True

def _test_callback(value: bool) -> None:
    """
    If test is true, we'll create all files in a tmp directory, then delete them after
    """
    if value:
        state["test"] = True

# Must come after all callback definitions
@app.callback()
def main(
    ctx: typer.Context,
    verbose: Optional[bool] = typer.Option(
        False,
        "--verbose",
        "-v",
        help="Enable verbose output",
        show_default=False,
        callback=_verbose_callback,
        is_eager=True
    ),
    test: Optional[bool] = typer.Option(
        False,
        "--test",
        callback=_test_callback,
        hidden=True
    ),
    version: Optional[bool] = typer.Option(
        None,
        "--version",
        help="Show the application's version and exit",
        callback=_version_callback,
        is_eager=True
    )
) -> None:
    """A CLI application for transferring journal content from one server to another."""
    state["context"] = ctx
