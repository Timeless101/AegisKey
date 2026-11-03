export const escapeHTML = (value) =>
  String(value ?? "").replace(
    /[&<>"']/g,
    (c) =>
      ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" })[
        c
      ],
  );
export function safeURL(value) {
  try {
    const u = new URL(value);
    return ["https:", "http:"].includes(u.protocol) ? u.href : "";
  } catch {
    return "";
  }
}
export function displayHost(value) {
  try {
    return new URL(value).hostname.replace(/^www\./, "");
  } catch {
    return "";
  }
}
export function formatDate(value) {
  if (!value) return "Unknown";
  const d = new Date(value);
  return Number.isNaN(d.getTime())
    ? "Unknown"
    : d.toLocaleDateString("en-GB", {
        day: "numeric",
        month: "short",
        year: "numeric",
      });
}
export function randomInt(max) {
  const limit = Math.floor(0x100000000 / max) * max;
  const data = new Uint32Array(1);
  do {
    crypto.getRandomValues(data);
  } while (data[0] >= limit);
  return data[0] % max;
}
export function generatePassword(length, options) {
  const groups = [
    options.uppercase && "ABCDEFGHJKLMNPQRSTUVWXYZ",
    options.lowercase && "abcdefghijkmnopqrstuvwxyz",
    options.numbers && "23456789",
    options.symbols && "!@#$%&*+-=?",
  ].filter(Boolean);
  if (!groups.length) throw new Error("Select at least one character type.");
  const alphabet = groups.join("");
  const chars = groups.map((group) => group[randomInt(group.length)]);
  while (chars.length < length)
    chars.push(alphabet[randomInt(alphabet.length)]);
  for (let i = chars.length - 1; i > 0; i--) {
    const j = randomInt(i + 1);
    [chars[i], chars[j]] = [chars[j], chars[i]];
  }
  return chars.join("");
}
// This is a composition hint, not a password-strength or breach assessment.
export function passwordHint(value) {
  if (!value) return { label: "No password", level: 0 };
  const count = [/[a-z]/, /[A-Z]/, /[0-9]/, /[^a-zA-Z0-9]/].filter((r) =>
    r.test(value),
  ).length;
  if (value.length >= 16 && count >= 3)
    return { label: "Long & varied", level: 3 };
  if (value.length >= 12 && count >= 2)
    return { label: "Good length", level: 2 };
  return { label: "Consider a longer password", level: 1 };
}
