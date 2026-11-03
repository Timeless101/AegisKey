import test from "node:test";
import assert from "node:assert/strict";

globalThis.window = {
  AEGIS_CONFIG: { apiBaseUrl: "http://127.0.0.1:8000", requestTimeoutMs: 30 },
};
const { checkPrototypeLogin } = await import("../js/prototype-login.js");
const { setCSRF } = await import("../js/api.js");

test("prototype login sends the current JSON contract without cookies or CSRF leakage", async () => {
  const original = globalThis.fetch;
  let call;
  globalThis.fetch = async (url, options) => {
    call = { url, options };
    return Response.json({
      verified: true,
      session_created: false,
      user: { id: "7", email: "qa@example.invalid" },
      ignored: "not copied",
    });
  };
  try {
    setCSRF("production-csrf-must-not-be-sent");
    const user = await checkPrototypeLogin({
      email: "qa@example.invalid",
      password: "Fictional-test-password!",
    });
    assert.deepEqual(user, { id: "7", email: "qa@example.invalid" });
    assert.equal(call.url, "http://127.0.0.1:8000/auth/login");
    assert.equal(call.options.credentials, "omit");
    assert.equal(call.options.method, "POST");
    assert.equal(call.options.headers["X-CSRF-Token"], undefined);
    assert.deepEqual(JSON.parse(call.options.body), {
      email: "qa@example.invalid",
      password: "Fictional-test-password!",
    });
  } finally {
    globalThis.fetch = original;
    setCSRF(null);
  }
});
test("prototype login rejects raw key tuples, null, and unverified or session responses", async () => {
  const original = globalThis.fetch;
  try {
    for (const data of [
      null,
      ["qa@example.invalid", 7, "SERVER-KEY"],
      {},
      {
        verified: false,
        session_created: false,
        user: { id: "7", email: "qa@example.invalid" },
      },
      {
        verified: true,
        session_created: true,
        user: { id: "7", email: "qa@example.invalid" },
      },
    ]) {
      globalThis.fetch = async () => Response.json(data);
      await assert.rejects(
        checkPrototypeLogin({ email: "qa@example.invalid", password: "test" }),
        /unexpected response/,
      );
    }
    globalThis.fetch = async () =>
      Response.json({ detail: "PRIVATE DEBUG" }, { status: 401 });
    await assert.rejects(
      checkPrototypeLogin({ email: "qa@example.invalid", password: "test" }),
      (error) =>
        error.status === 401 && !error.message.includes("PRIVATE DEBUG"),
    );
  } finally {
    globalThis.fetch = original;
  }
});
