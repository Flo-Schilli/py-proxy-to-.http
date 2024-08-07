import json
import os
from datetime import datetime


class FileWriter:
    def __init__(self, dir_name: str, file_name: str):
        self._dir_name = dir_name
        self._request_file_handle = open(os.path.join(dir_name, f'{file_name}.request.http'), 'a')
        self._response_file_handle = open(os.path.join(dir_name, f'{file_name}.response.http'), 'a')

        self._env_created = False

    def __del__(self):
        self._request_file_handle.close()
        self._response_file_handle.close()

    def __req_format(self, method: str, url: str, headers: dict | None, params: dict | None, payload: dict | None,
                     status: int | None = None) -> str:
        """
        Formats the request details into a string representation compatible with .http files.

        :param method: The HTTP method of the request.
        :param url: The URL of the request.
        :param headers: The headers of the request.
        :param params: The parameters of the request.
        :param payload: The payload of the request.
        :return: The formatted request string.
        """
        request = f'{method} {url}'

        if params is not None and len(params) > 0:
            request += f'?{"&".join(["{0}={1}".format(k, v) for k, v in params.items()])}\n'
        else:
            request += '\n'

        if status is not None:
            request += f'Response code: {status}\n\n'

        if headers is not None:
            for key, value in headers.items():
                if key.lower() == 'authorization':
                    method = value.split(' ')[0]
                    value = method + ' {{token}}'

                request += f'{key}: {value}\n'

        if payload is not None:
            request += '\n' + json.dumps(payload, indent=2) + '\n'

        return request

    def __add_next_request(self, data: str) -> str:
        data += '\n###\n'
        return data

    def __surround_with_comment(self, data: str) -> str:
        return f'<!--\n{data}\n-->'

    def __create_http_env(self, headers: dict):
        """
        Create HTTP environment by extracting token from headers and saving it to a JSON file.

        :param headers: A dictionary of headers.
        :type headers: dict
        :return: None
        :rtype: None
        """
        if not self._env_created:
            token = None
            if headers is not None:
                for key, value in headers.items():
                    if key.lower() == 'authorization':
                        token = value.split(' ')[1]

            if token is not None:
                env = {'dev': {'token': token}}

                with open(os.path.join(self._dir_name, f'http-client.env.json'), 'w') as env_file:
                    json.dump(env, env_file, indent=2)
                self._env_created = True

    def req_write(self, method: str, url: str, headers: dict, params: dict = None, payload: dict = None):
        self.__create_http_env(headers)

        self._request_file_handle.write(self.__add_next_request(
            self.__req_format(method, url, headers, params, payload)))
        self._request_file_handle.flush()

    def res_write(self, method: str, url: str, headers: dict, params: dict = None, payload: dict = None, status: int = None):
        """
        Writes the response of the API Query

        :param method: The HTTP method to be used for the request
        :param url: The URL to which the request will be made
        :param headers: A dictionary of headers to be sent with the request
        :param params: (Optional) A dictionary of URL parameters to be encoded and sent with the request
        :param payload: (Optional) A dictionary of payload data to be sent as the request body
        :param status: (Optional) The status code to be returned in the response

        :return: None

        """
        self._response_file_handle.write(
            self.__add_next_request(
                self.__surround_with_comment(
                    self.__req_format(method, url, headers, params, payload, status))))
        self._response_file_handle.flush()
