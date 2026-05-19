import importlib.util
import socket
import ssl
import sys
import threading
import uuid
from pathlib import Path
from typing import Callable

import utils.http_parser as http_parser

TARGET_HOST = "github.com"
TARGET_PORT = 443
TARGET_SSL = True

stop: bool = False
stop_route: str

created_sockets: list[socket.socket] = []
created_threads: list[threading.Thread] = []

# Define plugin functions
modify_request: Callable[
    [dict[str, str], dict[str, list[str]], bytes],
    tuple[dict[str, str], dict[str, list[str]], bytes],
]
modify_response: Callable[
    [dict[str, str], dict[str, list[str]], bytes],
    tuple[dict[str, str], dict[str, list[str]], bytes],
]


# Function to load the plugin file for the target
def load_plugin() -> None:
    global modify_request, modify_response

    executable_path: Path = Path(sys.argv[0]).parent
    plugin_path: str = str(
        executable_path / "plugins" / ("%s.%d.py" % (TARGET_HOST, TARGET_PORT))
    )
    print("[proxy.py:load_plugin] Loading plugin file %s" % (plugin_path))  # Log
    plugin_spec = importlib.util.spec_from_file_location("plugin", plugin_path)
    if plugin_spec is None:
        print(
            '[proxy.py:load_plugin] Could not load plugin "%s"' % (plugin_path)
        )  # Log
        exit(1)
    if plugin_spec.loader is None:
        print(
            '[proxy.py:load_plugin] Could not load loader of spec for plugin: "%s"'
            % (plugin_path)
        )  # Log
        exit(1)

    plugin_module = importlib.util.module_from_spec(plugin_spec)
    plugin_spec.loader.exec_module(plugin_module)

    # Load custom plugin functions
    modify_request = plugin_module.modify_request
    modify_response = plugin_module.modify_response
    print("[proxy.py:load_plugin] Plugin succesfully loaded")  # Log


# Function that handles HTTP request and response
def handle_http(
    client_socket: socket.socket, server_socket: socket.socket | ssl.SSLSocket
) -> None:
    global modify_request, modify_response, stop_route, stop
    keep_alive: bool = True

    # Send and receive loop
    while keep_alive:
        keep_alive = False

        # Receive from client
        request_headers: dict[str, list[str]]
        request_parameters: dict[str, str]
        request_header_data: bytes = b""
        request_body: bytes = b""
        while not request_header_data.endswith(b"\r\n\r\n"):
            request_header_data += client_socket.recv(1)

        request_parameters = http_parser.get_request_parameters(request_header_data)

        # Check if the proxy should be terminated
        if request_parameters["route"] == stop_route:
            print("[proxy.py:handle_http] Stopping the WebTheft proxy")  # Log
            stop = True
            continue

        request_headers = http_parser.get_headers(request_header_data)
        if (
            "content-length" in request_headers
            and request_parameters["method"] != "HEAD"
        ):
            request_content_length = int(request_headers["content-length"][0])
            request_body += client_socket.recv(request_content_length)

        # Modify client request with plugin functions
        modified_request = modify_request(
            request_parameters, request_headers, request_body
        )
        modified_request_parameters = modified_request[0]
        modified_request_headers = modified_request[1]
        modified_request_body = modified_request[2]

        # Build modified client request
        new_request = http_parser.build_request(
            modified_request_parameters, modified_request_headers, modified_request_body
        )

        # Send to server
        server_socket.sendall(new_request)

        # Receive headers from server
        response_headers: dict[str, list[str]]
        response_parameters: dict[str, str]
        response_header_data: bytes = b""
        response_body: bytes = b""
        while not response_header_data.endswith(b"\r\n\r\n"):
            response_header_data += server_socket.recv(1)

        # Receive body content from server
        response_parameters = http_parser.get_response_parameters(response_header_data)
        response_headers = http_parser.get_headers(response_header_data)

        if "content-length" in response_headers:
            response_content_length = int(response_headers["content-length"][0])
            while not response_content_length == len(response_body):
                response_body += server_socket.recv(1)
        if "transfer-encoding" in response_headers:
            if response_headers["transfer-encoding"][0].lower() == "chunked":
                _finished = False
                while not _finished:
                    _chunk_size: int
                    _chunk_data: bytes = b""
                    _chunk_raw: bytes = b""

                    while not _chunk_raw.endswith(b"\r\n"):
                        _chunk_raw += server_socket.recv(1)

                    _chunk_raw = _chunk_raw[:-2]
                    _chunk_size = int(_chunk_raw.decode(), 16)
                    if _chunk_size == 0:
                        _finished = True
                        continue

                    while not len(_chunk_data) == _chunk_size:
                        _chunk_data += server_socket.recv(1)
                    server_socket.recv(2)
                    response_body += _chunk_data
            del response_headers["transfer-encoding"]
            response_headers["content-length"] = []
            response_headers["content-length"].append(str(len(response_body)))
            server_socket.recv(2)

        # Check if the connection should be kept alive
        if "connection" in response_headers:
            keep_alive = response_headers["connection"][0].lower() == "keep-alive"

        # Modify server response with plugin functions
        modified_response = modify_response(
            response_parameters, response_headers, response_body
        )
        modified_response_parameters = modified_response[0]
        modified_response_headers = modified_response[1]
        modified_response_body = modified_response[2]

        # Build modified server reponse
        new_response = http_parser.build_response(
            modified_response_parameters,
            modified_response_headers,
            modified_response_body,
        )

        # Send to client
        client_socket.sendall(new_response)

    client_socket.close()
    server_socket.close()
    # print("Closing connection")  # Debug


