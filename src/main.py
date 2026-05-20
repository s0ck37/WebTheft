import utils.proxy

banner: str = r"""
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
 🥷 WebTheft Forward intercepting proxy (MITM-capable design)
  ~ by s0ck37
"""

target = (
    "www.instagram.com",
    443,
    True,
)

print(banner)
print("[main.py] Starting WebTheft")
utils.proxy.start(("localhost", 80), target)
print("[main.py] WebTheft finished")
