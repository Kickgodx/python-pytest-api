class Client:
    def __init__(self):
        self.client_id = None
        self.client_secret = None
        self.api_key = None
        self.base_content_type = "application/json"

    def get_base_headers(self) -> dict:
        return {"Content-Type": self.base_content_type}

    @staticmethod
    def get_empty_headers() -> dict:
        return {}

    def get_client_id(self) -> str:
        return self.client_id

    def get_client_secret(self) -> str:
        return self.client_secret
