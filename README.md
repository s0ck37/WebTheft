# 🥷 WebTheft

A lightweight HTTP/1.1 forward intercepting proxy built in Python using `h11`, designed for traffic inspection, modification, and plugin-based request/response rewriting.

> ⚠️ Educational / research tool only. Do not use on networks or systems you do not own or have permission to test.

## 📌 Features

- HTTP/1.1 forward proxy
- Request and response interception
- Plugin system for modifying traffic
- Header/body rewriting support
- Multi-threaded client handling
- Basic session routing control (stop route)
- Optional SSL target support (server-side TLS connection)

## 🧠 Architecture

````
Client → WebTheft Proxy → Target Server
↕
plugin system
(modify_request / modify_response)
````

Core components:
- `h11` for HTTP/1.1 parsing and serialization
- raw `socket` connections for client/server transport
- plugin-based modification layer

## 📦 Requirements

```txt
h11
````

Install:

```bash
pip install -r requirements.txt
```

## 🚀 Usage

Start the proxy:

```bash
python src/main.py
```

By default, it binds to:

```
localhost:80
```

and forwards traffic to:

```
github.com:443 (TLS enabled)
```

## 🔌 Plugin System

Each target has its own plugin file:

```
plugins/<host>.<port>.py
```

Example:

```
plugins/github.com.443.py
```

### Plugin API

An example plugin was created for users to use it like a template for their own plugins.  
It has the basic functionality to make a simple web service work under the proxy.  
Find it [here](/src/plugins/simpleplugin.example.443.py).  
  
Each plugin must define:

```python
def modify_request(request: HttpRequest) -> HttpRequest:
    ...

def modify_response(response: HttpResponse) -> HttpResponse:
    ...
```

### HttpRequest structure

```python
@dataclass
class HttpRequest:
    method: bytes
    target: bytes
    headers: list[tuple[bytes, bytes]]
    body: bytes
```

### HttpResponse structure

```python
@dataclass
class HttpResponse:
    status_code: int
    headers: list[tuple[bytes, bytes]]
    body: bytes
```

## 🧪 Example Plugin Behavior

* Rewrite `Host` header
* Modify `Origin` / `Referer`
* Rewrite redirect locations

## 🛑 Stop Route

A random stop route is generated at runtime.

Visiting:

```
http://127.0.0.1:80/<random-stop-id>
```

will shutdown the proxy.

## ⚠️ Limitations

* HTTP/2 not supported
* No streaming optimization (full body buffering)
* No async I/O (thread-based only)
* No full TLS interception (MITM HTTPS not implemented)
* Basic connection handling (keep-alive partially supported)

---

## 📜 Disclaimer

This tool is intended for:

* learning HTTP internals
* debugging
* controlled security research

Do not use it to intercept traffic without explicit authorization.
