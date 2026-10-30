// Admin login.
//  - Client: password form. The password is checked against the Cloudflare secret ADMIN_PASSWORD;
//    on success the admin gets ADMIN_GITHUB_TOKEN (a fine-grained token limited to this repo's files).
//  - Developer: "Log in with GitHub" (OAuth app; GITHUB_CLIENT_ID / GITHUB_CLIENT_SECRET).
const SECURITY = { "Cache-Control": "no-store", "X-Robots-Tag": "noindex", "X-Frame-Options": "DENY" };

function page(body, status = 200) {
  return new Response(`<!doctype html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1"><meta name="robots" content="noindex">
<title>Two Stooges Admin – Sign in</title>
<style>
body{margin:0;min-height:100vh;display:grid;place-items:center;background:#123c2f;font:16px/1.4 system-ui,sans-serif;color:#1a1c1b}
.box{background:#fff;border-radius:10px;padding:28px 24px;width:min(340px,90vw);box-shadow:0 10px 30px rgba(0,0,0,.3);text-align:center}
img{width:170px;margin-bottom:12px}h1{font-size:20px;margin:0 0 16px;color:#123c2f}
input{width:100%;box-sizing:border-box;font-size:18px;padding:12px;border:2px solid #cfd6d2;border-radius:6px;margin-bottom:12px}
input:focus{outline:3px solid #f0c044;border-color:#123c2f}
button{width:100%;font-size:18px;font-weight:700;padding:12px;border:0;border-radius:6px;background:#ffce51;color:#123c2f;cursor:pointer}
.err{color:#b3261e;font-weight:600;margin:0 0 12px}.dev{display:block;margin-top:18px;font-size:13px;color:#5b655f}
</style></head><body><div class="box">${body}</div></body></html>`,
    { status, headers: { "Content-Type": "text/html; charset=utf-8", ...SECURITY } });
}

function form(error = "") {
  return page(`<img src="/assets/img/brand/two-stooges-logo.webp" alt="Two Stooges">
<h1>Admin sign in</h1>
${error ? `<p class="err">${error}</p>` : ""}
<form method="post" action="/api/auth">
<label for="pw" style="position:absolute;left:-9999px">Password</label>
<input id="pw" name="password" type="password" placeholder="Password" autocomplete="current-password" required autofocus>
<button type="submit">Sign in</button></form>
<a class="dev" href="/api/auth?github=1">Developer: log in with GitHub</a>`, error ? 401 : 200);
}

// Sends the token to the admin window that opened this popup (same site only).
function handoff(origin, status, content) {
  const msg = JSON.stringify(`authorization:github:${status}:${JSON.stringify(content)}`);
  return page(`<p>Signing in…</p><script>
(function(){var o=${JSON.stringify(origin)};
function r(e){if(e.origin!==o)return;window.opener.postMessage(${msg},o);window.removeEventListener("message",r);setTimeout(function(){window.close()},300);}
window.addEventListener("message",r);
if(window.opener)window.opener.postMessage("authorizing:github",o);else document.body.textContent="Please open the Admin from the website footer.";})();
</script>`);
}

async function sameText(a, b) {
  const enc = new TextEncoder();
  const [x, y] = await Promise.all([crypto.subtle.digest("SHA-256", enc.encode(a)), crypto.subtle.digest("SHA-256", enc.encode(b))]);
  const u = new Uint8Array(x), v = new Uint8Array(y);
  let diff = 0;
  for (let i = 0; i < u.length; i++) diff |= u[i] ^ v[i];
  return diff === 0;
}

export async function onRequestGet({ request, env }) {
  const url = new URL(request.url);
  if (!url.searchParams.has("github")) return form();
  const state = crypto.randomUUID();
  const gh = new URL("https://github.com/login/oauth/authorize");
  gh.searchParams.set("client_id", env.GITHUB_CLIENT_ID);
  gh.searchParams.set("redirect_uri", `${url.origin}/api/callback`);
  gh.searchParams.set("scope", "repo");
  gh.searchParams.set("state", state);
  return new Response(null, { status: 302, headers: { Location: gh.toString(), ...SECURITY,
    "Set-Cookie": `ts_oauth_state=${state}; Path=/api; HttpOnly; Secure; SameSite=Lax; Max-Age=600` } });
}

export async function onRequestPost({ request, env }) {
  const url = new URL(request.url);
  const data = await request.formData().catch(() => null);
  const pw = (data && data.get("password")) || "";
  if (!env.ADMIN_PASSWORD || !env.ADMIN_GITHUB_TOKEN) return form("Admin login isn't set up yet. Call your web designer.");
  const clean = (v) => String(v).trim().replace(/^[`'"]+|[`'"]+$/g, "").trim();
  if (!(await sameText(clean(pw), clean(env.ADMIN_PASSWORD)))) {
    await new Promise((r) => setTimeout(r, 1500)); // slow down guessing
    return form("Wrong password. Try again.");
  }
  return handoff(url.origin, "success", { token: env.ADMIN_GITHUB_TOKEN, provider: "github" });
}
