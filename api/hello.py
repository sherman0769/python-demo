# api/hello.py
from http import HTTPStatus

def handler(request, response):
    """
    Vercel 會呼叫 handler(request, response)
    把字串 JSON 回傳給瀏覽器。
    """
    response.status_code = HTTPStatus.OK
    response.headers["Content-Type"] = "application/json"
    response.body = b'{"message": "Hello from Vercel Python Function!"}'
