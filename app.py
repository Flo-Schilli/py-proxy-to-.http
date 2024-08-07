import os
from typing import Dict

import markdown
from flask import Flask, request, send_file, Response


import requests
from requests import RequestException

from src.classes.Zip import Zip
from src.classes import RequestHandler
from src.classes.RequestHandler import RequestHandler
from src.classes.dto.ConfigDto import ConfigDto
from src.classes.dto.QueryDto import QueryDto
from src.classes.helpers.Helper import Helper

app = Flask(__name__)

in_memory_cache: Dict[str, RequestHandler] = {}

md = Helper.read_markdown(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'README.md'))


@app.route('/', methods=["GET"])
def home():
    return markdown.markdown(md)


@app.route('/config/start', methods=["POST"])
def start():
    data: ConfigDto = ConfigDto.from_dict(request.get_json())

    if data is not None and data.base_url is not None:
        ip = request.remote_addr
        if data.ip is not None:
            ip = data.ip

        cache = RequestHandler(data)
        Helper.save_object(cached_objects=in_memory_cache, request=request, obj=cache)

        return Response(status=200, response=str(cache.uuid))
    else:
        return Response(status=404, response='Base URL not provided')


@app.route('/config/stop', methods=["GET"])
def download():
    cache = Helper.get_object(cached_objects=in_memory_cache, request=request)

    if cache is not None:
        data = send_file(
            Zip.zip_file(cache.storage_path),
            mimetype='application/zip',
            download_name='Requests.zip'
        )

        Helper.delete_object(cached_objects=in_memory_cache, request=request)
        return data
    else:
        return Response(status=200)


@app.route('/proxy/', defaults={'path': ''}, methods=["GET", "POST", "PATCH", "DELETE"])
@app.route('/proxy/<path:path>', methods=["GET", "POST", "PATCH", "DELETE"])
def proxy(path) -> Response:

    if request.headers.get('Authorization') is not None:
        headers = {'Authorization': request.headers.get('Authorization')}
    else:
        headers = {}

    cache = Helper.get_object(cached_objects=in_memory_cache, request=request)
    if cache is None:
        return Response(status=404, response='Logging was not started before')

    url = f'{cache.base_url}/{path}'

    query = QueryDto(headers, request.args, request.get_json(silent=True))

    response: Response | None = None
    try:
        if request.method == "GET":
            response = requests.get(url, params=query.params, headers=query.headers)
        elif request.method == "POST":
            response = requests.post(url, params=query.params, headers=query.headers, json=query.payload)
        elif request.method == "PATCH":
            response = requests.patch(url, params=query.params, headers=query.headers, json=query.payload)
        elif request.method == "DELETE":
            response = requests.delete(url, params=query.params, headers=query.headers)
        else:
            return Response(status=405, response='Method not supported')
    except RequestException as e:
        return Response(status=500, response=str(e))

    response_data = None
    if Helper.is_valid_json(response):
        response_data = response.json()

    return_data = QueryDto(response.headers, None, response_data)

    cache.create_environment(query.headers)
    cache.write(request.method, url, response.status_code, query, return_data)

    if response is not None:
        if not response.content:
            return Response(status=response.status_code)

        custom_response = Response(response.content, status=response.status_code)

        if 'Content-Type' in response.headers:
            custom_response.headers['Content-Type'] = response.headers['Content-Type']

        return custom_response


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
