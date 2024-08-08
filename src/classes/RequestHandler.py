import tempfile
import uuid

from src.classes.FileWriter import FileWriter
from src.classes.dothttp.DotHttp import DotHttp
from src.classes.dto.ConfigDto import ConfigDto
from src.classes.dto.QueryDto import QueryDto


class RequestHandler:
    def __init__(self, config: ConfigDto):
        self._remote_addr = config.ip
        self._base_url = config.base_url
        self._dothttp = DotHttp(config.dothttp)

        self._uuid = uuid.uuid4()
        self._storage_path = tempfile.TemporaryDirectory()
        self._request_number = 0
        self._file = FileWriter(dir_name=self._storage_path.name, uuid=str(self._uuid))

    def __del__(self):
        self._storage_path.cleanup()

    @property
    def uuid(self) -> uuid.UUID:
        return self._uuid

    @property
    def base_url(self) -> str:
        return self._base_url

    @property
    def storage_path(self) -> tempfile.TemporaryDirectory:
        return self._storage_path

    def write(self, method: str, url: str, status: int, query: QueryDto, response: QueryDto):
        self._request_number += 1

        response_name = self._file.response_name(self._request_number)
        dothttp = self._dothttp.create_dothttp_for_request(self._request_number, method, url, status,
                                                           query, response_name)
        self._file.request_append(dothttp)

        self._file.create_response(self._request_number, self._dothttp.create_dothttp_for_response(status, response))

    def create_environment(self, headers: dict):
        dothttp = self._dothttp.create_dothttp_json(headers)
        if dothttp is not None:
            self._file.write_env(dothttp)
