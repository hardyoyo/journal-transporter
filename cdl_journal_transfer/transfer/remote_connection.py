import asyncio, asyncssh, json

class RemoteConnection:

    def __init__(self, **options):
        self.host = options["host"]
        self.username = options["username"]
        self.password = options["password"]
        self.port = int(options["port"]) if options["port"] is not None else None


    async def create_connection(self):
        self.conn = await asyncssh.connect(self.host, **self._connection_options())
        return self.conn


    async def run(self, command):
        conn = self.conn if hasattr(self, "conn") else await self.create_connection()
        response = await conn.run(command)
        return json.loads(response.stdout)


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
