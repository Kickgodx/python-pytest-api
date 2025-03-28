import inspect
import json
import os
import uuid
import warnings

import allure
import requests
import urllib3
from requests import Response, HTTPError
from urllib3.exceptions import InsecureRequestWarning  # Правильный импорт

from utils.custom_logger import logger

HTTP_METHODS = ("GET", "POST", "PUT", "DELETE", "PATCH")
DEFAULT_TIMEOUT = 30


# Класс-обертка для работы с HTTP-запросами и логированием
class CustomRequester:
    """
    Класс-обёртка для работы с HTTP-запросами и логированием
    """
    def __init__(self, base_url: str, headers=None, timeout=DEFAULT_TIMEOUT):
        self.base_url = base_url
        self.headers = headers or {}
        self.timeout = timeout
        self.session = requests.Session()
        self.session.headers.update(self.headers)
        self.last_test_name = None  # Атрибут для хранения имени текущего теста
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning) # Для интернал вылетает ошибка про сертификат
        warnings.filterwarnings("ignore", category=InsecureRequestWarning)

    def close(self):
        self.session.close()
        logger.info("Session closed")

    @staticmethod
    def _get_caller_info() -> tuple[str, int, str]:
        for frame in inspect.stack():
            module = inspect.getmodule(frame[0])
            filename = module.__file__ if module else "Unknown"
            if filename != __file__:
                lineno = frame.lineno
                funcname = frame.function
                return filename, lineno, funcname
        return "Unknown", 0, "Unknown"

    def _log_request(self, request_id: str, method: str, url: str, **kwargs) -> None:
        """
        Метод для логирования информации о запросе
        :param request_id: уникальный идентификатор запроса
        :param method: HTTP-метод
        :param url: URL-адрес запроса
        :param kwargs: дополнительные параметры запроса
        :return: None
        """
        filename, lineno, funcname = self._get_caller_info()
        logger.info(f"RequestID: [{request_id}] - Request: {method} {url} - {filename}:{lineno} - {funcname}")
        if 'headers' in kwargs:
            headers_to_log = self._mask_bearer_tokens(kwargs['headers'])
            logger.info(f"RequestID: [{request_id}] - Headers: {headers_to_log}")
        if 'params' in kwargs:
            logger.info(f"RequestID: [{request_id}] - Params: {kwargs['params']}")
        if 'json' in kwargs:
            logger.info(f"RequestID: [{request_id}] - Payload (json): {kwargs['json']}")
        if 'data' in kwargs:
            logger.info(f"RequestID: [{request_id}] - Payload (data): {kwargs['data']}")

    @staticmethod
    def _log_response(request_id: str, response: Response) -> None:
        """
        Метод для логирования информации об ответе
        :param request_id: уникальный идентификатор запроса
        :param response: объект ответа на запрос (requests.Response)
        :return: None
        """
        logger.info(f"[{request_id}] - Response: {response.status_code} {response.url}")
        logger.info(f"[{request_id}] - Response headers: {response.headers}")
        logger.info(f"[{request_id}] - Response body: {response.text}\n")

    def _log_error(self, request_id: str, err, response: Response | None, data, headers: dict, url: str, method: str, filename, lineno, funcname) -> None:
        """
        Метод для логирования информации об ошибке
        :param request_id: уникальный идентификатор запроса
        :param err: объект ошибки (HTTPError или RequestException)
        :param response: объект ответа на запрос (requests.Response)
        :param data: данные запроса
        :param headers: заголовки запроса (dict)
        :param url: URL-адрес запроса
        :param method: HTTP-метод
        :param filename: имя файла, из которого был вызван запрос
        :param lineno: номер строки, из которой был вызван запрос
        :param funcname: имя функции, из которой был вызван запрос
        :return: None
        """
        test_name = os.environ.get('PYTEST_CURRENT_TEST', 'Unknown test')

        if test_name != 'Unknown test':
            logger.error(f"Test: {test_name}")
            self.last_test_name = test_name

        logger.error(f"[{request_id}] - Error occurred: {err}")
        logger.error(f"[{request_id}] - Error in: {filename}:{lineno} - {funcname}")
        logger.error(f"[{request_id}] - Request URL: {method} {url}")
        headers_to_log = self._mask_bearer_tokens(headers)
        logger.error(f"[{request_id}] - Request headers: {headers_to_log}")
        logger.error(f"[{request_id}] - Request body: {data}")
        if response is not None:
            logger.error(f"[{request_id}] - Response headers: {response.headers}")
            logger.error(f"[{request_id}] - Response body: {response.text}\n")
        else:
            logger.error(f"[{request_id}] - Response body: None\n")

    def _handle_response(self, request_id: str, response: Response, data=None, headers: dict =None, url: str = None, method: str=None) -> Response:
        """
        Метод для обработки ответа на запрос
        :param request_id: уникальный идентификатор запроса
        :param response: объект ответа на запрос (requests.Response)
        :param data: данные запроса
        :param headers: заголовки запроса (dict)
        :param url: URL-адрес запроса
        :param method: HTTP-метод
        :return: объект ответа на запрос (requests.Response)
        """
        filename, lineno, funcname = self._get_caller_info()
        response_request_id = response.headers.get("Requestid", f"requestId {request_id}")

        try:
            response.raise_for_status()
        except HTTPError as e:
            exception_name = e.__class__.__name__
            err_msg = f"исключение при {method.upper()} запросе {url}:\n {e}"
            self._log_error(response_request_id, f"{exception_name} {err_msg}", response, data, headers, url, method, filename, lineno, funcname)
            raise HTTPError(err_msg, response=e.response, request=e.response.request) from e
        except Exception as e:
            exception_name = e.__class__.__name__
            err_msg = f"исключение при {method.upper()} запросе {url}:\n {e}"
            self._log_error(response_request_id, f"{exception_name} {err_msg}", response, data, headers, url, method, filename, lineno, funcname)
            raise e.__class__(err_msg) from e

        return response

    def _send_request(self, method: str, endpoint: str, use_allure: bool, data=None, headers: dict = None, params=None, **kwargs) -> Response:
        """
        Универсальный метод для отправки HTTP-запросов.
        """
        if method.upper() not in HTTP_METHODS:
            raise ValueError(f"Недопустимый HTTP-метод: {method}. Допустимые значения: {HTTP_METHODS}")

        request_id = str(uuid.uuid4())
        filename, lineno, funcname = self._get_caller_info()
        url = f"{self.base_url}{endpoint}"
        combined_headers = {**self.headers, **(headers or {})}

        self._log_request(request_id, method, url, headers=combined_headers, params=params, data=data, **kwargs)

        try:
            response = self.session.request(
                method=method, url=url, headers=combined_headers, params=params, data=data, timeout=self.timeout, verify=False,
                **kwargs
            )
        except Exception as e:
            self._add_request_attachments(method, url, headers, data, params)
            exception_name = e.__class__.__name__
            err_msg = f"исключение при {method.upper()} запросе {endpoint}:\n{e}"
            self._log_error(request_id, f"{exception_name} {err_msg}", None, data, combined_headers, url, method,
                            filename, lineno, funcname)
            raise e.__class__(err_msg) from e

        self._log_response(request_id, response)
        try:
            handled_response = self._handle_response(request_id, response, method=method, url=url, headers=response.request.headers, data=data)
        except Exception:
            self._add_request_attachments(method, url, headers, data, params)
            self._add_response_attachments(response)
            raise

        if use_allure:
            self._add_request_attachments(method, url, headers, data, params)
            self._add_response_attachments(handled_response)

        return handled_response

    def get(self, endpoint: str, headers: dict = None, params=None, use_allure = True, **kwargs) -> Response:
        return self._send_request("GET", endpoint, use_allure=use_allure, headers=headers, params=params, **kwargs)

    def post(self, endpoint: str, data=None, headers: dict = None, use_allure = True, **kwargs) -> Response:
        return self._send_request("POST", endpoint, use_allure=use_allure, data=data, headers=headers, **kwargs)

    def put(self, endpoint: str, data=None, headers: dict = None, use_allure = True, **kwargs) -> Response:
        return self._send_request("PUT", endpoint, use_allure=use_allure, data=data, headers=headers, **kwargs)

    def patch(self, endpoint: str, data=None, headers: dict = None, use_allure = True, **kwargs) -> Response:
        return self._send_request("PATCH", endpoint, use_allure=use_allure, data=data, headers=headers, **kwargs)

    def delete(self, endpoint: str, headers: dict = None, use_allure = True, **kwargs) -> Response:
        return self._send_request("DELETE", endpoint, use_allure=use_allure, headers=headers, **kwargs)

    # Методы для управления заголовками
    def set_header(self, key: str, value: str) -> None:
        """
        Метод для добавления заголовка
        :param key: ключ заголовка
        :param value: значение заголовка
        """
        self.headers[key] = value
        self.session.headers.update(self.headers)

    def remove_header(self, key: str) -> None:
        """
        Метод для удаления заголовка
        :param key: ключ заголовка
        """
        if key in self.headers:
            del self.headers[key]
            self.session.headers.pop(key, None)

    def get_header(self, key: str) -> str | None:
        """
        Метод для получения значения заголовка по ключу
        :param key: ключ заголовка
        :return: значение заголовка или None, если заголовок не найден
        """
        return self.headers.get(key)

    def get_all_headers(self) -> dict | None:
        """
        Метод для получения всех заголовков
        :return: все заголовки или None, если заголовки отсутствуют
        """
        return self.headers

    def update_headers(self, headers: dict) -> None:
        """
        Метод для обновления заголовков
        :param headers: новые заголовки
        """
        self.headers.update(headers)
        self.session.headers.update(self.headers)

    @property
    def all_headers(self) -> dict | None:
        """
        Свойство для получения всех заголовков
        :return: все заголовки или None, если заголовки отсутствуют
        """
        return self.headers

    @staticmethod
    def _add_response_attachments(response):
        allure.attach(name='Response status code', body=f"{response.status_code}",
                      attachment_type=allure.attachment_type.TEXT)
        allure.attach(name="Response Headers", body=json.dumps(dict(response.headers), indent=2),
                      attachment_type=allure.attachment_type.JSON)
        if response.text:
            allure.attach(name='Response body', body=response.text, attachment_type=allure.attachment_type.TEXT)

    @staticmethod
    def _add_request_attachments(method, url, headers, data, params):
        allure.attach(name='Request', body=f"{method} {url}", attachment_type=allure.attachment_type.TEXT)
        allure.attach(body=json.dumps(headers, indent=2), name='Request headers',
                      attachment_type=allure.attachment_type.JSON)
        if data:
            allure.attach(name='Request body', body=str(data), attachment_type=allure.attachment_type.TEXT)
        if params:
            allure.attach(name='Request params', body=json.dumps(params, indent=2),
                          attachment_type=allure.attachment_type.JSON)

    @staticmethod
    def _mask_bearer_tokens(headers: dict) -> dict:
        """
        Маскирует Bearer-токены во всех значениях словаря headers.
        Возвращает новый словарь с замаскированными данными.
        """
        masked_headers = {}
        for key, value in headers.items():
            if isinstance(value, str) and 'Bearer ' in value:
                # Разделяем строку по Bearer и маскируем токен
                parts = value.split('Bearer ')
                if len(parts) > 1:
                    # Оставляем 'Bearer ', но заменяем сам токен на '*****'
                    masked_value = f"{parts[0]}Bearer *****"
                    masked_headers[key] = masked_value
                else:
                    masked_headers[key] = value
            else:
                masked_headers[key] = value
        headers_ref = {**headers, **masked_headers}
        return headers_ref