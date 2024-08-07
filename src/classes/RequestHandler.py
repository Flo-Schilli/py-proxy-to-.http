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
        self._file = FileWriter(dir_name=self._storage_path.name, file_name=str(self._uuid))

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

        dothttp = self._dothttp.create_dothttp_for_call(method, url, status, query, response)
        self._file.append(dothttp)

    def create_environment(self, headers: dict):
        dothttp = self._dothttp.create_dothttp_json(headers)
        self._file.write_env(dothttp)
