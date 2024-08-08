import json

from src.classes.dto.ConfigDto import DotHttpConfigDto
from src.classes.dto.QueryDto import QueryDto
from src.enum.IdeEnum import Ide


class DotHttp:
    def __init__(self, config: DotHttpConfigDto):
        self._create_dothttp_json: bool = config.create_environment
        self._auto_create_response_assertation: bool = config.create_assert
        self._ide = config.used_ide

        self._environment = config.environment
        self._headers_to_write = []
        self._headers_to_variable = {
            'authorization': 'token',
        }

    def create_dothttp_json(self, headers: dict) -> dict | None:
        """
        Create HTTP environment by extracting token from headers and saving it to a JSON file.

        :param headers: A dictionary of headers.
        :type headers: dict
        :return: dothttp JSON file.
        :rtype: str
        """

        variables = {}
        if self._create_dothttp_json:
            if headers is not None:
                for key, value in headers.items():
                    if key.lower() in self._headers_to_variable:
                        variables.update({self._headers_to_variable.get(key.lower()): value})

            if variables is not None and len(variables) > 0:
                dothttp_json = {self._environment: variables}
                return dothttp_json
            else:
                return None
        else:
            return None

    def _create_response_link(self, response_name: str | None) -> str:
        response_str = ''
        if response_name is not None:
            response_list = [
                f'',
                f'<> {response_name}',
                f'',
                f'',
            ]

            if self._ide is not Ide.INTELLIJ:
                response_list.insert(1, 'Response: ')
                response_list = [f'# {val}' for val in response_list]
                response_list.append('')

            response_str = '\n'.join(response_list)

        return response_str

    def _format_request(self, request_number: int, method: str, url: str, headers: dict | None,
                        params: dict | None, payload: dict | None, response_name: str | None) -> str:
        """
        Formats the request details into a string representation compatible with .http files.

        :param method: The HTTP method of the request.
        :param url: The URL of the request.
        :param headers: The headers of the request.
        :param params: The parameters of the request.
        :param payload: The payload of the request.
        :return: The formatted request string.
        """
        request = f'### Request {request_number}\n'

        if self._ide is not Ide.INTELLIJ:
            request += self._create_response_link(response_name)

        request += f'{method} {url}'

        if self._ide == Ide.INTELLIJ or self._ide == Ide.VISUAL_STUDIO:
            if params is not None and len(params) > 0:
                request += f'?{"&".join(["{0}={1}".format(k, v) for k, v in params.items()])}\n'
            else:
                request += '\n'

        if headers is not None:
            for key, value in headers.items():
                # Replace some defined headers with variables
                if key.lower() in self._headers_to_variable:
                    value = '{{' + self._headers_to_variable[key.lower()] + '}}'

                # Only write header if it shall be written
                if key.lower() in self._headers_to_variable or key.lower() in self._headers_to_write:
                    request += f'{key}: {value}\n'
        if payload is not None:
            request += f'Content-Type: application/json\n'

        if (params is not None and len(params) > 0 and
                not (self._ide == Ide.INTELLIJ or self._ide == Ide.VISUAL_STUDIO)):
            request += '\n'
            for key, value in params.items():
                request += f'? {key} = {value}\n'

        if payload is not None:
            request += f'\n{json.dumps(payload, indent=2)}\n'

        return request

    def _create_response_assert(self, status_code: int) -> str:
        if self._auto_create_response_assertation:
            assert_value = [
                "",
                "> {%",
                " client.test('Check response status " + str(status_code) + "', () => {",
                "     client.assert(response.status === " + str(status_code) + ", 'Response check failed');",
                " });",
                " %}",
                "",
                "",
            ]

            return '\n'.join(assert_value)
        else:
            return ''

    def _add_line_comment(self, data: str) -> str:
        return '\n'.join([f'# {str_val}' for str_val in data.split('\n')])

    def _format_response(self, status: int, headers: dict | None, payload: dict | None) -> str:
        """
        Formats the request details into a string representation compatible with .http files.

        :param status: The response status of the request.
        :param headers: The headers of the request.
        :param payload: The payload of the request.
        :return: The formatted request string.
        """
        response_dict = {'status': status, 'headers': dict(headers), 'payload': payload}
        return json.dumps(response_dict, indent=2)

    def create_dothttp_for_request(self, request_number: int, method: str, url: str, status: int,
                                   query: QueryDto, response_name: str | None) -> str:

        dothttp = ''
        dothttp += self._format_request(request_number, method, url, query.headers, query.params,
                                        query.payload, response_name)
        dothttp += self._create_response_assert(status)

        if self._ide is Ide.INTELLIJ:
            dothttp += self._create_response_link(response_name)

        return dothttp

    def create_dothttp_for_response(self, status: int, response: QueryDto) -> str:
        dothttp = ''
        dothttp += self._format_response(status, response.headers, response.payload)
        return dothttp

