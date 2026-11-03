import test from "node:test";
import assert from "node:assert/strict";
import { createServer } from "node:http";
import { once } from "node:events";
import { formatDate } from "../js/utils.js";

globalThis.window = { AEGIS_CONFIG: {} };
const { createLegacyApi, mapCredential } = await import("../js/legacy-api.js");
const response = {
  cred_id: 3,
  userid: 1,
  service: "Existing API example",
  username: "qa@example.invalid",
  password: "ENCRYPTED_TEST_VALUE",
  comment: "Fictional response from the existing route.",
  editeddate: "2026-11-03 10:30:00",
};

test("existing credential fields are mapped without ciphertext, owner IDs or invented creation dates", () => {
  const item = mapCredential({ ...response, unexpected: "extra" }, 3);
  assert.equal(item.id, "3");
  assert.equal(item.name, response.service);
  assert.equal(item.username, response.username);
  assert.equal(item.notes, response.comment);
  assert.equal(item.updated_at, "2026-11-03T10:30:00");
  assert.equal(item.created_at, null);
  for (const field of ["password", "userid", "unexpected"])
    assert.equal(field in item, false);
  assert.equal(formatDate(item.created_at), "Unknown");
  assert.equal(
    mapCredential({ ...response, editeddate: "invalid date" }, 3).updated_at,
    null,
  );
  assert.throws(
    () => mapCredential({ ...response, cred_id: 4 }, 3),
    /unexpected response/,
  );
  assert.throws(() => mapCredential({ cred_id: 3 }, 3), /unexpected response/);
});

test("real HTTP integration uses GET /credentials/3, without cookies or auth", async () => {
  const calls = [];
  const server = createServer((req, res) => {
    calls.push({ path: req.url, method: req.method, headers: req.headers });
    res.setHeader("Content-Type", "application/json");
    if (req.url !== "/credentials/3") {
      res.writeHead(404);
      res.end("{}");
      return;
    }
    res.end(JSON.stringify(response));
  });
  server.listen(0, "127.0.0.1");
  await once(server, "listening");
  try {
    const adapter = createLegacyApi({
      baseUrl: `http://127.0.0.1:${server.address().port}/`,
      credentialIds: [3],
      timeoutMs: 2000,
    });
    const result = await adapter.items();
    assert.equal(result.items[0].name, response.service);
    assert.equal((await adapter.item("3")).notes, response.comment);
    assert.equal(calls.length, 2);
    for (const call of calls) {
      assert.equal(call.path, "/credentials/3");
      assert.equal(call.method, "GET");
      assert.equal(call.headers.cookie, undefined);
      assert.equal(call.headers.authorization, undefined);
      assert.equal(call.headers["x-csrf-token"], undefined);
    }
    await assert.rejects(adapter.item("4"), /not part of/);
    for (const method of ["create", "update", "remove", "reveal"])
      await assert.rejects(adapter[method]("3", {}));
    assert.equal(
      calls.length,
      2,
      "unsupported actions must not issue any request",
    );
    const missing = createLegacyApi({
      baseUrl: `http://127.0.0.1:${server.address().port}`,
      credentialIds: [4],
      timeoutMs: 2000,
    });
    await assert.rejects(
      missing.items(),
      (error) => error.status === 404 && error.message.includes("Credential 4"),
    );
  } finally {
    server.closeAllConnections();
    await new Promise((resolve) => server.close(resolve));
  }
});

test("legacy requests use omit credentials and report network/JSON failures without fake fallback data", async () => {
  const original = globalThis.fetch;
  let options;
  const adapter = createLegacyApi({
    baseUrl: "http://127.0.0.1:8000",
    credentialIds: [3],
    timeoutMs: 20,
  });
  try {
    globalThis.fetch = async (url, args) => {
      options = args;
      return new Response(JSON.stringify(response));
    };
    await adapter.items();
    assert.equal(options.credentials, "omit");
    assert.equal(options.cache, "no-store");
    assert.deepEqual(Object.keys(options.headers), ["Accept"]);
    globalThis.fetch = async () => new Response("<html>Error</html>");
    await assert.rejects(adapter.items(), /valid JSON/);
    globalThis.fetch = async () => {
      throw new TypeError("Network error");
    };
    await assert.rejects(adapter.items(), /Start FastAPI/);
    globalThis.fetch = async (url, { signal }) =>
      new Promise((resolve, reject) =>
        signal.addEventListener("abort", () =>
          reject(new DOMException("Aborted", "AbortError")),
        ),
      );
    await assert.rejects(adapter.items(), /too long/);
  } finally {
    globalThis.fetch = original;
  }
  assert.throws(
    () =>
      createLegacyApi({ baseUrl: "http://127.0.0.1:8000", credentialIds: [] }),
    /valid test credential/,
  );
});
