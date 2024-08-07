import json
import os
from typing import Dict

import markdown
from dotenv import load_dotenv
from flask import Flask, Response, request, send_file

import requests
from src.caching import CachedObject
from src.caching.CachedObject import CacheObject
from src.dto.StartDTO import StartDto

from src.helpers.Helper import Helper

app = Flask(__name__)

in_memory_cache: Dict[str, CachedObject] = {}

md = Helper.read_markdown(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'README.md'))


@app.route('/', methods=["GET"])
def home():
    return markdown.markdown(md)


@app.route('/config/start', methods=["POST"])
def start():
    data: StartDto = StartDto.from_dict(request.get_json())

    if data is not None and data.base_url is not None:
        ip = request.remote_addr
        if data.ip is not None:
            ip = data.ip

        cache = CacheObject(ip, data.base_url)
        Helper.save_object(cached_objects=in_memory_cache, request=request, obj=cache)

        return Response(status=200, response=str(cache.uuid))
    else:
        return Response(status=404, response='Base URL not provided')


@app.route('/config/stop', methods=["GET"])
def download():
    cache = Helper.get_object(cached_objects=in_memory_cache, request=request)

    if cache is not None:
        data = send_file(
            cache.zip_file(),
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

    cache.write_request(request.method, url, headers, request.args, request.get_json(silent=True))

    if request.method == "GET":
        response = requests.get(url, params=request.args, headers=headers)
    elif request.method == "POST":
        response = requests.post(url, params=request.args, headers=headers, json=request.get_json())
    elif request.method == "PATCH":
        response = requests.patch(url, params=request.args, headers=headers, json=request.get_json())
    elif request.method == "DELETE":
        response = requests.delete(url, params=request.args, headers=headers)

    response_data = None
    if Helper.is_valid_json(response):
        response_data = response.json()

    cache.write_response(request.method, url, response.headers, request.args, response_data, response.status_code)

    if not response.content:
        return Response(status=response.status_code)
    else:
        custom_response = Response(response.content, status=response.status_code)
        custom_response.headers['Content-Type'] = response.headers['Content-Type']
        return custom_response


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
