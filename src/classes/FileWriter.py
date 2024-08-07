import json
import os


class FileWriter:
    def __init__(self, dir_name: str, file_name: str):
        self._dir_name = dir_name
        self._file_handle = open(os.path.join(dir_name, f'{file_name}.http'), 'a')

        self._env_file_name = 'http-client.env.json'
        self._env_created = False

    def __del__(self):
        self._file_handle.close()

    def append(self, data: str):
        self._file_handle.write(data)
        self._file_handle.flush()

    def write_env(self, data: dict):
        if not self._env_created:
            with open(os.path.join(self._dir_name, self._env_file_name), 'w') as env_file:
                json.dump(data, env_file, indent=2)
            self._env_created = True



