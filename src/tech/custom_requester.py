import json
import uuid
import warnings

import allure
import requests
import urllib3
from requests import HTTPError, Response
from urllib3.exceptions import InsecureRequestWarning

from src.tech.custom_logger import log_request, log_error, log_response, log_info

HTTP_METHODS = ("GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS")
DEFAULT_TIMEOUT = 30
MIN_CLIENT_ERROR_CODE = 400  # 4xx errors start at 400
MAX_SERVER_ERROR_CODE = 599  # 5xx errors end at 599


class CustomRequester:
    """Класс-обёртка для работы с HTTP-запросами и логированием"""

    def __init__(self, base_url: str, timeout=DEFAULT_TIMEOUT):
        self.base_url = base_url
        self.timeout = timeout
        self.session = requests.Session()
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)  # Для интернал вылетает ошибка про сертификат
        warnings.filterwarnings("ignore", category=InsecureRequestWarning)

    def close(self):
        self.session.close()
        log_info("Session closed")

    def _send_request(
        self, method: str, endpoint: str, data=None, headers: dict = None, params=None, use_allure: bool = True, **kwargs
    ) -> Response:
        """Универсальный метод для отправки HTTP-запросов."""
        if method.upper() not in HTTP_METHODS:
            err_msg = f"Недопустимый HTTP-метод: {method}. Допустимые значения: {HTTP_METHODS}"
            raise ValueError(err_msg)

        request_id = str(uuid.uuid4())
        url = f"{self.base_url}{endpoint}"
        combined_headers = {**headers}

        log_request(request_id, method, url, headers=combined_headers, params=params, data=data, **kwargs)

        try:
            response = self.session.request(
                method=method, url=url, headers=combined_headers, params=params, data=data, timeout=self.timeout, verify=False, **kwargs
            )
        except Exception as e:
            self._add_request_attachments(method, url, headers, data, params)
            exception_name = e.__class__.__name__
            err_msg = f"исключение при {method.upper()} запросе {endpoint}:\n{e}"
            log_error(request_id, f"{exception_name} {err_msg}", None, data, combined_headers, url, method)
            raise e.__class__(err_msg) from e

        log_response(request_id, response)

        if use_allure:
            self._add_request_attachments(method, url, response.request.headers, data, params)
            self._add_response_attachments(response)

        if MIN_CLIENT_ERROR_CODE <= response.status_code < MAX_SERVER_ERROR_CODE:
            try:
                response.raise_for_status()
            except HTTPError as e:
                exception_name = e.__class__.__name__
                log_error(request_id, f"{exception_name}: {e}", response, data, combined_headers, url, method)

        return response

    def get(self, endpoint: str, headers: dict = None, params=None, use_allure=True, **kwargs) -> Response:
        return self._send_request("GET", endpoint, use_allure=use_allure, headers=headers, params=params, **kwargs)

    def post(self, endpoint: str, data=None, headers: dict = None, use_allure=True, **kwargs) -> Response:
        return self._send_request("POST", endpoint, use_allure=use_allure, data=data, headers=headers, **kwargs)

    def put(self, endpoint: str, data=None, headers: dict = None, use_allure=True, **kwargs) -> Response:
        return self._send_request("PUT", endpoint, use_allure=use_allure, data=data, headers=headers, **kwargs)

    def patch(self, endpoint: str, data=None, headers: dict = None, use_allure=True, **kwargs) -> Response:
        return self._send_request("PATCH", endpoint, use_allure=use_allure, data=data, headers=headers, **kwargs)

    def delete(self, endpoint: str, headers: dict = None, use_allure=True, **kwargs) -> Response:
        return self._send_request("DELETE", endpoint, use_allure=use_allure, headers=headers, **kwargs)

    def options(self, endpoint: str, headers: dict = None, use_allure=True, **kwargs) -> Response:
        return self._send_request("OPTIONS", endpoint, use_allure=use_allure, headers=headers, **kwargs)

    @staticmethod
    def _add_response_attachments(response):
        allure.attach(name="Response status code", body=f"{response.status_code}", attachment_type=allure.attachment_type.TEXT)
        allure.attach(
            name="Response Headers", body=json.dumps(dict(response.headers), indent=2), attachment_type=allure.attachment_type.JSON
        )
        if response.text:
            try:
                json_data = response.json()
                allure.attach(name="Response body", body=json.dumps(json_data, indent=2), attachment_type=allure.attachment_type.JSON)
            except ValueError:
                allure.attach(name="Response body", body=response.text, attachment_type=allure.attachment_type.TEXT)

    @staticmethod
    def _add_request_attachments(method, url, headers, data, params):
        allure.attach(name="Request", body=f"{method} {url}", attachment_type=allure.attachment_type.TEXT)
        allure.attach(body=json.dumps(dict(headers), indent=2), name="Request headers", attachment_type=allure.attachment_type.JSON)
        if data:
            try:
                if isinstance(data, str):
                    data = json.loads(data)

                # Пробуем преобразовать в JSON
                json_data = json.dumps(data, indent=2)
                allure.attach(name="Request body", body=json_data, attachment_type=allure.attachment_type.JSON)
            except TypeError:
                allure.attach(name="Request body", body=str(data), attachment_type=allure.attachment_type.TEXT)

        if params:
            allure.attach(name="Request params", body=json.dumps(params, indent=2), attachment_type=allure.attachment_type.JSON)
