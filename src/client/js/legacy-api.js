import { ApiError, config } from "./api.js";

// Temporary bridge to the existing Python route. This is NOT authentication.
// Only the explicitly configured IDs are loaded; no ID enumeration or fake records.
export function mapCredential(data, expectedId) {
  if (
    !data ||
    typeof data !== "object" ||
    Array.isArray(data) ||
    String(data.cred_id) !== String(expectedId) ||
    typeof data.service !== "string" ||
    typeof data.username !== "string"
  ) {
    throw new ApiError("The credential API returned an unexpected response.");
  }
  // SQLite's local timestamp has a space separator. Do not invent a timezone.
  const updatedAt =
    typeof data.editeddate === "string"
      ? data.editeddate.replace(/^(\d{4}-\d{2}-\d{2}) /, "$1T")
      : null;
  return {
    id: String(data.cred_id),
    type: "login",
    name: data.service,
    username: data.username,
    notes: typeof data.comment === "string" ? data.comment : "",
    updated_at:
      updatedAt && !Number.isNaN(new Date(updatedAt).getTime())
        ? updatedAt
        : null,
    created_at: null,
    url: "",
    collection: "Personal", // Presentation default; this API has no collection field.
    favorite: false,
    // Never copy userid, password/ciphertext, or arbitrary server fields to UI state.
  };
}

export function createLegacyApi({
  baseUrl = config.legacyApiBaseUrl,
  credentialIds = config.legacyCredentialIds,
  timeoutMs = config.requestTimeoutMs,
} = {}) {
  const ids = [...new Set((credentialIds || []).map(String))];
  if (!ids.length || ids.some((id) => !/^[1-9]\d*$/.test(id))) {
    throw new ApiError("Configure at least one valid test credential ID.");
  }
  const base = String(baseUrl || "").replace(/\/$/, "");
  if (!base) throw new ApiError("Configure the URL of your local test API.");

  async function item(id) {
    if (!ids.includes(String(id))) {
      throw new ApiError(
        "This credential is not part of the configured API test.",
      );
    }
    const controller = new AbortController();
    const timeout = setTimeout(() => controller.abort(), timeoutMs);
    try {
      const response = await fetch(
        `${base}/credentials/${encodeURIComponent(id)}`,
        {
          method: "GET",
          headers: { Accept: "application/json" },
          // The existing route has no auth and uses wildcard CORS. Never send cookies
          // or a production CSRF/token to this separate test origin.
          credentials: "omit",
          cache: "no-store",
          signal: controller.signal,
        },
      );
      if (!response.ok) {
        const message =
          response.status === 404
            ? `Credential ${id} was not found by the test API.`
            : "The local credential API could not complete the request.";
        throw new ApiError(message, response.status);
      }
      let data;
      try {
        data = await response.json();
      } catch {
        throw new ApiError("The credential API did not return valid JSON.");
      }
      return mapCredential(data, id);
    } catch (error) {
      if (error instanceof ApiError) throw error;
      throw new ApiError(
        error.name === "AbortError"
          ? "The local test API took too long to respond. Check that FastAPI is running."
          : "Cannot reach the local test API. Start FastAPI and check its URL and CORS settings.",
      );
    } finally {
      clearTimeout(timeout);
    }
  }
  const unsupported = async () => {
    throw new ApiError(
      "This existing API connection is read-only. That endpoint is not available yet.",
    );
  };
  return {
    async items() {
      return { items: await Promise.all(ids.map(item)) };
    },
    item,
    create: unsupported,
    update: unsupported,
    remove: unsupported,
    reveal: async () => {
      throw new ApiError(
        "This API returns an encrypted password. No plaintext reveal endpoint is connected.",
      );
    },
    // These only close the local test view; there is no server session to revoke.
    async lock() {},
    async logout() {},
  };
}
