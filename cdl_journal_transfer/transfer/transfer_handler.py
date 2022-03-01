"""Interface for handling journal transfers from source to target servers"""
# cdl_journal_transfer/transfer/handler.py

import asyncio, json, uuid, inspect

from pathlib import Path
from datetime import datetime

from cdl_journal_transfer import __version__

from cdl_journal_transfer.transfer.http_connection import HTTPConnection
from cdl_journal_transfer.transfer.ssh_connection import SSHConnection


class TransferHandler:

    SERVER_OPTION_KEYS = ["port", "username", "password"]

    def __init__(self, data_directory: str, source: dict = None, target: dict = None, **options):
        self.data_directory = Path(data_directory) / "current"
        self.source = source
        self.target = target
        self.options = options
        self.source_connection = self.__connection_class(source)(**self.source) if source is not None else None
        self.target_connection = self.__connection_class(target)(**self.target) if target is not None else None

        self.uuid = uuid.uuid1()
        self.initialize_data_directory()


    def initialize_data_directory(self):
        file = self.data_directory / "index.json"
        file.touch()
        now = datetime.now()

        content = {
            "application": "CDL Journal Transfer",
            "version": __version__,
            "initiated": now.strftime("%Y/%m/%d at %H:%M:%S"),
            "transaction_id": str(self.uuid)
        }

        open(file, "w").write(json.dumps(content))


    def fetch_data(self, journal_paths, progress_reporter) -> None:
        self.progress_reporter = progress_reporter
        self.progress_reporter.update(0)

        self.__fetch_journal_index(journal_paths)
        self.__fetch_all_journals()


    def put_data(self) -> None:
        pass


    ## Private

    ## Connection handlers

    def __do_fetch(self, api_path, file, **args) -> None:
        if self.source is None : return

        response = self.source_connection.get(api_path)
        self.__assign_uuids(response)
        data = json.dumps(response, indent=2)

        with open(file, "w") as f:
            f.write(data)

        return data


    async def __do_put(self, record_name, data=None) -> None:
        if self.target is None : return

        if data is None:
            data_dir = self.get_data_dir(record_name)
            with open(data_dir / "index.json") as f:
                data = json.loads(f.read())

        response = await self.target_connection.put_data("journals", data)


    def __connection_class(self, server_def):
        if server_def["type"] == "ssh":
            return SSHConnection
        elif server_def["type"] == "http":
            return HTTPConnection


    ## Sausage makers

    def __fetch_journal_index(self, journal_paths) -> None:
        """
        Gets basic journal metadata from source /journals endpoint
        """
        dir_path = self.data_directory / "journals"
        dir_path.mkdir(exist_ok=True)
        target_file_path = self.data_directory / "journals" / "index.json"
        target_file_path.touch(exist_ok=True)

        self.__do_fetch("journals", target_file_path)


    def __fetch_all_journals(self):
        """
        Fetches data for all journals present in journals/index.js
        """
        with open(self.data_directory / "journals" / "index.json") as f:
            journal_index = json.loads(f.read())

        self.journal_count = len(journal_index)

        for index, journal in enumerate(journal_index):
            self.progress_reporter.update(message=f"Importing journal {journal['title']}")
            self.__fetch_journal(journal)
            self.progress_reporter.update((1 / self.journal_count) * 100)


    def __fetch_journal(self, journal: dict):
        """
        Fetches data for a provided journal stub
        """
        self.current_journal_path = self.data_directory / "journals" / journal["uuid"]
        dir = self.current_journal_path.mkdir()
        file = self.current_journal_path / "journal.json"
        file.touch()

        self.current_journal_source_id = journal["source_record_key"].split(":")[-1]
        self.__do_fetch(f"journals/{self.current_journal_source_id}", file)



    #     self.__fetch_issues(journal)
    #     self.__fetch_submissions(journal)
    #     self.__fetch_users(journal)
    #
    #
    # def __fetch_issues(self, journal: dict):
    #     """
    #     Fetches issues for a journal
    #     """
    #     path = self.current_journal_path / "issues"
    #     dir = path.mkdir()
    #     file = path / "index.json"
    #     file.touch()
    #
    #     self.__do_fetch(f"journals/{journal_id}/issues", file)
    #
    # def __fetch_users(self, journal):
    #     """
    #     Fetches data for all users for each journal present in journals/index.js
    #     """
    #     path = self.data_directory / "users"
    #     dir = path.mkdir(exists_ok=True)




    ## Utilities

    def __assign_uuids(self, json):
        if type(json) is list:
            for entry in json:
                self.__assign_uuids(entry)
        elif json["source_record_key"]:
            json["uuid"] = str(uuid.uuid5(self.uuid, json["source_record_key"]))
