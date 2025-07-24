import uuid
from urllib.parse import urlparse

import requests
from requests import Response

from config import DEFAULT_TIMEOUT
from src.utils.custom_logger import logger, log
from src.utils.decorators import send_request_wrapper


class CustomRequester:
    """Класс-обёртка для работы с HTTP-запросами и логированием"""

    def __init__(self, base_url: str, timeout=DEFAULT_TIMEOUT):
        self.base_url = base_url
        self.domain = self.get_base_domain()
        self.timeout = timeout
        self.session = requests.Session()
        self.session.verify = False

    def close(self):
        self.session.close()
        logger.log_info("Session closed")

    @send_request_wrapper(logger)
    def _send_request(self, method: str, endpoint: str, use_allure: bool = True, **kwargs) -> Response:
        """Универсальный метод для отправки HTTP-запросов."""
        kwargs.setdefault('timeout', self.timeout)

        url = f"{self.base_url}{endpoint}"

        return self.session.request(method=method, url=url, **kwargs)

    def check_server_alive(self):
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

    def healthcheck(self):
        """Проверяет, доступен ли сервер по base_url с помощью HEAD-запроса."""
        try:
            response = self.session.head(self.base_url, timeout=self.timeout, verify=False)
            if not (200 <= response.status_code < 400):
                log.log_error(
                    str(uuid.uuid4()),
                    f"HEAD-запрос к {self.base_url} вернул статус {response.status_code}",
                    response,
                    None,
                    response.request.headers if hasattr(response, 'request') else {},
                    self.base_url,
                    "HEAD"
                )
                # raise ConnectionError(f"Сервер недоступен: HEAD {self.base_url} -> {response.status_code}")
        except requests.exceptions.RequestException as e:
            log.log_error(str(uuid.uuid4()), f"Ошибка при проверке сервера {self.base_url}: {e}", None, None, {}, self.base_url, "HEAD")
            # raise ConnectionError(f"Сервер недоступен: {e}")

    def get(self, endpoint: str, use_allure=True, **kwargs) -> Response:
        self.check_server_alive()
        return self._send_request("GET", endpoint, use_allure=use_allure, **kwargs)

    def post(self, endpoint: str, use_allure=True, **kwargs) -> Response:
        self.check_server_alive()
        return self._send_request("POST", endpoint, use_allure=use_allure, **kwargs)

    def put(self, endpoint: str, use_allure=True, **kwargs) -> Response:
        self.check_server_alive()
        return self._send_request("PUT", endpoint, use_allure=use_allure, **kwargs)

    def patch(self, endpoint: str, use_allure=True, **kwargs) -> Response:
        self.check_server_alive()
        return self._send_request("PATCH", endpoint, use_allure=use_allure, **kwargs)

    def delete(self, endpoint: str, use_allure=True, **kwargs) -> Response:
        self.check_server_alive()
        return self._send_request("DELETE", endpoint, use_allure=use_allure, **kwargs)

    def options(self, endpoint: str, use_allure=True, **kwargs) -> Response:
        return self._send_request("OPTIONS", endpoint, use_allure=use_allure, **kwargs)

    def head(self, endpoint: str, use_allure=True, **kwargs) -> Response:
        return self._send_request("HEAD", endpoint, use_allure=use_allure, **kwargs)

    def trace(self, endpoint: str, use_allure=True, **kwargs) -> Response:
        return self._send_request("TRACE", endpoint, use_allure=use_allure, **kwargs)

    def connect(self, endpoint: str, use_allure=True, **kwargs) -> Response:
        return self._send_request("CONNECT", endpoint, use_allure=use_allure, **kwargs)

    def get_base_domain(self) -> str:
        """
        Возвращает базовый хост без протокола
        """
        parsed_url = urlparse(self.base_url)
        return parsed_url.hostname or parsed_url.netloc or self.base_url
