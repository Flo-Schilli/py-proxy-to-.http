from typing import Tuple, Dict

from flask import Request, Response

from src.classes.RequestHandler import RequestHandler


class Helper:
    @staticmethod
    def read_markdown(path: str) -> str:
        md_data = ''
        with open(path) as md:
            md_data = md.read()

        return md_data

    @staticmethod
    def is_valid_json(response: Response) -> bool:
        """
        Check if the given data is a valid JSON string.

        :param response: The data to be checked as a JSON string.
        :return: True if the data is a valid JSON string, False otherwise.
        """
        try:
            response.json()
            return True
        except ValueError:
            return False

    @staticmethod
    def get_identifier(request: Request) -> Tuple[str, str]:
        """
        :param request: the HTTP request object.
        :return: a tuple containing the IP address of the client and the UUID of the API proxy.

        This method returns the identifier information of the client making the HTTP request.
        It determines the client's IP address by checking the `remote_addr` property of the request.
        If the request headers contain the `X-Forwarded-For` header,
        it uses the value of that header as the IP address instead.
        The method also retrieves the UUID of the API proxy from the `X-Proxy-UUID` request header, if it exists.

        The method then returns a tuple containing the IP address and API UUID.
        The IP address is always included, but the API UUID may be an empty string if the `X-Proxy-UUID` header is not
        set.
        """
        ip = request.remote_addr
        if request.headers.get('X-Forwarded-For') is not None:
            ip = request.headers.get('X-Forwarded-For')

        api_uuid = ''
        if request.headers.get('X-Proxy-UUID') is not None:
            api_uuid = request.headers.get('X-Proxy-UUID')

        return ip, api_uuid

    @staticmethod
    def get_object(cached_objects: Dict[str, RequestHandler], request: Request) -> RequestHandler | None:
        ip, api_uuid = Helper.get_identifier(request)
        if cached_objects.get(ip) is not None:
            return cached_objects.get(ip)
        return None

    @staticmethod
    def save_object(cached_objects: Dict[str, RequestHandler], request: Request, obj: RequestHandler) -> None:
        """
        :param cached_objects: A dictionary containing cached objects.
        :param request: The request object received.
        :param obj: The CacheObject to be saved.
        :return: None

        This method saves the provided CacheObject in the cached_objects dictionary.
        If the IP address from the request object already exists in the dictionary,
        it will be removed and replaced with the new object.

        Otherwise, the new object will simply be added to the dictionary.
        """
        ip, api_uuid = Helper.get_identifier(request)

        if cached_objects.get(ip) is not None:
            cached_objects.pop(ip)

        cached_objects[ip] = obj


    @staticmethod
    def delete_object(cached_objects: Dict[str, RequestHandler], request: Request) -> None:
        """
        Deletes a cached object from the provided dictionary based on the given request.

        :param cached_objects: A dictionary containing cached objects with IP addresses as keys.
        :param request: An instance of the Request class representing the request details.
        :return: None
        """
        ip, api_uuid = Helper.get_identifier(request)

        if cached_objects.get(ip) is not None:
            cached_objects.pop(ip)
