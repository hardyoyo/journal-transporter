import textwrap
import urllib.parse


class ServerResponseError(Exception):
    def __init__(self, message, response):
        super().__init__(message)
        self.message = message
        self.response = response
        self.url = urllib.parse.urlparse(response.url)
        self.full_message = self.__build_full_message()

    def __build_full_message(self):
        return textwrap.dedent(f"""\
        The server at {self.url.netloc} has returned an error response.

        {self.message}
        """)


class AbortError(Exception):
    pass
