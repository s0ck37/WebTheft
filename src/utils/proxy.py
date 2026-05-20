import importlib.util
import socket
import ssl
import sys
import threading
import uuid
from dataclasses import dataclass
from pathlib import Path
from typing import Callable

import h11

target_host: str
target_port: int
target_ssl: bool

stop: bool = False
stop_route: str

created_sockets: list[socket.socket] = []
created_threads: list[threading.Thread] = []


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


# Define plugin functions
modify_request: Callable[[HttpRequest], HttpRequest]
modify_response: Callable[[HttpResponse], HttpResponse]


# Function to load the plugin file for the target
def load_plugin() -> None:
    global modify_request, modify_response

    executable_path: Path = Path(sys.argv[0]).parent
    plugin_path: str = str(
        executable_path / "plugins" / ("%s.%d.py" % (target_host, target_port))
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

    # Send and receive loop
    while True:
        # recreate connections per cycle (fixes h11 state bug)
        client_http = h11.Connection(h11.SERVER)
        server_http = h11.Connection(h11.CLIENT)

        # Get client request
        client_request = HttpRequest(b"", b"", [], b"")
        client_raw_data: bytes

        request_done = False

        while not request_done:
            # Get client request initial data
            client_raw_data = client_socket.recv(4096)
            if not client_raw_data:
                client_socket.close()
                server_socket.close()
                return

            client_http.receive_data(client_raw_data)

            # Receive request
            # request_chunks: list[bytes] = [] # Debug
            while True:
                client_event = client_http.next_event()

                if client_event is h11.NEED_DATA:
                    break
                if isinstance(client_event, h11.Request):
                    client_request.method = client_event.method
                    client_request.target = client_event.target
                    client_request.headers = list(client_event.headers)
                elif isinstance(client_event, h11.Data):
                    client_request.body += client_event.data
                elif isinstance(client_event, h11.EndOfMessage):
                    request_done = True
                    break

        # Check if route matches the stop route
        if client_request.target.decode() == stop_route:
            client_socket.close()
            server_socket.close()
            stop = True
            return

        # Modify request data
        modified_client_request = modify_request(client_request)

        # Build modified request
        modified_raw_request: bytes = b""
        _request_builder = h11.Connection(h11.CLIENT)

        _modified_request = h11.Request(
            method=modified_client_request.method,
            target=modified_client_request.target,
            headers=modified_client_request.headers,
        )

        modified_raw_request += _request_builder.send(_modified_request)
        if modified_client_request.body != b"":
            modified_raw_request += _request_builder.send(
                h11.Data(data=modified_client_request.body)
            )
        modified_raw_request += _request_builder.send(h11.EndOfMessage())

        # Send modifed request to server
        server_socket.sendall(modified_raw_request)

        # Get server response
        server_response = HttpResponse(0, [], b"")
        server_raw_data: bytes

        response_done = False
        while not response_done:
            # Get server response initial data
            server_raw_data = server_socket.recv(4096)
            if not server_raw_data:
                client_socket.close()
                server_socket.close()
                return

            server_http.receive_data(server_raw_data)

            # Receive response
            # response_chunks: list[bytes] = []
            while True:
                server_event = server_http.next_event()

                if server_event is h11.NEED_DATA:
                    break
                if isinstance(server_event, h11.Response):
                    server_response.status_code = server_event.status_code
                    server_response.headers = list(server_event.headers)
                    if client_request.method == b"HEAD":
                        response_done = True
                        break
                elif isinstance(server_event, h11.Data):
                    server_response.body += server_event.data
                elif isinstance(server_event, h11.EndOfMessage):
                    response_done = True
                    break

        # Modify response data
        modified_server_response = modify_response(server_response)

        # Build modified response
        modified_raw_response: bytes = b""
        _response_builder = h11.Connection(h11.SERVER)

        _modified_response = h11.Response(
            status_code=modified_server_response.status_code,
            headers=modified_server_response.headers,
        )

        modified_raw_response += _response_builder.send(_modified_response)
        modified_raw_response += _response_builder.send(
            h11.Data(data=modified_server_response.body)
        )
        modified_raw_response += _response_builder.send(h11.EndOfMessage())

        # Send modifed response to client
        client_socket.sendall(modified_raw_response)

        # Check if the connection should be closed
        if (
            b"connection: close" in modified_raw_response.split(b"\r\n\r\n")[0].lower()
            or b"connection: close"
            in modified_raw_request.split(b"\r\n\r\n")[0].lower()
        ):
            client_socket.close()
            server_socket.close()
            return


# Function to handle the client connection
def handle_client(
    client_socket: socket.socket, client_address: tuple[str, int]
) -> None:
    global target_host, target_port, target_ssl, created_sockets

    # print(
    #     "[proxy.py:handle_client] New client connected -> %s:%d"
    #     % (client_address[0], client_address[1])
    # )  # Log

    plain_socket: socket.socket = socket.create_connection((target_host, target_port))
    target_socket = socket.socket | ssl.SSLSocket

    # Handle if the target uses SSL
    if target_ssl:
        context: ssl.SSLContext = ssl.create_default_context()
        target_socket = context.wrap_socket(plain_socket, server_hostname=target_host)
    else:
        target_socket = plain_socket

    created_sockets.append(client_socket)
    created_sockets.append(target_socket)
    try:
        handle_http(client_socket, target_socket)
    except Exception as _e:
        print(
            "[proxy.py:handle_client] Error in connection %s:%d -> %s"
            % (client_address[0], client_address[1], _e)
        )  # Log


# Loop function that accepts clients
def create_listening_socket(address: tuple[str, int], ssl: bool = False) -> None:
    global stop, created_sockets, created_threads
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
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
def start(bind_data: tuple[str, int], target_data: tuple[str, int, bool]) -> None:
    global target_host, target_port, target_ssl, stop_route

    target_host = target_data[0]
    target_port = target_data[1]
    target_ssl = target_data[2]
    print(
        "[proxy.py:start] Impersonating web service %s:%d (SSL: %r)" % target_data
    )  # Log

    load_plugin()

    stop_route = "/" + str(uuid.uuid4())
    print(
        "[proxy.py:start] Fetch http://%s:%d%s to stop WebTheft"
        % (bind_data[0], bind_data[1], stop_route),
    )  # Log

    print("[proxy.py:start] Creating listening socket on %s:%d" % bind_data)  # Log
    create_listening_socket(bind_data)
