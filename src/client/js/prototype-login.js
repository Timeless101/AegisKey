import { request, ApiError } from "./api.js";

// The existing Python login only verifies credentials; it creates no session.
// Do not feed this result into acceptSession or unlock a vault based on a user ID.
export async function checkPrototypeLogin({ email, password }) {
  const result = await request("/auth/login", {
    method: "POST",
    body: { email, password },
    anonymous: true,
    credentials: "omit",
  });
  if (
    result?.verified !== true ||
    result.session_created !== false ||
    !result.user ||
    typeof result.user.id !== "string" ||
    !result.user.id ||
    typeof result.user.email !== "string" ||
    !result.user.email
  ) {
    // Reject the old [email, userid, encryption_key] response as well as null/200.
    throw new ApiError(
      "The login API returned an unexpected response. Update the Python route before continuing.",
    );
  }
  return { id: result.user.id, email: result.user.email };
}
