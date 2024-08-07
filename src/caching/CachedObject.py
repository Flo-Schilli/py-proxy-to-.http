import io
import os
import tempfile
import uuid
import zipfile


from src.FileWriter import FileWriter


class CacheObject:
    def __init__(self, remote_addr: str, base_url: str):
        self._remote_addr = remote_addr
        self._base_url = base_url
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

    def zip_file(self) -> io.BytesIO:
        data = io.BytesIO()

        with zipfile.ZipFile(data, mode='w') as z:
            for file_name in os.listdir(self._storage_path.name):
                absolute_path = os.path.join(self._storage_path.name, file_name)
                relative_path = os.path.relpath(absolute_path, self._storage_path.name)
                z.write(absolute_path, arcname=relative_path)

        data.seek(0)

        return data

    def write_request(self, method: str, url: str, headers: dict, params: dict = None, payload: dict = None) -> None:
        self._file.req_write(method, url, headers, params, payload)

    def write_response(self, method: str, url: str, headers: dict, params: dict = None, payload: dict = None, status: int = None) -> None:
        self._file.res_write(method, url, headers, params, payload, status)
