import test from "node:test";
import assert from "node:assert/strict";
import { webcrypto } from "node:crypto";
import { generatePassword, safeURL, escapeHTML } from "../js/utils.js";
import { createDemo } from "../js/demo.js";
if (!globalThis.crypto) globalThis.crypto = webcrypto;

test("generator creates requested length and includes every selected character group", () => {
  for (const length of [8, 24, 64])
    for (let n = 0; n < 50; n++) {
      const value = generatePassword(length, {
        uppercase: true,
        lowercase: true,
        numbers: true,
        symbols: true,
      });
      assert.equal(value.length, length);
      for (const pattern of [/[A-Z]/, /[a-z]/, /[2-9]/, /[!@#$%&*+\-=?]/])
        assert.match(value, pattern);
      assert.doesNotMatch(value, /[01OIl]/);
    }
});
test("generator rejects empty options and honors numbers-only selection", () => {
  assert.throws(() => generatePassword(24, {}));
  assert.match(generatePassword(64, { numbers: true }), /^[2-9]{64}$/);
});
test("user content is escaped and unsafe website protocols are rejected", () => {
  assert.equal(
    escapeHTML('<img src=x onerror="alert(1)">'),
    "&lt;img src=x onerror=&quot;alert(1)&quot;&gt;",
  );
  for (const value of [
    "javascript:alert(1)",
    "data:text/html,test",
    "file:///tmp/test",
    "invalid",
  ])
    assert.equal(safeURL(value), "");
  assert.equal(
    safeURL("https://example.invalid/path"),
    "https://example.invalid/path",
  );
});
test("demo CRUD is isolated, password reads are explicit, blank edits preserve a password", async () => {
  const first = createDemo(),
    second = createDemo();
  const item = await first.create({
    type: "login",
    name: "Test only",
    username: "qa@example.invalid",
    password: "Fictional-pass!42",
    collection: "Personal",
  });
  assert.ok(item.id);
  assert.equal(item.password, undefined);
  assert.equal(
    (await first.items()).items.some((x) => "password" in x),
    false,
  );
  assert.equal(
    (await second.items()).items.some((x) => x.id === item.id),
    false,
  );
  await first.update(item.id, { name: "Updated" });
  assert.equal((await first.reveal(item.id)).password, "Fictional-pass!42");
  await first.remove(item.id);
  assert.equal(
    (await first.items()).items.some((x) => x.id === item.id),
    false,
  );
});

globalThis.window = {
  AEGIS_CONFIG: { apiBaseUrl: "/api", requestTimeoutMs: 30 },
};
const { request, setCSRF, onUnauthorized } = await import("../js/api.js");
test("API adapter sends cookies and CSRF without logging or persisting bearer tokens", async () => {
  const original = globalThis.fetch;
  let received;
  globalThis.fetch = async (url, options) => {
    received = { url, options };
    return new Response(JSON.stringify({ id: "1" }), {
      headers: { "Content-Type": "application/json" },
    });
  };
  try {
    setCSRF("csrf-test");
    await request("/items", { method: "POST", body: { name: "Test" } });
    assert.equal(received.url, "/api/items");
    assert.equal(received.options.credentials, "include");
    assert.equal(received.options.headers["X-CSRF-Token"], "csrf-test");
    assert.equal(received.options.headers.Authorization, undefined);
    assert.equal(received.options.cache, "no-store");
  } finally {
    globalThis.fetch = original;
    setCSRF(null);
  }
});
test("API adapter rejects HTML and does not expose sensitive server error messages", async () => {
  const original = globalThis.fetch;
  try {
    globalThis.fetch = async () =>
      new Response("<html>Error</html>", {
        headers: { "Content-Type": "text/html" },
      });
    await assert.rejects(request("/items"), /expected JSON/);
    globalThis.fetch = async () =>
      new Response(JSON.stringify({ detail: "SECRET-DEBUG-DATA" }), {
        status: 500,
        headers: { "Content-Type": "application/json" },
      });
    await assert.rejects(
      request("/items"),
      (err) => !err.message.includes("SECRET-DEBUG-DATA") && err.status === 500,
    );
  } finally {
    globalThis.fetch = original;
  }
});
test("expired sessions trigger the handler, anonymous sign-in failures do not", async () => {
  const original = globalThis.fetch;
  let count = 0;
  onUnauthorized(() => count++);
  globalThis.fetch = async () =>
    new Response("{}", {
      status: 401,
      headers: { "Content-Type": "application/json" },
    });
  try {
    await assert.rejects(request("/auth/me", { anonymous: true }));
    assert.equal(count, 0);
    await assert.rejects(request("/items"));
    assert.equal(count, 1);
  } finally {
    globalThis.fetch = original;
    onUnauthorized(() => {});
  }
});
test("requests time out without hanging the interface", async () => {
  const original = globalThis.fetch;
  globalThis.fetch = async (url, { signal }) =>
    new Promise((resolve, reject) =>
      signal.addEventListener("abort", () =>
        reject(new DOMException("Aborted", "AbortError")),
      ),
    );
  try {
    await assert.rejects(request("/items"), /too long/);
  } finally {
    globalThis.fetch = original;
  }
});
