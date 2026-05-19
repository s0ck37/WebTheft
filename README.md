# WebTheft

> A Python framework for impersonating web services through an HTTP proxy in order to study phishing techniques, traffic interception, and web authentication flows in controlled environments.

```text

      ...    .     ...                       ..         s                                          s
  .~`"888x.!**h.-``888h.              . uW8"          :8      .uef^"                  oec :      :8
 dX   `8888   :X   48888>             `t888          .88    :d88E                    @88888     .88
'888x  8888  X88.  '8888>       .u     8888   .     :888ooo `888E            .u      8"*88%    :888ooo
'88888 8888X:8888:   )?""`   ud8888.   9888.z88N  -*8888888  888E .z8k    ud8888.    8b.     -*8888888
 `8888>8888 '88888>.88h.   :888'8888.  9888  888E   8888     888E~?888L :888'8888.  u888888>   8888
   `8" 888f  `8888>X88888. d888 '88%"  9888  888E   8888     888E  888E d888 '88%"   8888R     8888
  -~` '8%"     88" `88888X 8888.+"     9888  888E   8888     888E  888E 8888.+"      8888P     8888
  .H888n.      XHn.  `*88! 8888L       9888  888E  .8888Lu=  888E  888E 8888L        *888>    .8888Lu=
 :88888888x..x88888X.  `!  '8888c. .+ .8888  888"  ^%888*    888E  888E '8888c. .+   4888     ^%888*
 f  ^%888888% `*88888nx"    "88888%    `%888*%"      'Y"    m888N= 888>  "88888%     '888       'Y"
      `"**"`    `"**""        "YP'        "`                 `Y"   888     "YP'       88R
                                                                  J88"                88>
                                                                  @%                  48
                                                                :"                    '8
 WebTheft ~ by s0ck37

[main.py] Starting WebTheft
[proxy.py:load_plugin] Loading plugin file src\plugins\github.com.443.py
[proxy.py:load_plugin] Plugin succesfully loaded
[proxy.py:start] Fetch http://localhost:80/12073ce3-d69b-4ec7-aa07-a18fc22d8846 to stop WebTheft
[proxy.py:start] Creating listening socket on localhost:80
[proxy.py:create_listening_socket] Waiting for incomning connections
[proxy.py:handle_client] New client connected -> 127.0.0.1:50600

[plugins/github.com:modify_request] Request for /login
[plugins/github.com:modify_request] Intercepted cookie -> _gh_sess=[REDACTED]
[plugins/github.com:modify_request] Intercepted cookie ->  cpu_bucket=[REDACTED]
[plugins/github.com:modify_request] Intercepted cookie ->  preferred_color_mode=[REDACTED]
[plugins/github.com:modify_request] Intercepted cookie ->  _octo=[REDACTED]
[plugins/github.com:modify_request] Intercepted cookie ->  tz=[REDACTED]
[plugins/github.com:modify_request] Intercepted cookie ->  _device_id=[REDACTED]
[plugins/github.com:modify_request] Intercepted cookie ->  last_write_ms=[REDACTED]
[plugins/github.com:modify_request] Intercepted cookie ->  saved_user_sessions=

[proxy.py:handle_client] New client connected -> 127.0.0.1:50602

[plugins/github.com:modify_request] Request for /u2f/login_fragment?disable_signup=false&is_emu_login=false&mobile_ios=false
[plugins/github.com:modify_request] Intercepted cookie -> _gh_sess=[REDACTED]
[plugins/github.com:modify_request] Intercepted cookie ->  cpu_bucket=[REDACTED]
[plugins/github.com:modify_request] Intercepted cookie ->  preferred_color_mode=[REDACTED]
[plugins/github.com:modify_request] Intercepted cookie ->  _octo=[REDACTED]
[plugins/github.com:modify_request] Intercepted cookie ->  tz=[REDACTED]
[plugins/github.com:modify_request] Intercepted cookie ->  _device_id=[REDACTED]
[plugins/github.com:modify_request] Intercepted cookie ->  last_write_ms=[REDACTED]
[plugins/github.com:modify_request] Intercepted cookie ->  saved_user_sessions=

[proxy.py:handle_client] New client connected -> 127.0.0.1:50606

[plugins/github.com:modify_request] Request for /session

[plugins/github.com:modify_request] Found credentials -> s0ck37:[REDACTED]

[plugins/github.com:modify_request] Intercepted cookie -> _gh_sess=[REDACTED]
[plugins/github.com:modify_request] Intercepted cookie ->  cpu_bucket=[REDACTED]
[plugins/github.com:modify_request] Intercepted cookie ->  preferred_color_mode=[REDACTED]
[plugins/github.com:modify_request] Intercepted cookie ->  _octo=[REDACTED]
[plugins/github.com:modify_request] Intercepted cookie ->  tz=[REDACTED]
[plugins/github.com:modify_request] Intercepted cookie ->  _device_id=[REDACTED]
[plugins/github.com:modify_request] Intercepted cookie ->  last_write_ms=[REDACTED]
[plugins/github.com:modify_request] Intercepted cookie ->  saved_user_sessions=

[proxy.py:handle_client] New client connected -> 127.0.0.1:50608

[plugins/github.com:modify_request] Request for /sessions/two-factor/sms/confirm
[plugins/github.com:modify_request] Intercepted cookie -> _gh_sess=[REDACTED]
[plugins/github.com:modify_request] Intercepted cookie ->  cpu_bucket=[REDACTED]
[plugins/github.com:modify_request] Intercepted cookie ->  preferred_color_mode=[REDACTED]
[plugins/github.com:modify_request] Intercepted cookie ->  _octo=[REDACTED]
[plugins/github.com:modify_request] Intercepted cookie ->  tz=[REDACTED]
[plugins/github.com:modify_request] Intercepted cookie ->  _device_id=[REDACTED]
[plugins/github.com:modify_request] Intercepted cookie ->  last_write_ms=[REDACTED]
[plugins/github.com:modify_request] Intercepted cookie ->  saved_user_sessions=

[proxy.py:handle_client] New client connected -> 127.0.0.1:50610

[plugins/github.com:modify_request] Request for /sessions/two-factor/sms/confirm
[plugins/github.com:modify_request] Intercepted cookie -> _gh_sess=[REDACTED]
[plugins/github.com:modify_request] Intercepted cookie ->  cpu_bucket=[REDACTED]
[plugins/github.com:modify_request] Intercepted cookie ->  preferred_color_mode=[REDACTED]
[plugins/github.com:modify_request] Intercepted cookie ->  _octo=[REDACTED]
[plugins/github.com:modify_request] Intercepted cookie ->  tz=[REDACTED]
[plugins/github.com:modify_request] Intercepted cookie ->  _device_id=[REDACTED]
[plugins/github.com:modify_request] Intercepted cookie ->  last_write_ms=[REDACTED]
[plugins/github.com:modify_request] Intercepted cookie ->  saved_user_sessions=

[proxy.py:handle_client] New client connected -> 127.0.0.1:50612

[plugins/github.com:modify_request] Request for /sessions/two-factor/sms
[plugins/github.com:modify_request] Intercepted cookie -> _gh_sess=[REDACTED]
[plugins/github.com:modify_request] Intercepted cookie ->  cpu_bucket=[REDACTED]
[plugins/github.com:modify_request] Intercepted cookie ->  preferred_color_mode=[REDACTED]
[plugins/github.com:modify_request] Intercepted cookie ->  _octo=[REDACTED]
[plugins/github.com:modify_request] Intercepted cookie ->  tz=[REDACTED]
[plugins/github.com:modify_request] Intercepted cookie ->  _device_id=[REDACTED]
[plugins/github.com:modify_request] Intercepted cookie ->  last_write_ms=[REDACTED]
[plugins/github.com:modify_request] Intercepted cookie ->  saved_user_sessions=

[proxy.py:handle_client] New client connected -> 127.0.0.1:50614

[plugins/github.com:modify_request] Request for /sessions/two-factor

[plugins/github.com:modify_request] SMS OTP Intercepted -> [REDACTED]

[plugins/github.com:modify_request] Intercepted cookie -> _gh_sess=[REDACTED]
[plugins/github.com:modify_request] Intercepted cookie ->  cpu_bucket=[REDACTED]
[plugins/github.com:modify_request] Intercepted cookie ->  preferred_color_mode=[REDACTED]
[plugins/github.com:modify_request] Intercepted cookie ->  _octo=[REDACTED]
[plugins/github.com:modify_request] Intercepted cookie ->  tz=[REDACTED]
[plugins/github.com:modify_request] Intercepted cookie ->  _device_id=[REDACTED]
[plugins/github.com:modify_request] Intercepted cookie ->  last_write_ms=[REDACTED]
[plugins/github.com:modify_request] Intercepted cookie ->  saved_user_sessions=

[proxy.py:handle_client] New client connected -> 127.0.0.1:50647
[proxy.py:handle_http] Stopping the WebTheft proxy
[proxy.py:create_listening_socket] Closing created sockets
[proxy.py:create_listening_socket] Waiting for created threads
[main.py] WebTheft finished
```

## What is WebTheft?

WebTheft is an experimental proxy framework written in Python that acts as an intermediary between a client and a real web service. It forwards traffic to the legitimate target while allowing requests and responses to be intercepted, inspected, and modified through a plugin system.

The purpose of the project is to demonstrate and research how phishing-style proxy attacks and web service impersonation work at a technical level.

Using plugins, WebTheft can:

- impersonate existing websites,
- rewrite requests and responses,
- intercept authentication flows,
- inspect cookies and session data,
- modify headers and redirects,
- and analyze how web clients communicate with remote services.

The included example plugin targets GitHub authentication flows and demonstrates how credential interception techniques used in adversary-in-the-middle phishing attacks operate internally.

---

## Educational Purpose

This project exists for:

- cybersecurity education,
- phishing-awareness research,
- red-team lab simulations,
- protocol experimentation,
- and defensive security analysis.

It is intended to help researchers and students understand the mechanics behind modern credential interception attacks so they can better detect and defend against them.

---

## Warning

This software must only be used in:

- authorized environments,
- isolated labs,
- capture-the-flag exercises,
- or systems you own or have explicit permission to test.

Unauthorized interception of credentials, sessions, or network traffic may be illegal.

The author and contributors are not responsible for misuse of this software.
