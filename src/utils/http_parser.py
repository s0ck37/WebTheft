# Reference: https://developer.mozilla.org/en-US/docs/Web/HTTP

# Function to get HTTP request parameters
def get_request_parameters(data: bytes) -> dict[str, str]:
    raw_request: bytes = data.split(b"\r\n")[0].strip()
    request_data_list: list[bytes] = raw_request.split(b" ")
    request_data: dict[str, str] = {}

    request_data["method"] = request_data_list[0].decode()
    request_data["route"] = request_data_list[1].decode()
    request_data["version"] = request_data_list[2].decode()
    return request_data


# Function to get HTTP response parameters
def get_response_parameters(data: bytes) -> dict[str, str]:
    raw_response: bytes = data.split(b"\r\n")[0].strip()
    response_data_list: list[bytes] = raw_response.split(b" ")
    response_data: dict[str, str] = {}

    response_data["version"] = response_data_list[0].decode()
    response_data["status_code"] = response_data_list[1].decode()
    response_data["status_message"] = response_data_list[2].decode()
    return response_data


# Function to get HTTP request headers
def get_headers(data: bytes) -> dict[str, list[str]]:

    data = data.strip()
    raw_headers = data.split(b"\r\n")
    clean_headers: dict[str, list[str]] = {}

    for raw_header in raw_headers[1:]:
        header_data = raw_header.strip().split(b": ", 1)
        if raw_header == b"":
            continue

        header_name: str = header_data[0].decode().lower()
        header_content: str = header_data[1].decode()
        if header_name not in clean_headers:
            clean_headers[header_name] = []
            clean_headers[header_name].append(header_content)
        else:
            clean_headers[header_name].append(header_content)
    return clean_headers


# Function to decode HTTP body data
# They can be in the order they were applied, like: deflate, gzip
# Supported methods: gzip, compress, deflate, br, zstd, dcb, dcz
def decode_body(content: bytes, encoding: str) -> str:
    return ""


# Function to build an HTTP request
def build_request(
    parameters: dict[str, str], headers: dict[str, list[str]], body: bytes
) -> bytes:
    final_request: bytes = b""

    # Build parameters
    final_request += parameters["method"].encode() + b" "
    final_request += parameters["route"].encode() + b" "
    final_request += parameters["version"].encode() + b"\r\n"

    # Format header names correctly and build headers
    for header in headers:
        printable_header: str = ""
        for _ci in range(0, len(header)):
            if _ci == 0:
                printable_header += header[_ci].upper()
            elif header[_ci - 1] == "-":
                printable_header += header[_ci].upper()
            else:
                printable_header += header[_ci]

        for value in headers[header]:
            _cache_header: str = "%s: %s" % (
                printable_header,
                value,
            )
            final_request += _cache_header.encode() + b"\r\n"
    final_request += b"\r\n"

    # Build content
    final_request += body
    return final_request


# Function to build an HTTP response
def build_response(
    parameters: dict[str, str], headers: dict[str, list[str]], body: bytes
) -> bytes:
    final_response: bytes = b""

    # Build parameters
    final_response += parameters["version"].encode() + b" "
    final_response += parameters["status_code"].encode() + b" "
    final_response += parameters["status_message"].encode() + b"\r\n"

    # Format header names correctly and build headers
    for header in headers:
        printable_header: str = ""
        for _ci in range(0, len(header)):
            if _ci == 0:
                printable_header += header[_ci].upper()
            elif header[_ci - 1] == "-":
                printable_header += header[_ci].upper()
            else:
                printable_header += header[_ci]

        for value in headers[header]:
            _cache_header: str = "%s: %s" % (
                printable_header,
                value,
            )
            final_response += _cache_header.encode() + b"\r\n"
    final_response += b"\r\n"

    # Build content
    final_response += body
    return final_response
