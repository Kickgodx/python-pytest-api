import inspect
import json
import os
import uuid
import warnings

import allure
import requests
import urllib3
from requests import Response, HTTPError
from urllib3.exceptions import InsecureRequestWarning

from src.tech.custom_logger import logger

HTTP_METHODS = ("GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS")
DEFAULT_TIMEOUT = 30


class CustomRequester:
    """
    Класс-обёртка для работы с HTTP-запросами и логированием
    """
    def __init__(self, base_url: str, headers=None, timeout=DEFAULT_TIMEOUT):
        self.base_url = base_url
        self.timeout = timeout
        self.session = requests.Session()
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
        if filename is None or lineno is None or funcname is None:
            filename, lineno, funcname = self._get_caller_info()

        test_name = os.environ.get('PYTEST_CURRENT_TEST', 'Unknown test')

        log_lines = []

        if test_name != 'Unknown test':
            log_lines.append(f"Test: {test_name}")
        else:
            log_lines.append(f"Unknown test")

        log_lines.append(f"[{request_id}] - Error in: {filename}:{lineno} - {funcname}")
        log_lines.append(f"[{request_id}] - {err}")
        log_lines.append(f"[{request_id}] - Request URL: {method} {url}")

        headers_to_log = self._mask_bearer_tokens(headers)
        log_lines.append(f"[{request_id}] - Request headers: {headers_to_log}")
        log_lines.append(f"[{request_id}] - Request body: {data}")

        if response is not None:
            log_lines.append(f"[{request_id}] - Response headers: {response.headers}")
            log_lines.append(f"[{request_id}] - Response body: {response.text}\n")
        else:
            log_lines.append(f"[{request_id}] - Response body: None\n")

        # Объединяем все строки с переносами
        logger.error("\n".join(log_lines))

    def _send_request(self, method: str, endpoint: str, use_allure: bool, data=None, headers: dict = None, params=None, **kwargs) -> Response:
        """
        Универсальный метод для отправки HTTP-запросов.
        """
        if method.upper() not in HTTP_METHODS:
            raise ValueError(f"Недопустимый HTTP-метод: {method}. Допустимые значения: {HTTP_METHODS}")

        request_id = str(uuid.uuid4())
        filename, lineno, funcname = self._get_caller_info()
        url = f"{self.base_url}{endpoint}"
        combined_headers = {**headers}

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

        if use_allure:
            self._add_request_attachments(method, url, response.request.headers, data, params)
            self._add_response_attachments(response)

        if 400 <= response.status_code < 600:
            try:
                response.raise_for_status()
            except HTTPError as e:
                exception_name = e.__class__.__name__
                self._log_error(request_id, f"{exception_name}: {e}", response, data, combined_headers, url, method, None, None, None)

        return response

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

    def options(self, endpoint: str, headers: dict = None, use_allure = True, **kwargs) -> Response:
        return self._send_request("OPTIONS", endpoint, use_allure=use_allure, headers=headers, **kwargs)

    @staticmethod
    def _add_response_attachments(response):
        allure.attach(name='Response status code', body=f"{response.status_code}", attachment_type=allure.attachment_type.TEXT)
        allure.attach(name="Response Headers", body=json.dumps(dict(response.headers), indent=2), attachment_type=allure.attachment_type.JSON)
        if response.text:
            try:
                json_data = response.json()
                allure.attach(name='Response body', body=json.dumps(json_data, indent=2), attachment_type=allure.attachment_type.JSON)
            except ValueError:
                allure.attach(name='Response body', body=response.text, attachment_type=allure.attachment_type.TEXT)

    @staticmethod
    def _add_request_attachments(method, url, headers, data, params):
        allure.attach(name='Request', body=f"{method} {url}", attachment_type=allure.attachment_type.TEXT)
        allure.attach(body=json.dumps(dict(headers), indent=2), name='Request headers', attachment_type=allure.attachment_type.JSON)
        if data:
            try:
                if isinstance(data, str):
                    data = json.loads(data)

                # Пробуем преобразовать в JSON
                json_data = json.dumps(data, indent=2)
                allure.attach(name='Request body', body=json_data, attachment_type=allure.attachment_type.JSON)
            except TypeError:
                allure.attach(name='Request body', body=str(data), attachment_type=allure.attachment_type.TEXT)

        if params:
            allure.attach(name='Request params', body=json.dumps(params, indent=2), attachment_type=allure.attachment_type.JSON)

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