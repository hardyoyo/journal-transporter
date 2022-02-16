import asyncio, asyncssh, json, requests

from cdl_journal_transfer.transfer.abstract_connection import AbstractConnection

class HTTPConnection(AbstractConnection):

    async def get_data(self, command):
        url = f"{self.host.strip('/')}/{command.strip('/')}"
        request_opts = self.credentials()
        response = requests.get(url, **request_opts)
        return json.loads(response.text)


    async def put_data(self, path, data):
        url = f"{self.host.strip('/')}/{path.strip('/')}/"
        request_opts = self.credentials()
        if type(data) is list:
            for index, record in enumerate(data):
                response = requests.post(url, json=record, **request_opts)
        else:
            requests.post(url, json=data, **request_opts)


    def credentials(self):
        if self.username is None : return {}
        return { "auth": (self.username, self.password) }
