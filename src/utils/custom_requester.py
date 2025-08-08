from urllib.parse import urlparse

import requests
from requests import Response
from requests.adapters import HTTPAdapter
from requests.cookies import RequestsCookieJar
from urllib3.util.retry import Retry

from config import DEFAULT_TIMEOUT
from src.decorators.allure_steps import add_allure_attachments
from src.decorators.http_wrappers import send_request_wrapper
from src.utils.custom_logger import log, logger


class CustomRequester:
    """Класс-обёртка для работы с HTTP-запросами и логированием"""

    def __init__(
        self,
        base_url: str,
        timeout: float = DEFAULT_TIMEOUT,
        headers: dict[str, str] | None = None,
        use_env_proxies: bool = False,
        retries: int | None = None,
        backoff_factor: float = 0.1,
        status_forcelist: tuple[int, ...] = (500, 502, 503, 504),
    ):
        """Создает HTTP-клиент.

        Args:
            base_url: базовый URL сервиса.
            timeout: таймаут запросов.
            headers: заголовки, добавляемые ко всем запросам.
            use_env_proxies: использовать ли прокси из переменных окружения.
                По умолчанию прокси отключены, что предотвращает неожиданные
                ошибки при запуске тестов в окружениях с ограниченным доступом
                к внешней сети.
        """

        self.base_url = base_url
        self.domain = self.get_base_domain()
        self.timeout = timeout
        self.session = requests.Session()
        # По умолчанию отключаем использование системных прокси, чтобы
        # избежать ошибок вроде 403 при попытке соединения через недоступный
        # прокси-сервер. Поведение можно изменить через параметр
        # ``use_env_proxies``.
        self.session.trust_env = use_env_proxies

        if retries:
            retry = Retry(
                total=retries,
                backoff_factor=backoff_factor,
                status_forcelist=status_forcelist,
                allowed_methods=("HEAD", "GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"),
            )
            adapter = HTTPAdapter(max_retries=retry)
            self.session.mount("http://", adapter)
            self.session.mount("https://", adapter)

        self.default_headers = headers or {}

        if self.default_headers:
            self.session.headers.update(self.default_headers)

    def session_close(self):
        self.session.close()

    # Контекстные менеджеры для управления ресурсами
    def __enter__(self):
        """Вход в синхронный контекстный менеджер"""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Выход из синхронного контекстного менеджера"""
        self.session_close()

    def _build_url(self, endpoint: str) -> str:
        if endpoint:
            return (
                f"{self.base_url}{endpoint}"
                if endpoint.startswith("/")
                else f"{self.base_url}/{endpoint}"
            )
        return self.base_url

    @send_request_wrapper(logger)
    @add_allure_attachments
    def _send_request(
        self,
        method: str,
        endpoint: str,
        use_allure: bool = True,  # noqa: ARG002
        **kwargs,
    ) -> Response:
        """Универсальный метод для отправки HTTP-запросов."""
        kwargs.setdefault("timeout", self.timeout)

        url = self._build_url(endpoint)

        return self.session.request(method=method, url=url, **kwargs)

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

    def add_cookie(self, cookies: dict | RequestsCookieJar):
        """
        Добавить куки в сессию

        Args:
            cookies: Куки в виде словаря или RequestsCookieJar
        """
        if isinstance(cookies, dict):
            for key, value in cookies.items():
                self.session.cookies.set(key, value)
        elif isinstance(cookies, RequestsCookieJar):
            self.session.cookies.update(cookies)
        else:
            raise TypeError("Куки должны быть словарем или RequestsCookieJar")

    def clear_cookies(self):
        """Очищает все куки в текущей сессии"""
        self.session.cookies.clear()

    def get_client_info(self) -> dict:
        """Получить информацию о клиенте"""
        return {
            "base_url": self.base_url,
            "domain": self.domain,
            "protocol": urlparse(self.base_url).scheme,
            "timeout": self.timeout,
            "default_headers": self.default_headers,
            "session_cookies": self.session.cookies.get_dict(),
            "session_headers": self.session.headers,
        }

    def check_server_alive(self):
        """Проверяет, доступен ли сервер по base_url с помощью HEAD-запроса. Если HEAD не поддерживается (405), пробует OPTIONS."""
        try:
            response = self.session.head(self.base_url, timeout=self.timeout, verify=False)
            if response.status_code in {405, 404}:
                # HEAD не поддерживается, пробуем OPTIONS
                log.info(f"HEAD не поддерживается, вызываем OPTIONS для {self.base_url}")
                response = self.session.options(self.base_url, timeout=self.timeout, verify=False)
            if not (200 <= response.status_code < 400):
                log.error(f"Сервер недоступен: {response.status_code} {self.base_url}")
                raise ConnectionError(
                    f"Сервер недоступен: {response.request.method if hasattr(response, 'request') else 'HEAD/OPTIONS'} {self.base_url} -> {response.status_code}"
                )
        except requests.exceptions.RequestException as e:
            log.error(f"Ошибка при проверке сервера: {e}")
            raise ConnectionError(f"Сервер недоступен: {e}") from e

    # Хуки сессии (для логирования через session hooks)
    @staticmethod
    def request_logging(response: Response, *_args, **_kwargs) -> Response:
        """Логирует запрос ПОСЛЕ отправки (из объекта Response)."""
        log.info(
            f"Request: {response.request.method} {response.request.url}\n"
            f"Headers: {response.request.headers}\n"
            f"Body: {response.request.body}",
        )
        return response

    @staticmethod
    def response_logging(response: Response, *_args, **_kwargs) -> Response:
        """Логирует ответ сервера."""
        log.info(
            f"Response: {response.status_code} {response.url}\n"
            f"Content: {response.text if response.text else {response.content}}\n",
        )
        return response
