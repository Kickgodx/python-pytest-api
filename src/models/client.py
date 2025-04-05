class Client:
    def __init__(self):
        self.id = None
        self.client_secret = None
        self.api_key = None
        self.base_content_type = "application/json"

    def get_base_headers(self) -> dict:
        return {"Content-Type": self.base_content_type}

    @staticmethod
    def get_empty_headers() -> dict:
        return {}

    def get_auth_headers(self) -> dict:
        return {"Content-Type": self.base_content_type, "api_key": f"{self.api_key}"}
