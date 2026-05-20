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
    log += "[plugins/simpleplugin.example:modify_request] %s request for %s\n" % (
        request.method.decode(),
        request.target.decode(),
    )  # Log

    print(log.strip())  # Log

    # Modify headers
    for _hi in range(0, len(request.headers)):
        if request.headers[_hi][0].lower() == b"host":
            if actual_host == b"":
                actual_host = request.headers[_hi][1]
            request.headers[_hi] = (request.headers[_hi][0], b"simpleplugin.example")

        if request.headers[_hi][0].lower() == b"origin":
            request.headers[_hi] = (
                request.headers[_hi][0],
                request.headers[_hi][1].replace(actual_host, b"simpleplugin.example"),
            )
            request.headers[_hi] = (
                request.headers[_hi][0],
                request.headers[_hi][1].replace(b"http:", b"https:"),
            )

        if request.headers[_hi][0].lower() == b"referer":
            request.headers[_hi] = (
                request.headers[_hi][0],
                request.headers[_hi][1].replace(actual_host, b"simpleplugin.example"),
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
                response.headers[_hi][1].replace(b"simpleplugin.example", actual_host),
            )
            response.headers[_hi] = (
                response.headers[_hi][0],
                response.headers[_hi][1].replace(b"https:", b"http:"),
            )

    return response
