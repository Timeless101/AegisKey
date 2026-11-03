// Keep this file public: never put client secrets, API keys or signing keys here.
window.AEGIS_CONFIG = Object.freeze({
  apiBaseUrl: "http://127.0.0.1:8000",
  // Current Python login check; use password/redirect only once real sessions exist.
  loginMode: "prototype",
  enableDemo: true,
  // Existing unauthenticated FastAPI prototype. Disable this for production.
  enableLegacyTestApi: true,
  legacyApiBaseUrl: "http://127.0.0.1:8000",
  legacyCredentialIds: [3],
  requestTimeoutMs: 15000,
});
