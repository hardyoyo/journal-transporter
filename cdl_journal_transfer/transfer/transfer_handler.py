"""Interface for handling journal transfers from source to target servers"""
# cdl_journal_transfer/transfer/handler.py

import asyncio, asyncssh, json

from pathlib import Path

from cdl_journal_transfer.transfer.http_connection import HTTPConnection
from cdl_journal_transfer.transfer.ssh_connection import SSHConnection


class TransferHandler:

    SERVER_OPTION_KEYS = ["port", "username", "password"]

    def __init__(self, data_directory: str, source: dict = None, target: dict = None, **options):
        self.data_directory = data_directory
        self.source = source
        self.target = target
        self.options = options
        self.source_connection = self.connection_class(source)(**self.source) if source is not None else None
        self.target_connection = self.connection_class(target)(**self.target) if target is not None else None


    def get_data_dir(self, *path_segments) -> Path:
        path = (Path(self.data_directory) / "current")

        for segment in path_segments:
            path = path / segment
            path.mkdir(exist_ok=True)
            index_file = (path / "index.json")
            index_file.touch(exist_ok=True)

        return path


    async def get(self, record_name, **filters) -> None:
        if self.source is None : return

        data_dir = self.get_data_dir(record_name)
        response = await self.source_connection.run_command(record_name)

        with open(data_dir / "index.json", "w") as f:
            f.write(json.dumps(response, indent=2))


    async def put(self, record_name, data=None) -> None:
        if self.target is None : return

        if data is None:
            data_dir = self.get_data_dir(record_name)
            with open(data_dir / "index.json") as f:
                data = json.loads(f.read())

        response = await self.target_connection.put_data("journals", data)


    def connection_class(self, server_def):
        if server_def["type"] == "ssh":
            return SSHConnection
        elif server_def["type"] == "http":
            return HTTPConnection


    ## Convenience methods

    async def get_journals(self) -> None:
        await self.get("journals")


    async def put_journals(self) -> None:
        await self.put("journals")
