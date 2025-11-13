import os, json, time, base64
from datetime import datetime, timedelta, timezone
import boto3, requests

# === Env vars ===
ISSUER              = os.environ["OIDC_ISSUER"].rstrip("/")
CLIENT_ID           = os.environ["OIDC_CLIENT_ID"]
SECRET_ID           = os.environ["OIDC_SECRET_ID"]              # Secrets Manager name; value is {"OIDC_CLIENT_SECRET":"..."}
REDIRECT_URI        = os.environ["REDIRECT_URI"]                # https://api.<env>.example.com/auth/callback
POST_LOGIN_REDIRECT = os.environ["POST_LOGIN_REDIRECT"]         # https://app.<env>.example.com/
COOKIE_DOMAIN       = os.environ.get("COOKIE_DOMAIN", "")
SESSION_TABLE       = os.environ["SESSION_TABLE"]
SESSION_TTL_HOURS   = int(os.environ.get("SESSION_TTL_HOURS", "24"))
TOKEN_ENDPOINT      = os.environ.get("OIDC_TOKEN_ENDPOINT", f"{ISSUER}/token")  # some IdPs use /access_token

dynamodb = boto3.resource("dynamodb")
sessions = dynamodb.Table(SESSION_TABLE)
secrets  = boto3.client("secretsmanager")

def _json(status, headers, body=""):
    return {"statusCode": status, "headers": headers, "body": body}

def _redirect(location, set_cookie=None):
    h = {"Location": location, "Cache-Control": "no-store", "Pragma": "no-cache"}
    if set_cookie: h["Set-Cookie"] = set_cookie
    return _json(302, h)

def _cookie_str(name, val, max_age):
    parts = [f"{name}={val}", "HttpOnly", "Secure", "SameSite=Lax", "Path=/", f"Max-Age={max_age}"]
    if COOKIE_DOMAIN: parts.append(f"Domain={COOKIE_DOMAIN}")
    return "; ".join(parts)

def _qs(event):
    return event.get("queryStringParameters") or {}

def _cookie(event, key):
    raw = (event.get("headers") or {}).get("cookie") or (event.get("headers") or {}).get("Cookie") or ""
    for part in raw.split(";"):
        k, _, v = part.strip().partition("=")
        if k == key: return v
    return None

def _get_secret(secret_id):
    s = secrets.get_secret_value(SecretId=secret_id)["SecretString"]
    return json.loads(s)

def _sid():
    return base64.urlsafe_b64encode(os.urandom(16)).decode("ascii").rstrip("=")

def handler(event, _ctx):
    # 1) read code/state
    qs = _qs(event)
    code  = qs.get("code")
    state = qs.get("state")
    if not code or not state:
        return _json(400, {"Content-Type":"text/plain"}, "Missing code/state")

    # 2) basic CSRF check via cookie
    cookie_state = _cookie(event, "oauth_state")
    if not cookie_state or cookie_state != state:
        return _json(400, {"Content-Type":"text/plain"}, "Invalid state")

    # 3) exchange code -> tokens (client_secret_post for simplicity)
    client_secret = _get_secret(SECRET_ID)["OIDC_CLIENT_SECRET"]
    form = {
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": REDIRECT_URI,
        "client_id": CLIENT_ID,
        "client_secret": client_secret
    }
    r = requests.post(TOKEN_ENDPOINT, data=form, headers={"Content-Type":"application/x-www-form-urlencoded"}, timeout=10)
    if r.status_code != 200:
        return _json(400, {"Content-Type":"text/plain"}, "Token exchange failed")

    tokens = r.json()  # {access_token, refresh_token, id_token, expires_in, ...}

    # 4) create a simple session
    sid = _sid()
    ttl = int((datetime.now(timezone.utc) + timedelta(hours=SESSION_TTL_HOURS)).timestamp())
    sessions.put_item(Item={
        "sid": sid,
        "user": {},  # keep minimal; you can add claims later
        "tokens": {
            "access_token": tokens.get("access_token"),
            "refresh_token": tokens.get("refresh_token"),
            "id_token": tokens.get("id_token"),
            "token_type": tokens.get("token_type"),
            "scope": tokens.get("scope"),
            "expires_in": tokens.get("expires_in"),
            "obtained_at": int(time.time()),
        },
        "expiresAt": ttl,
        "createdAt": int(time.time())
    })

    # 5) set session cookie, clear helper cookie(s), and redirect to SPA
    max_age = SESSION_TTL_HOURS * 3600
    set_sid = _cookie_str("sid", sid, max_age)

    expires_past = "Thu, 01 Jan 1970 00:00:00 GMT"
    clear = [f"oauth_state=; Expires={expires_past}; Path=/"]
    if COOKIE_DOMAIN: clear = [c + f"; Domain={COOKIE_DOMAIN}" for c in clear]
    set_cookies = f"{set_sid}, {', '.join(clear)}"

    return _redirect(POST_LOGIN_REDIRECT, set_cookie=set_cookies)