# Function to handle the client connection
def handle_client(
    client_socket: socket.socket, client_address: tuple[str, int]
) -> None:
    global TARGET_HOST, TARGET_PORT, TARGET_SSL, created_sockets

    print(
        "[proxy.py:handle_client] New client connected -> %s:%d"
        % (client_address[0], client_address[1])
    )  # Log

    plain_socket: socket.socket = socket.create_connection((TARGET_HOST, TARGET_PORT))
    target_socket = socket.socket | ssl.SSLSocket

    # Handle if the target uses SSL
    if TARGET_SSL:
        context: ssl.SSLContext = ssl.create_default_context()
        target_socket = context.wrap_socket(plain_socket, server_hostname=TARGET_HOST)
    else:
        target_socket = plain_socket

    created_sockets.append(client_socket)
    created_sockets.append(target_socket)
    try:
        handle_http(client_socket, target_socket)
    except Exception as _e:
        print(
            "[proxy.py:handle_client] Error in connection %s -> %s:%d"
            % (_e, client_address[0], client_address[1])
        )  # Log


# Loop function that accepts clients
def create_listening_socket(address: tuple[str, int], ssl: bool = False) -> None:
    global stop, created_sockets, created_threads
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(address)
    server_socket.listen(20)

    print("[proxy.py:create_listening_socket] Waiting for incomning connections")  # Log
    while not stop:
        conn, addr = server_socket.accept()
        new_thread = threading.Thread(
            target=handle_client,
            args=(
                conn,
                addr,
            ),
        )
        new_thread.start()
        created_threads.append(new_thread)

    print("[proxy.py:create_listening_socket] Closing created sockets")  # Log
    for _s in created_sockets:
        _s.close()
    print("[proxy.py:create_listening_socket] Waiting for created threads")  # Log
    for _t in created_threads:
        _t.join()


# Function to start the proxy
def start(bind_data: tuple[str, int]) -> None:
    global stop_route
    load_plugin()

    stop_route = "/" + str(uuid.uuid4())
    print(
        "[proxy.py:start] Fetch http://%s:%d%s to stop WebTheft"
        % (bind_data[0], bind_data[1], stop_route),
    )  # Log

    print("[proxy.py:start] Creating listening socket on %s:%d" % bind_data)  # Log
    create_listening_socket(bind_data)
