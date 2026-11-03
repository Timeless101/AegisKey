// Keep this file public: never put client secrets, API keys or signing keys here.
window.AEGIS_CONFIG = Object.freeze({
  apiBaseUrl: "/api",
  // 'password' uses /auth/login; 'redirect' starts your self-hosted OIDC/BFF login.
  loginMode: "password",
  enableDemo: true,
  // Existing unauthenticated FastAPI prototype. Disable this for production.
  enableLegacyTestApi: true,
  legacyApiBaseUrl: "http://127.0.0.1:8000",
  legacyCredentialIds: [3],
  requestTimeoutMs: 15000,
});
