// Keep this file public: never put client secrets, API keys or signing keys here.
window.AEGIS_CONFIG = Object.freeze({
  apiBaseUrl: "/api",
  // 'password' uses /auth/login; 'redirect' starts your self-hosted OIDC/BFF login.
  loginMode: "password",
  enableDemo: true,
  requestTimeoutMs: 15000,
});
