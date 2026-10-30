// Admin login, step 2: GitHub sends the user back here; trade the code for a token
// and hand it to the admin window (Decap CMS) on this same site only.
export async function onRequestGet({ request, env }) {
  const url = new URL(request.url);
  const code = url.searchParams.get("code");
  const state = url.searchParams.get("state");
  const cookie = (request.headers.get("Cookie") || "").match(/ts_oauth_state=([\w-]+)/);
  let status = "error", content = { error: "Login failed. Close this window and try again." };

  if (code && state && cookie && cookie[1] === state) {
    const res = await fetch("https://github.com/login/oauth/access_token", {
      method: "POST",
      headers: { "Content-Type": "application/json", Accept: "application/json", "User-Agent": "two-stooges-admin" },
      body: JSON.stringify({ client_id: env.GITHUB_CLIENT_ID, client_secret: env.GITHUB_CLIENT_SECRET, code, redirect_uri: `${url.origin}/api/callback` }),
    });
    const data = await res.json().catch(() => ({}));
    if (data.access_token) { status = "success"; content = { token: data.access_token, provider: "github" }; }
    else if (data.error_description) content = { error: data.error_description };
  }

  const msg = JSON.stringify(`authorization:github:${status}:${JSON.stringify(content)}`);
  const origin = JSON.stringify(url.origin);
  const html = `<!doctype html><meta charset="utf-8"><meta name="robots" content="noindex"><title>Signing in…</title>
<p style="font-family:sans-serif">Signing in…</p>
<script>
(function () {
  var origin = ${origin};
  function receive(e) {
    if (e.origin !== origin) return;
    window.opener.postMessage(${msg}, origin);
    window.removeEventListener("message", receive);
    setTimeout(function () { window.close(); }, 300);
  }
  window.addEventListener("message", receive);
  if (window.opener) window.opener.postMessage("authorizing:github", origin);
  else document.body.textContent = "Please start the login from the Admin page.";
})();
</script>`;
  return new Response(html, {
    headers: {
      "Content-Type": "text/html; charset=utf-8",
      "Cache-Control": "no-store",
      "X-Robots-Tag": "noindex",
      "Set-Cookie": "ts_oauth_state=; Path=/api; HttpOnly; Secure; SameSite=Lax; Max-Age=0",
    },
  });
}
