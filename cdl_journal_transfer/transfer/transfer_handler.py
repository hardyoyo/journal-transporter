"""Interface for handling journal transfers from source to target servers"""
# cdl_journal_transfer/transfer/handler.py

import asyncio, asyncssh

from pathlib import Path

class TransferHandler:

    SERVER_OPTION_KEYS = ["port", "username", "password"]

    def __init__(self, data_directory: str, source: dict = None, target: dict = None, **options):
        self.data_directory = data_directory
        self.source = source
        self.target = target
        self.options = options

    async def get_journals(self):
        if self.source is None : return
        if not hasattr(self, "source_conn") : await self._connect_source()

        result = await self.source_conn.run("ojs-cli /journals")

        journal_dir = (Path(self.data_directory) / "current" / "journals")
        journal_dir.mkdir(exist_ok=True)
        index_file = (journal_dir / "index.json")
        index_file.touch(exist_ok=True)

        with open(index_file, "w") as f:
            f.write(result.stdout)

    async def _connect_source(self):
        self.source_conn = await asyncssh.connect(self.source["host"], **self._connection_options_for(self.source))

    async def _connect_target(self):
        self.target_conn = await asyncssh.connect(self.source["host"], **self._connection_options_for(self.target))

    def _connection_options_for(self, server_def):
        unfiltered = { key: server_def[key] for key in self.SERVER_OPTION_KEYS }
        filtered = { k:v for k,v in unfiltered.items() if v is not None }
        if filtered["port"] is not None : filtered["port"] = int(filtered["port"])
        return filtered
