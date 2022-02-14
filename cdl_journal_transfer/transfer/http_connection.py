import asyncio, asyncssh, json, requests

from cdl_journal_transfer.transfer.abstract_connection import AbstractConnection

class HTTPConnection(AbstractConnection):

    async def create_connection(self):
        self.conn = await asyncssh.connect(self.host, **self._connection_options())
        return self.conn


    async def run_command(self, command):
        url = f"{self.host.strip('/')}/{command.strip('/')}"
        request_opts = {
            "auth": (self.username, self.password) if self.username else None
        }
        response = requests.get(url, **request_opts)
        return json.loads(response.text)


    async def run_commands(self, *commands):
        async with conn.create_process('') as process:
            for op in commands:
                process.stdin.write(op + '\n')
                result = await process.stdout.readline()
                print(op, '=', result, end='')

    def _connection_options(self):
        opts = {
            "username": self.username,
            "password": self.password,
            "port": self.port
        }

        return { k:v for k,v in opts.items() if v is not None }
