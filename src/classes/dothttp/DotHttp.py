import json

from src.classes.dto.ConfigDto import DotHttpConfigDto
from src.classes.dto.QueryDto import QueryDto


class DotHttp:
    def __init__(self, config: DotHttpConfigDto):
        self._create_dothttp_json: bool = config.create_environment
        self._auto_create_response_assertation: bool = config.create_assert
        self._create_response: bool = config.create_response_comment
        self._write_params_in_url: bool = config.write_params_in_url

        self._environment = config.environment
        self._headers_to_write = []
        self._headers_to_variable = {
            'authorization': 'token',
        }

    def create_dothttp_json(self, headers: dict) -> dict:
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

            if variables is not None:
                dothttp_json = {self._environment: variables}
                return dothttp_json
            else:
                return {}
        else:
            return {}

    def _format_request(self, method: str, url: str, headers: dict | None, params: dict | None,
                        payload: dict | None) -> str:
        """
        Formats the request details into a string representation compatible with .http files.

        :param method: The HTTP method of the request.
        :param url: The URL of the request.
        :param headers: The headers of the request.
        :param params: The parameters of the request.
        :param payload: The payload of the request.
        :return: The formatted request string.
        """
        request = '### Request\n'
        request += f'{method} {url}'

        if self._write_params_in_url:
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

        if params is not None and len(params) > 0 and not self._write_params_in_url:
            request += '\n'
            for key, value in params.items():
                request += f'? {key} = {value}\n'

        if payload is not None:
            request += f'\njson({json.dumps(payload, indent=2)})\n'

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
        if self._create_response:
            comment = '\n###\n'
            response = f'Response\n\nResponse status {status}\n\n'

            if headers is not None:
                for key, value in headers.items():
                    # Write all headers
                    response += f'{key}: {value}\n'

            if payload is not None:
                response += f'\n{json.dumps(payload, indent=2)}\n'

            response += '\n\n'

            return f'{comment}{self._add_line_comment(response)}{comment}'
        else:
            return ''

    def create_dothttp_for_call(self, method: str, url: str, status: int, query: QueryDto, response: QueryDto) -> str:

        dothttp = ''
        dothttp += self._format_request(method, url, query.headers, query.params, query.payload)
        dothttp += self._create_response_assert(status)
        dothttp += self._format_response(status, response.headers, response.payload)

        return dothttp

