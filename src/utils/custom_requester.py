import json
import uuid
import warnings

import allure
import requests
import urllib3
from requests import HTTPError, Response
from urllib3.exceptions import InsecureRequestWarning

from config import DEFAULT_TIMEOUT, MAX_SERVER_ERROR_CODE, MIN_CLIENT_ERROR_CODE
from src.utils.custom_logger import logger, log
from src.utils.decorators import validate_http_method, add_allure_attachments, handle_request_exceptions


class CustomRequester:
    """Класс-обёртка для работы с HTTP-запросами и логированием"""

    def __init__(self, base_url: str, timeout=DEFAULT_TIMEOUT):
        self.base_url = base_url
        self.timeout = timeout
        self.session = requests.Session()
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
        warnings.filterwarnings("ignore", category=InsecureRequestWarning)

    def close(self):
        self.session.close()
        logger.log_info("Session closed")

    @validate_http_method
    @add_allure_attachments
    @handle_request_exceptions(logger)
    def _send_request(self, method: str, endpoint: str, use_allure: bool = True, **kwargs) -> Response:
        """Универсальный метод для отправки HTTP-запросов."""
        kwargs.setdefault('timeout', self.timeout)
        kwargs.setdefault('verify', False)
        data = kwargs.get("data", None)
        request_id = kwargs.get("headers", {}).get("requestId", str(uuid.uuid4()))

        url = f"{self.base_url}{endpoint}"

        logger.log_request(request_id, method, url, **kwargs)

        response = self.session.request(method=method, url=url, **kwargs)

        logger.log_response(request_id, response)

        if MIN_CLIENT_ERROR_CODE <= response.status_code < MAX_SERVER_ERROR_CODE:
            try:
                response.raise_for_status()
            except HTTPError as e:
                exception_name = e.__class__.__name__
                logger.log_error(request_id, f"{exception_name}: {e}", response, data, response.request.headers, url, method)

        return response

    def _check_server_alive(self):
        """Проверяет, доступен ли сервер по base_url с помощью HEAD-запроса. Если HEAD не поддерживается (405), пробует OPTIONS."""
        try:
            response = self.session.head(self.base_url, timeout=self.timeout, verify=False)
            if response.status_code == 405 or response.status_code == 404:
                # HEAD не поддерживается, пробуем OPTIONS
                log.info(f"HEAD не поддерживается, вызываем OPTIONS для {self.base_url}")
                response = self.session.options(self.base_url, timeout=self.timeout, verify=False)
            if not (200 <= response.status_code < 400):
                logger.log_error(
                    str(uuid.uuid4()),
                    f"Проверочный запрос к {self.base_url} вернул статус {response.status_code}",
                    response,
                    None,
                    response.request.headers if hasattr(response, 'request') else {},
                    self.base_url,
                    response.request.method if hasattr(response, 'request') else "HEAD/OPTIONS"
                )
                raise ConnectionError(f"Сервер недоступен: {response.request.method if hasattr(response, 'request') else 'HEAD/OPTIONS'} {self.base_url} -> {response.status_code}")
        except requests.exceptions.RequestException as e:
            logger.log_error(str(uuid.uuid4()), f"Ошибка при проверке сервера: {e}", None, None, {}, self.base_url, "HEAD/OPTIONS")
            raise ConnectionError(f"Сервер недоступен: {e}")

    def clear_cookies(self):
        """Очищает все куки в текущей сессии"""
        self.session.cookies.clear()

    def add_cookie(self, cookie):
        """Добавить куки к существующим"""
        if isinstance(cookie, dict):
            for key, value in cookie.items():
                self.session.cookies.set(key, value)
        elif isinstance(cookie, requests.cookies.RequestsCookieJar):
            self.session.cookies.update(cookie)
        else:
            raise TypeError("cookie должен быть словарем или RequestsCookieJar")

    def get(self, endpoint: str, use_allure=True, **kwargs) -> Response:
        self._check_server_alive()
        return self._send_request("GET", endpoint, use_allure, **kwargs)

    def post(self, endpoint: str, use_allure=True, **kwargs) -> Response:
        self._check_server_alive()
        return self._send_request("POST", endpoint, use_allure, **kwargs)

    def put(self, endpoint: str, use_allure=True, **kwargs) -> Response:
        self._check_server_alive()
        return self._send_request("PUT", endpoint, use_allure, **kwargs)

    def patch(self, endpoint: str, use_allure=True, **kwargs) -> Response:
        self._check_server_alive()
        return self._send_request("PATCH", endpoint, use_allure, **kwargs)

    def delete(self, endpoint: str, use_allure=True, **kwargs) -> Response:
        self._check_server_alive()
        return self._send_request("DELETE", endpoint, use_allure, **kwargs)

    def options(self, endpoint: str, use_allure=True, **kwargs) -> Response:
        return self._send_request("OPTIONS", endpoint, use_allure, **kwargs)

    def head(self, endpoint: str, use_allure=True, **kwargs) -> Response:
        return self._send_request("HEAD", endpoint, use_allure, **kwargs)

    def trace(self, endpoint: str, use_allure=True, **kwargs) -> Response:
        return self._send_request("TRACE", endpoint, use_allure, **kwargs)

    def connect(self, endpoint: str, use_allure=True, **kwargs) -> Response:
        return self._send_request("CONNECT", endpoint, use_allure, **kwargs)

    @staticmethod
    def _add_response_attachments(response):
        allure.attach(name="Response status code", body=f"{response.status_code}", attachment_type=allure.attachment_type.TEXT)
        allure.attach(
            name="Response Headers", body=json.dumps(dict(response.headers), indent=2), attachment_type=allure.attachment_type.JSON
        )
        if response.cookies:
            cookies_dict = {cookie.name: cookie.value for cookie in response.cookies}
            allure.attach(name="Response Cookies", body=json.dumps(cookies_dict, indent=2), attachment_type=allure.attachment_type.JSON)
        if response.text:
            try:
                json_data = response.json()
                allure.attach(name="Response body", body=json.dumps(json_data, indent=2), attachment_type=allure.attachment_type.JSON)
            except (TypeError, ValueError):
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
            except (TypeError, ValueError):
                allure.attach(name="Request body", body=str(data), attachment_type=allure.attachment_type.TEXT)

        if params and isinstance(params, dict):
            allure.attach(name="Request params", body=json.dumps(params, indent=2), attachment_type=allure.attachment_type.JSON)
