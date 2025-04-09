import uuid


class HeaderBuilder:
    """
    Builder для создания заголовков запроса (device_id, device_type, content_type, auth_token)
    """

    def __init__(self, headers: dict = None, content_type: str = "application/json"):
        self._headers = {"Content-Type": content_type}
        if headers is not None:
            self._headers = headers.copy()

    def add_request_id(self, request_id=str(uuid.uuid4())):
        return self.add_header("requestId", request_id)

    def add_header(self, name, value):
        self._headers[name] = value
        return self

    def add_headers(self, additional_headers):
        self._headers.update(additional_headers)
        return self

    def get_header(self, name):
        return self._headers.get(name, None)

    def remove_header(self, name):
        if name in self._headers:
            del self._headers[name]
        return self

    def update_headers(self, headers):
        self._headers.update(headers)
        return self

    def build(self):
        return self._headers
