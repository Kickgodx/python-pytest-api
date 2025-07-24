import json

import allure
from requests import Response


def add_response_attachments(response: Response):
    allure.attach(name='Response status code', body=f"{response.status_code}",
                  attachment_type=allure.attachment_type.TEXT)
    allure.attach(name="Response Headers", body=json.dumps(dict(response.headers), indent=2),
                  attachment_type=allure.attachment_type.JSON)
    if response.cookies:
        cookies_dict = {cookie.name: cookie.value for cookie in response.cookies}
        allure.attach(name="Response Cookies", body=json.dumps(cookies_dict, indent=2),
                      attachment_type=allure.attachment_type.JSON)
    if response.headers.get("Content-type", "") != "application/pdf":
        if response.text:
            try:
                body = json.dumps(response.json(), indent=1, ensure_ascii=False)
                allure.attach(name='Response body', body=body, attachment_type=allure.attachment_type.JSON)
            except Exception:
                body = response.text
                allure.attach(name='Response body', body=body, attachment_type=allure.attachment_type.TEXT)


def add_request_attachments(method, url, headers, data, params):
    allure.attach(name='Request', body=f"{method} {url}", attachment_type=allure.attachment_type.TEXT)
    allure.attach(body=json.dumps(dict(headers), indent=2), name='Request headers',
                  attachment_type=allure.attachment_type.JSON)

    if params:
        allure.attach(name='Request params', body=json.dumps(params, indent=1, ensure_ascii=False),
                      attachment_type=allure.attachment_type.JSON)

    if data:
        try:
            body = json.dumps(json.loads(data), indent=1, ensure_ascii=False)
            allure.attach(name='Request body', body=body, attachment_type=allure.attachment_type.JSON)
        except Exception:
            body = str(data)
            allure.attach(name='Request body', body=body, attachment_type=allure.attachment_type.TEXT)
