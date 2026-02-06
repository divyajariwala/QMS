import { API_BASE_URL } from "src/config";

/* ---------------- Types ---------------- */

type HttpMethod = "GET" | "POST" | "PUT" | "PATCH" | "DELETE";

interface ApiRequestOptions<TBody = unknown> {
  method?: HttpMethod;
  body?: TBody;
  token?: boolean;
  headers?: HeadersInit;
}

/* ---------------- Core API Method ---------------- */

export async function apiRequest<TResponse, TBody = unknown>(
  endpoint: string,
  options: ApiRequestOptions<TBody> = {}
): Promise<TResponse> {
  const {
    method = "GET",
    body,
    token,
    headers = {},
  } = options;

  const finalHeaders = new Headers(headers);

  if (token) {
      const accessToken = window.sessionStorage.access_token 
    finalHeaders.set("Authorization", `Bearer ${accessToken}`);
  }

  // Set JSON header only when body is JSON
  const isJsonBody =
    body && !(body instanceof FormData) && method !== "GET";

  if (isJsonBody && !finalHeaders.has("Content-Type")) {
    finalHeaders.set("Content-Type", "application/json");
  }

  const res = await fetch(`${API_BASE_URL}${endpoint}`, {
    method,
    headers: finalHeaders,
    body: isJsonBody ? JSON.stringify(body) : (body as BodyInit | undefined),
  });

  if (!res.ok) {
    const text = await res.text();
    throw new Error(`API Error ${res.status}: ${text}`);
  }

  return res.json();
}
