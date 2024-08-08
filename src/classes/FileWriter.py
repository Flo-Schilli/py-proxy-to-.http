import json
import os


class FileWriter:
    def __init__(self, dir_name: str, uuid: str):
        self._dir_name = dir_name
        self._uuid = uuid
        self._file_handle = open(os.path.join(dir_name, f'{uuid}.http'), 'a')

        self._response_dir = 'response'
        self._env_file_name = 'http-client.env.json'
        self._env_created = False

        # Create the response directory
        os.makedirs(os.path.join(self._dir_name, self._response_dir), exist_ok=True)

    def __del__(self):
        self._file_handle.close()

    def response_name(self, request_number: int) -> str:
        return os.path.join(self._response_dir, f'{self._uuid}.{request_number}.json')

    def request_append(self, data: str):
        self._file_handle.write(data)
        self._file_handle.flush()

    def create_response(self, request_number: int, data: str):
        path = os.path.join(self._dir_name, self.response_name(request_number))
        with open(path, 'w') as res:
            res.write(data)
            res.flush()

    def write_env(self, data: dict):
        if not self._env_created:
            with open(os.path.join(self._dir_name, self._env_file_name), 'w') as env_file:
                json.dump(data, env_file, indent=2)
            self._env_created = True



