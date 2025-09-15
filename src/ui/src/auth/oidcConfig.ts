const req = (k: string, v?: string) => {
  if (!v) throw new Error(`Missing env: ${k}`);
  return v;
};

export const oidcConfig = {
  authority: req("VITE_OIDC_AUTHORITY", import.meta.env.VITE_OIDC_AUTHORITY),
  client_id: req("VITE_OIDC_CLIENT_ID", import.meta.env.VITE_OIDC_CLIENT_ID),
  redirect_uri: req("VITE_OIDC_REDIRECT_URI", import.meta.env.VITE_OIDC_REDIRECT_URI),
  post_logout_redirect_uri: req("VITE_OIDC_POST_LOGOUT_REDIRECT_URI", import.meta.env.VITE_OIDC_POST_LOGOUT_REDIRECT_URI),
  client_secret: req("VITE_OIDC_CLIENT_SECRET", import.meta.env.VITE_OIDC_CLIENT_SECRET),
  response_type: "code",
  scope: import.meta.env.VITE_OIDC_SCOPE || "openid email profile uid",
  automaticSilentRenew: true,
  loadUserInfo: true,
    metadata: {
    issuer: "https://login-stg.pwc.com/openam/oauth2/realms/root/realms/pwc",
    authorization_endpoint: "https://login-stg.pwc.com/openam/oauth2/realms/root/realms/pwc/authorize",
    token_endpoint:        "https://login-stg.pwc.com/openam/oauth2/realms/root/realms/pwc/access_token",
    userinfo_endpoint:     "https://login-stg.pwc.com/openam/oauth2/realms/root/realms/pwc/userinfo",
    jwks_uri:              "https://login-stg.pwc.com/openam/oauth2/realms/root/realms/pwc/connect/jwk_uri",
    end_session_endpoint:  "https://login-stg.pwc.com/openam/oauth2/realms/root/realms/pwc/connect/endSession",
    introspection_endpoint:"https://login-stg.pwc.com/openam/oauth2/realms/root/realms/pwc/tokeninfo",
    },
} as const;