import asyncio, asyncssh, json

from abc import ABC, abstractmethod

class AbstractConnection(ABC):

    def __init__(self, **options):
        self.host = options["host"]
        self.username = options["username"]
        self.password = options["password"]
        self.options = { k: options[k] for k in options if k not in ["host", "username", "password"] }
        self.setup()

    def setup(self):
        pass

    @abstractmethod
    def run_command(self, command):
        pass
