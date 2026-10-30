// Admin login, step 1: send the user to GitHub. Client ID/secret live in the
// Cloudflare Pages project settings (GITHUB_CLIENT_ID, GITHUB_CLIENT_SECRET).
export async function onRequestGet({ request, env }) {
  const url = new URL(request.url);
  const state = crypto.randomUUID();
  const gh = new URL("https://github.com/login/oauth/authorize");
  gh.searchParams.set("client_id", env.GITHUB_CLIENT_ID);
  gh.searchParams.set("redirect_uri", `${url.origin}/api/callback`);
  gh.searchParams.set("scope", "repo,user");
  gh.searchParams.set("state", state);
  return new Response(null, {
    status: 302,
    headers: {
      Location: gh.toString(),
      "Set-Cookie": `ts_oauth_state=${state}; Path=/api; HttpOnly; Secure; SameSite=Lax; Max-Age=600`,
      "Cache-Control": "no-store",
      "X-Robots-Tag": "noindex",
    },
  });
}
