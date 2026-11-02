const defaults = {
  apiBaseUrl: "/api",
  loginMode: "password",
  enableDemo: true,
  requestTimeoutMs: 15000,
};
export const config = { ...defaults, ...window.AEGIS_CONFIG };
let csrfToken = null;
let unauthorizedHandler = () => {};
export class ApiError extends Error {
  constructor(message, status = 0, code = "") {
    super(message);
    this.name = "ApiError";
    this.status = status;
    this.code = code;
  }
}
export function onUnauthorized(callback) {
  unauthorizedHandler = callback;
}
export function setCSRF(token) {
  csrfToken = token || null;
}
export async function request(
  path,
  { method = "GET", body, anonymous = false } = {},
) {
  const controller = new AbortController();
  const timeout = setTimeout(() => controller.abort(), config.requestTimeoutMs);
  try {
    const headers = { Accept: "application/json" };
    if (body !== undefined) headers["Content-Type"] = "application/json";
    if (!["GET", "HEAD"].includes(method) && csrfToken)
      headers["X-CSRF-Token"] = csrfToken;
    const response = await fetch(
      `${config.apiBaseUrl.replace(/\/$/, "")}${path}`,
      {
        method,
        headers,
        credentials: "include",
        signal: controller.signal,
        ...(body !== undefined ? { body: JSON.stringify(body) } : {}),
        cache: "no-store",
      },
    );
    const isJSON = response.headers
      .get("content-type")
      ?.includes("application/json");
    const data =
      response.status === 204 ? null : isJSON ? await response.json() : null;
    if (!response.ok) {
      if (response.status === 401 && !anonymous) unauthorizedHandler();
      const messages = {
        401: anonymous
          ? "Your sign-in details could not be verified."
          : "Your session has expired. Please sign in again.",
        403: "You do not have permission for this action.",
        423: "Your vault is locked. Unlock it to continue.",
        429: "Too many attempts. Please wait a moment and try again.",
        404: "This item could not be found.",
      };
      // Do not render raw backend responses: they can expose debug details or secrets.
      throw new ApiError(
        messages[response.status] ||
          "The request could not be completed. Please try again.",
        response.status,
        data?.error?.code || "",
      );
    }
    if (!isJSON && response.status !== 204)
      throw new ApiError(
        "The server did not return the expected JSON response.",
        response.status,
      );
    return data;
  } catch (error) {
    if (error instanceof ApiError) throw error;
    throw new ApiError(
      error.name === "AbortError"
        ? "The server took too long to respond. Please try again."
        : "Cannot reach AegisKey. Check your connection and try again.",
    );
  } finally {
    clearTimeout(timeout);
  }
}
export const api = {
  session: () => request("/auth/me", { anonymous: true }),
  login: (data) =>
    request("/auth/login", { method: "POST", body: data, anonymous: true }),
  verifyMFA: (data) =>
    request("/auth/mfa/verify", {
      method: "POST",
      body: data,
      anonymous: true,
    }),
  register: (data) =>
    request("/auth/register", { method: "POST", body: data, anonymous: true }),
  resetPassword: (data) =>
    request("/auth/password/reset", {
      method: "POST",
      body: data,
      anonymous: true,
    }),
  setupVault: (data) => request("/vault/setup", { method: "POST", body: data }),
  recover: (data) =>
    request("/auth/password/reset-request", {
      method: "POST",
      body: data,
      anonymous: true,
    }),
  logout: () => request("/auth/logout", { method: "POST" }),
  lock: () => request("/vault/lock", { method: "POST" }),
  unlock: (data) => request("/vault/unlock", { method: "POST", body: data }),
  items: () => request("/items"),
  item: (id) => request(`/items/${encodeURIComponent(id)}`),
  create: (data) => request("/items", { method: "POST", body: data }),
  update: (id, data) =>
    request(`/items/${encodeURIComponent(id)}`, {
      method: "PATCH",
      body: data,
    }),
  remove: (id) =>
    request(`/items/${encodeURIComponent(id)}`, { method: "DELETE" }),
  reveal: (id) =>
    request(`/items/${encodeURIComponent(id)}/reveal`, { method: "POST" }),
};
