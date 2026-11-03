import { icon } from "./icons.js";
import { api, config, onUnauthorized, setCSRF } from "./api.js";
import { createDemo } from "./demo.js";
import { createLegacyApi } from "./legacy-api.js";
import { checkPrototypeLogin } from "./prototype-login.js";
import {
  escapeHTML as e,
  safeURL,
  displayHost,
  formatDate,
  generatePassword,
} from "./utils.js";

const app = document.querySelector("#app");
const modal = document.querySelector("#modal");
const typeLabels = {
  login: "Password",
  note: "Secure note",
  identity: "Identity",
};
const navigation = [
  ["vault", "home", "All items"],
  ["passwords", "key", "Passwords"],
  ["notes", "note", "Secure notes"],
  ["identities", "identity", "Identities"],
  ["favorites", "star", "Favorites"],
];
let preferences = { theme: "light", autoLock: 5, view: "list" };
try {
  preferences = {
    ...preferences,
    ...JSON.parse(localStorage.getItem("aegiskey.preferences") || "{}"),
  };
} catch {
  /* Storage can be unavailable. */
}
preferences.autoLock = [1, 5, 15, 30].includes(Number(preferences.autoLock))
  ? Number(preferences.autoLock)
  : 5;
preferences.theme = preferences.theme === "dark" ? "dark" : "light";
preferences.view = preferences.view === "grid" ? "grid" : "list";
let state = {
  user: null,
  demo: false,
  legacyTest: false,
  locked: false,
  needsSetup: false,
  route: "vault",
  items: [],
  loading: false,
  error: "",
  query: "",
  tab: "all",
  sort: "name",
  page: 1,
  selected: null,
};
let service = api;
let epoch = 0;
let authPending = false;
let revealTimer;
let secretTimer;
let lastActivity = Date.now();
let modalTrigger = null;
let drawerTrigger = null;
let mfaChallenge = null;
let authView = "login";
let verifiedUser = null;
let lockedNotice = "";
let generated = "";
let generatorOptions = {
  uppercase: true,
  lowercase: true,
  numbers: true,
  symbols: true,
};
let generatorLength = 24;
const pageSize = 8;
const ui = {
  iconButton: (name, label, action, extra = "") =>
    `<button class="icon-btn" type="button" aria-label="${e(label)}" title="${e(label)}" data-action="${action}" ${extra}>${icon(name)}</button>`,
};
function savePreferences() {
  try {
    localStorage.setItem("aegiskey.preferences", JSON.stringify(preferences));
  } catch {}
  document.documentElement.dataset.theme = preferences.theme;
}
savePreferences();
function lockMarker(locked) {
  try {
    if (locked) sessionStorage.setItem("aegiskey.locked", "1");
    else sessionStorage.removeItem("aegiskey.locked");
  } catch {}
}
function wasLocked() {
  try {
    return sessionStorage.getItem("aegiskey.locked") === "1";
  } catch {
    return false;
  }
}
function rememberedEmail() {
  try {
    return localStorage.getItem("aegiskey.email") || "";
  } catch {
    return "";
  }
}
function rememberEmail(email, remember) {
  try {
    if (remember) localStorage.setItem("aegiskey.email", email);
    else localStorage.removeItem("aegiskey.email");
  } catch {}
}
function toast(message, error = false) {
  const node = document.createElement("div");
  node.className = `toast${error ? " error" : ""}`;
  node.innerHTML = icon(error ? "info" : "check");
  const text = document.createElement("span");
  text.textContent = message;
  node.append(text);
  document.querySelector("#toasts").append(node);
  setTimeout(() => node.remove(), 4500);
}
function routeFromHash() {
  const value = location.hash.replace(/^#\//, "").split("?")[0];
  return [
    ...navigation.map((x) => x[0]),
    "personal",
    "work",
    "generator",
    "settings",
  ].includes(value)
    ? value
    : "vault";
}
function currentTitle() {
  return (
    {
      vault: "My vault",
      passwords: "Passwords",
      notes: "Secure notes",
      identities: "Identities",
      favorites: "Favorites",
      personal: "Personal",
      work: "Work",
      generator: "Password generator",
      settings: "Settings",
    }[state.route] || "My vault"
  );
}
function typeIcon(type) {
  return { login: "key", note: "note", identity: "identity" }[type] || "key";
}
function initials(name) {
  return String(name || "AK")
    .trim()
    .split(/\s+/)
    .map((x) => x[0])
    .slice(0, 2)
    .join("")
    .toUpperCase();
}
function brand(item) {
  const known = [
    "github",
    "google",
    "notion",
    "figma",
    "stripe",
    "aws",
    "note",
    "identity",
  ];
  const kind = known.includes(item.brand)
    ? item.brand
    : ["note", "identity"].includes(item.type)
      ? item.type
      : "generic";
  const content = {
    github: icon("github"),
    google: "G",
    notion: "N",
    figma: "F",
    stripe: "S",
    aws: "aws",
    note: icon("note"),
    identity: icon("identity"),
    generic: e(initials(item.name)),
  };
  return `<span class="brand brand-${kind}">${content[kind] || content.generic}</span>`;
}
function footer() {
  return `<footer class="workspace-footer"><span>${icon("shield")} Your data. Your control.</span><span>AegisKey <span aria-hidden="true">·</span> <a href="https://github.com/Timeless101/AegisKey" target="_blank" rel="noopener noreferrer">Open source ${icon("external")}</a></span></footer>`;
}
function clearSecrets() {
  clearTimeout(revealTimer);
  clearTimeout(secretTimer);
  document.querySelectorAll("[data-secret]").forEach((node) => {
    if ("value" in node) node.value = "";
    else node.textContent = "••••••••••••";
  });
}
function closeModal() {
  clearSecrets();
  if (modal.open) modal.close();
  modal.innerHTML = "";
  if (modalTrigger?.isConnected) modalTrigger.focus();
  modalTrigger = null;
}
function closeDrawer() {
  document.querySelector(".app-shell")?.removeAttribute("inert");
  clearSecrets();
  document.querySelector("#drawer-root")?.remove();
  state.selected = null;
  if (drawerTrigger?.isConnected) drawerTrigger.focus();
  drawerTrigger = null;
}
function resetSession() {
  epoch++;
  clearSecrets();
  closeModal();
  closeDrawer();
  state = {
    ...state,
    user: null,
    items: [],
    loading: false,
    error: "",
    query: "",
    selected: null,
    demo: false,
    legacyTest: false,
    locked: false,
    needsSetup: false,
  };
  service = api;
  setCSRF(null);
  generated = "";
  authPending = false;
  mfaChallenge = null;
  verifiedUser = null;
  document.querySelector("#toasts").replaceChildren();
}
onUnauthorized(() => {
  if (!state.user) return;
  resetSession();
  authView = "login";
  renderAuth("Your session has expired. Please sign in again.");
});
function formError(form, message) {
  let node = form.querySelector("[data-form-error]");
  if (!node) {
    node = document.createElement("div");
    node.dataset.formError = "";
    node.className = "form-error";
    node.setAttribute("role", "alert");
    form.prepend(node);
  }
  node.textContent = message;
  node.hidden = false;
}
async function busyForm(form, callback) {
  const buttons = [...form.querySelectorAll("button[type=submit]")];
  buttons.forEach((x) => (x.disabled = true));
  form.querySelector("[data-form-error]")?.setAttribute("hidden", "");
  try {
    await callback();
  } catch (error) {
    if (form.isConnected)
      formError(
        form,
        error.message || "Something went wrong. Please try again.",
      );
  } finally {
    buttons.forEach((x) => (x.disabled = false));
  }
}

function authLayout(content) {
  return `<main id="main-content" class="auth-page"><aside class="auth-story" aria-label="About AegisKey"><span class="wordmark" role="img" aria-label="AegisKey"><img src="assets/mark.svg" alt="" width="35" height="35"><span aria-hidden="true">Aegis<span>Key</span></span></span><div class="story-content"><div class="story-label">${icon("shield")} A little more peace of mind</div><h1>Your digital life.<br>Your keys.<br><span>Your control.</span></h1><p>A quiet place for the things that matter. Keep your passwords, notes, and identities together in your own personal vault.</p><div class="story-features"><span>${icon("check")} Built for self-hosting</span><span>${icon("check")} Open source, by design</span></div></div><footer class="story-footer"><span>Independent. Personal. AegisKey.</span><a href="https://github.com/Timeless101/AegisKey" target="_blank" rel="noopener noreferrer">View on GitHub ${icon("external")}</a></footer></aside><section class="auth-main"><div class="auth-top" ${state.locked || config.loginMode === "prototype" ? 'style="visibility:hidden"' : ""}><span>${authView === "register" ? "Already have an account?" : "New to AegisKey?"}</span><button class="text-btn" data-action="${authView === "register" ? "login-view" : "register-view"}">${authView === "register" ? "Sign in" : "Create an account"}</button></div><div class="auth-card">${content}</div><p class="auth-bottom">${icon("shield")} Your keys to a safer digital life.</p></section></main>`;
}
function passwordField(
  id,
  label,
  autocomplete = "current-password",
  placeholder = "Enter your password",
  required = true,
) {
  return `<div class="field"><label for="${id}">${label}</label><div class="input-icon">${icon("lock")}<input id="${id}" name="password" type="password" autocomplete="${autocomplete}" placeholder="${placeholder}" ${required ? "required" : ""} maxlength="1024" data-secret>${ui.iconButton("eye", "Show password", "toggle-password", `data-target="${id}"`)}</div></div>`;
}
function renderAuth(message = "") {
  clearSecrets();
  document.title = "Sign in · AegisKey";
  const email = rememberedEmail();
  let content = "";
  const heading = `<img class="auth-logo" src="assets/mark.svg" alt="" width="58" height="58">`;
  if (authView === "verified" && verifiedUser && !state.user) {
    content = `${heading}<h2>Login details verified.</h2><p class="muted">Your Python backend accepted your email and password.</p><div class="form-success" role="status"><strong>${e(verifiedUser.email)}</strong><br>User ID: ${e(verifiedUser.id)}</div><p class="auth-subtle">Your current login route checks credentials, but does not create a session or token yet. This result does not unlock or authorize access to a vault.</p><div class="form-stack" style="margin-top:24px"><button class="btn btn-primary full" data-action="login-view">Back to sign in</button>${config.enableLegacyTestApi ? '<button class="btn full" data-action="start-legacy">Open separate read-only API test</button>' : ""}</div>${config.enableLegacyTestApi ? '<p class="auth-subtle">The existing credential API test is separate from this login check.</p>' : ""}`;
    document.title = "Login verified · AegisKey";
  } else if (state.locked && state.needsSetup) {
    content = `${heading}<h2>Make this vault yours.</h2><p class="muted">Choose a separate password to unlock your vault.</p><form id="setup-form" class="form-stack">${passwordField("setup-password", "Vault password", "new-password", "Choose a long vault password")}<div class="field"><label for="setup-confirm">Confirm vault password</label><input id="setup-confirm" name="confirm" type="password" autocomplete="new-password" required maxlength="1024" data-secret placeholder="Repeat your vault password"></div><button type="submit" class="btn btn-primary full">Create my vault ${icon("arrow")}</button></form><p class="auth-subtle">Keep this password safe. Resetting your account password does not automatically restore access to your vault.</p><button class="text-btn" style="margin-top:18px" data-action="logout">Sign out instead</button>`;
  } else if (state.locked) {
    content = `<div class="lock-avatar">${icon("lock")}</div><h2>Your vault is locked</h2><p class="lock-email">${e(state.user?.email || "")}</p><form id="unlock-form" class="form-stack">${lockedNotice ? `<p class="form-error">${e(lockedNotice)}</p>` : ""}${state.demo ? '<p class="form-success">This is a demo vault. You can unlock it without a password.</p>' : passwordField("unlock-password", "Vault password", "current-password", "Enter your vault password")}<button type="submit" class="btn btn-primary full"><span>Unlock vault</span>${icon("arrow")}</button></form><p class="lock-note">${state.demo ? "Demo changes stay in memory until you refresh." : "Enter your vault password to continue your session."}<br><button class="text-btn" data-action="logout" style="margin-top:12px">Sign out instead</button></p>`;
  } else if (authView === "reset") {
    content = `<button class="back-link" data-action="login-view">${icon("arrow")} Back to sign in</button>${heading}<h2>A fresh start.</h2><p class="muted">Reset your account password with your recovery code.</p><form id="reset-form" class="form-stack"><div class="field"><label for="reset-email">Email address</label><input id="reset-email" type="email" name="email" autocomplete="email" required maxlength="254"></div><div class="field"><label for="reset-code">Recovery code from your email</label><input id="reset-code" name="code" autocomplete="one-time-code" required maxlength="512" data-secret></div>${passwordField("reset-password", "New account password", "new-password", "Choose a long, unique password")}<div class="field"><label for="reset-confirm">Confirm new password</label><input id="reset-confirm" name="confirm" type="password" autocomplete="new-password" required maxlength="1024" data-secret></div><button type="submit" class="btn btn-primary full">Reset account password ${icon("arrow")}</button></form><p class="auth-subtle">This changes your account login, not your vault password.</p>`;
  } else if (authView === "recover") {
    content = `<button class="back-link" data-action="login-view">${icon("arrow")} Back to sign in</button>${heading}<h2>Forgot your password?</h2><p class="muted">We'll help you recover access to your account.</p><form id="recover-form" class="form-stack"><div class="field"><label for="recover-email">Email address</label><div class="input-icon">${icon("mail")}<input id="recover-email" name="email" type="email" autocomplete="email" required placeholder="you@example.com" maxlength="254"></div></div><button type="submit" class="btn btn-primary full">Send recovery instructions ${icon("arrow")}</button><button class="btn btn-quiet" type="button" data-action="reset-view">I already have a recovery code</button></form><p class="auth-subtle">Account recovery does not automatically recover your encrypted vault. Your server's recovery policy determines what can be restored.</p>`;
  } else if (authView === "register") {
    content = `${heading}<h2>A space of your own</h2><p class="muted">Create your AegisKey account.</p>${config.loginMode === "redirect" ? `<button class="btn btn-primary full" data-action="redirect-register">Continue to account registration ${icon("arrow")}</button>` : `<form id="register-form" class="form-stack"><div class="field"><label for="register-name">Your name</label><input id="register-name" name="name" autocomplete="name" required maxlength="100" placeholder="Your name"></div><div class="field"><label for="register-email">Email address</label><input id="register-email" name="email" type="email" autocomplete="email" required maxlength="254" placeholder="you@example.com"></div>${passwordField("register-password", "Account password", "new-password", "Choose a long, unique password")}<div class="field"><label for="register-confirm">Confirm password</label><input id="register-confirm" name="confirm" type="password" autocomplete="new-password" required maxlength="1024" placeholder="Repeat your password" data-secret></div><button type="submit" class="btn btn-primary full">Create account ${icon("arrow")}</button></form>`}<p class="auth-subtle">Use a long, unique password. Your server applies its password policy and manages vault setup.</p>`;
  } else if (authView === "mfa") {
    content = `${heading}<h2>One more step</h2><p class="muted">Enter the code from your authenticator app.</p><form id="mfa-form" class="form-stack"><div class="field"><label for="mfa-code">Authentication code</label><input id="mfa-code" name="code" inputmode="numeric" autocomplete="one-time-code" pattern="[0-9]{6,8}" minlength="6" maxlength="8" required placeholder="000000"></div><button type="submit" class="btn btn-primary full">Verify & continue ${icon("arrow")}</button><button type="button" class="btn btn-quiet" data-action="login-view">Back to sign in</button></form>`;
  } else {
    content = `${heading}<h2>Welcome back.</h2><p class="muted">Your keys to a safer digital life.</p>${message ? `<div class="form-error" role="alert" style="margin-bottom:20px">${e(message)}</div>` : ""}${config.loginMode === "redirect" ? `<button class="btn btn-primary full" data-action="redirect-login">Continue to secure sign in ${icon("arrow")}</button><p class="auth-subtle">Sign in through your self-hosted identity provider. You will return here afterwards.</p>` : `<form id="login-form" class="form-stack"><div class="field"><label for="login-email">Email address</label><div class="input-icon">${icon("mail")}<input id="login-email" name="email" type="email" autocomplete="username" value="${e(email)}" required maxlength="254" placeholder="you@example.com"></div></div>${passwordField("login-password", config.loginMode === "prototype" ? "Vault login password" : "Account password")}<div class="auth-options"><label class="checkbox"><input type="checkbox" name="remember" ${email ? "checked" : ""}>Remember email</label>${config.loginMode === "prototype" ? "" : '<button class="text-btn" type="button" data-action="recover-view">Forgot password?</button>'}</div><button type="submit" class="btn btn-primary full"><span>${config.loginMode === "prototype" ? "Test sign in" : "Sign in to your vault"}</span>${icon("arrow")}</button></form>`}${config.enableDemo ? `<div class="auth-demo"><p>Take a look around. No account needed.</p><button class="btn full" data-action="start-demo">${icon("bolt")} Explore the demo vault ${icon("arrow")}</button><p style="margin:10px 0 0;font-size:10px">Fictional data · Nothing is saved</p></div>` : ""}`;
  }
  if (
    !state.locked &&
    authView === "login" &&
    config.loginMode === "prototype"
  ) {
    const note =
      '<p class="field-help" style="margin-top:16px">Development login: verifies your existing Python route. Server sessions are not connected yet.</p>';
    content = content.replace("</form>", "</form>" + note);
  }
  if (!state.locked && authView === "login" && config.enableLegacyTestApi) {
    const testChoice = `<div class="auth-demo"><p>Connect to your existing FastAPI prototype.</p><button class="btn full" data-action="start-legacy">${icon("key")} Open local test API ${icon("arrow")}</button><p style="margin:10px 0 0;font-size:10px">Live test data · Read-only · No login required</p></div>`;
    const demoPosition = content.indexOf('<div class="auth-demo">');
    content =
      demoPosition < 0
        ? content + testChoice
        : content.slice(0, demoPosition) +
          testChoice +
          content.slice(demoPosition);
  }
  app.innerHTML = authLayout(content);
  if (authPending)
    app
      .querySelectorAll("button")
      .forEach((button) => (button.disabled = true));
}
async function acceptSession(data) {
  if (
    !data?.user?.id ||
    !data?.user?.email ||
    typeof data.csrf_token !== "string" ||
    !data.csrf_token
  )
    throw new Error("The server returned an incomplete session.");
  state.user = {
    id: String(data.user.id),
    email: String(data.user.email),
    name: String(data.user.name || data.user.email.split("@")[0]),
    mfa_enabled: Boolean(data.user.mfa_enabled),
  };
  setCSRF(data.csrf_token);
  state.needsSetup = data.vault_initialized === false;
  state.locked = state.needsSetup || data.vault_unlocked !== true;
  lastActivity = Date.now();
  if (state.locked) {
    lockMarker(true);
    renderAuth();
  } else {
    lockMarker(false);
    state.route = routeFromHash();
    renderShell();
    await loadItems();
  }
}
async function startLegacy() {
  if (!config.enableLegacyTestApi) return;
  resetSession();
  try {
    service = createLegacyApi();
    state.legacyTest = true;
    // This is a display context, NOT a successfully authenticated account.
    state.user = {
      id: "local-api-test",
      name: "Local API test",
      email: "Read-only · no authentication",
      mfa_enabled: false,
    };
    state.route = "vault";
    state.page = 1;
    state.tab = "all";
    state.sort = "name";
    lastActivity = Date.now();
    location.hash = "/test-api";
    renderShell();
    await loadItems();
  } catch (error) {
    resetSession();
    authView = "login";
    renderAuth(error.message);
  }
}
function applyLegacyPresentation() {
  if (!state.legacyTest) return;
  app
    .querySelectorAll(
      '[data-action="new-item"], [data-action="favorite"], [data-action="edit-item"], [data-action="delete-item"]',
    )
    .forEach((button) => button.remove());
  app.querySelectorAll('[data-action="quick-copy"]').forEach((button) => {
    button.setAttribute("aria-label", "Copy username");
    button.setAttribute("title", "Copy username");
  });
  const passwordField = app
    .querySelector("#detail-password")
    ?.closest(".detail-field");
  if (passwordField)
    passwordField.innerHTML =
      '<div><label>Password</label><div class="detail-value muted">Encrypted value returned by Python. Reveal is not connected yet.</div></div>';
  const drawerFooter = app.querySelector(".drawer-footer");
  if (drawerFooter)
    drawerFooter.innerHTML =
      '<button class="btn" data-action="close-drawer">Close details</button>';
}
async function startDemo() {
  resetSession();
  state.demo = true;
  service = createDemo();
  state.user = {
    id: "demo",
    email: "diego@aegiskey.dev",
    name: "Diego Wuck",
    mfa_enabled: false,
  };
  state.route = "vault";
  state.locked = false;
  state.query = "";
  state.tab = "all";
  state.page = 1;
  lastActivity = Date.now();
  location.hash = "/vault";
  renderShell();
  await loadItems();
}
function sidebar() {
  return `<div class="menu-overlay" data-action="close-menu"></div><aside class="sidebar" id="sidebar" aria-label="Main navigation"><a class="sidebar-logo" href="#/vault" aria-label="AegisKey home"><span class="wordmark" aria-hidden="true"><img src="assets/mark.svg" alt="" width="35" height="35"><span>Aegis<span>Key</span></span></span></a><p class="sidebar-section">WORKSPACE</p><nav>${navigation.map(([route, name, label]) => `<a class="nav-link ${state.route === route ? "active" : ""}" href="#/${route}" ${state.route === route ? 'aria-current="page"' : ""}>${icon(name)}<span>${label}</span><span class="nav-count">${countFor(route)}</span></a>`).join("")}</nav><p class="sidebar-section">COLLECTIONS</p><nav><a class="nav-link ${state.route === "personal" ? "active" : ""}" href="#/personal"><span class="collection-dot"></span>Personal<span class="nav-count">${state.items.filter((x) => x.collection === "Personal").length}</span></a><a class="nav-link ${state.route === "work" ? "active" : ""}" href="#/work"><span class="collection-dot work"></span>Work<span class="nav-count">${state.items.filter((x) => x.collection === "Work").length}</span></a></nav><p class="sidebar-section">TOOLS</p><nav><a class="nav-link ${state.route === "generator" ? "active" : ""}" href="#/generator">${icon("bolt")}Password generator</a><a class="nav-link ${state.route === "settings" ? "active" : ""}" href="#/settings">${icon("settings")}Settings</a></nav><div class="sidebar-bottom"><div class="sidebar-security">${icon("shield")}<div><strong>${state.legacyTest ? "Local API test" : state.demo ? "Demo workspace" : "Your personal workspace"}</strong><span>${state.legacyTest ? "Live test data · Read-only" : state.demo ? "Fictional data · This session only" : "Self-hosted. Independently yours."}</span></div></div><div class="sidebar-account"><div class="avatar">${e(initials(state.user.name))}</div><div class="account-info"><strong>${e(state.user.name)}</strong><span>${e(state.user.email)}</span></div>${ui.iconButton("logout", "Sign out", "logout")}</div></div></aside>`;
}
function countFor(route) {
  return state.items.filter(
    (x) =>
      route === "vault" ||
      (route === "favorites" && x.favorite) ||
      (route === "passwords" && x.type === "login") ||
      (route === "notes" && x.type === "note") ||
      (route === "identities" && x.type === "identity"),
  ).length;
}
function renderShell() {
  if (!state.user || state.locked) return;
  document.title = `${currentTitle()} · AegisKey`;
  app.innerHTML = `<div class="app-shell">${sidebar()}<div class="workspace"><header class="topbar">${ui.iconButton("menu", "Open navigation", "open-menu", 'aria-controls="sidebar" aria-expanded="false"').replace('class="icon-btn"', 'class="icon-btn mobile-menu"')}<div class="breadcrumb"><span>Workspace</span>${icon("chevron")}<strong>${e(currentTitle())}</strong></div><div class="topbar-actions"><span class="status"><i class="dot"></i>${state.legacyTest ? "Local API test" : state.demo ? "Demo mode" : "Vault unlocked"}</span><button class="btn topbar-lock" data-action="lock">${icon("lock")} ${state.legacyTest ? "Leave test" : "Lock vault"}</button></div></header><main id="main-content" class="content" tabindex="-1">${state.route === "generator" ? generatorPage() : state.route === "settings" ? settingsPage() : vaultPage()}</main></div></div>`;
  if (!["generator", "settings"].includes(state.route)) renderResults();
  if (state.route === "generator") updateGenerated();
  syncMobileNavigation();
  applyLegacyPresentation();
}
function pageHeading(title, subtitle, action = "") {
  return `<div class="page-heading"><div><div class="heading-label"><h1>${e(title)}</h1>${!["generator", "settings"].includes(state.route) ? `<span class="item-total">${baseItems().length}</span>` : ""}</div><p>${e(subtitle)}</p></div>${action}</div>`;
}
function demoBanner() {
  if (state.legacyTest) {
    const paths = config.legacyCredentialIds
      .map((id) => `/credentials/${id}`)
      .join(", ");
    return `<div class="demo-banner">${icon("info")}<span>Local API test · GET ${e(paths)} · Read-only, without authentication. Personal is a display default.</span><button class="text-btn" data-action="logout">Leave test</button></div>`;
  }
  return state.demo
    ? `<div class="demo-banner">${icon("info")}<span>You're exploring a demo vault. Changes are temporary — please use fictional data only.</span><button class="text-btn" data-action="exit-demo">Exit demo</button></div>`
    : "";
}
function vaultPage() {
  return `${pageHeading(currentTitle(), { vault: "A little more organized. A lot more peace of mind.", passwords: "All your logins, in one place.", notes: "Keep the little details close.", identities: "Your personal details, thoughtfully organized.", favorites: "The things you reach for most.", personal: "Your own corner of the digital world.", work: "Keep your work life neatly together." }[state.route], `<button class="btn btn-primary" data-action="new-item">${icon("plus")}<span>New item</span></button>`)}${demoBanner()}<section class="summary" aria-label="Vault overview"><div class="summary-card"><div class="summary-symbol">${icon("key")}</div><div><strong>${countFor("passwords")}</strong><p>Saved passwords</p></div>${icon("chevron")}</div><div class="summary-card"><div class="summary-symbol">${icon("note")}</div><div><strong>${countFor("notes")}</strong><p>Secure notes</p></div>${icon("chevron")}</div><div class="summary-card"><div class="summary-symbol">${icon("star")}</div><div><strong>${countFor("favorites")}</strong><p>Favorites</p></div>${icon("chevron")}</div></section><section class="vault-panel" aria-label="Vault items"><div class="vault-toolbar"><label class="search-box">${icon("search")}<span class="sr-only">Search vault items</span><input id="vault-search" type="search" placeholder="Search your vault…" value="${e(state.query)}" autocomplete="off"><kbd class="search-shortcut">/</kbd></label><div class="toolbar-spacer"></div><label class="sr-only" for="sort-items">Sort items</label><select class="toolbar-select" id="sort-items"><option value="name" ${state.sort === "name" ? "selected" : ""}>Name: A to Z</option><option value="updated" ${state.sort === "updated" ? "selected" : ""}>Recently updated</option><option value="created" ${state.sort === "created" ? "selected" : ""}>Recently added</option></select><div class="view-toggle" role="group" aria-label="Item layout">${["list", "grid"].map((v) => `<button type="button" class="icon-btn ${preferences.view === v ? "active" : ""}" data-action="view-${v}" aria-label="${v === "list" ? "List" : "Grid"} view" aria-pressed="${preferences.view === v}">${icon(v)}</button>`).join("")}</div></div><div class="filter-tabs" role="group" aria-label="Filter item types">${[
    ["all", "All items"],
    ["login", "Passwords"],
    ["note", "Secure notes"],
    ["identity", "Identities"],
  ]
    .map(
      ([key, label]) =>
        `<button class="filter-tab ${state.tab === key ? "active" : ""}" data-action="filter" data-filter="${key}" aria-pressed="${state.tab === key}">${label}<span>${baseItems().filter((x) => key === "all" || x.type === key).length}</span></button>`,
    )
    .join(
      "",
    )}</div><div id="results" aria-live="polite" aria-busy="${state.loading}"></div><div id="panel-footer"></div></section>${footer()}`;
}
function baseItems() {
  return state.items.filter((item) =>
    state.route === "passwords"
      ? item.type === "login"
      : state.route === "notes"
        ? item.type === "note"
        : state.route === "identities"
          ? item.type === "identity"
          : state.route === "favorites"
            ? item.favorite
            : state.route === "personal"
              ? item.collection === "Personal"
              : state.route === "work"
                ? item.collection === "Work"
                : true,
  );
}
function filteredItems() {
  const query = state.query.trim().toLocaleLowerCase();
  return baseItems()
    .filter(
      (x) =>
        (state.tab === "all" || x.type === state.tab) &&
        (!query ||
          [x.name, x.username, x.url, x.collection].some((v) =>
            String(v || "")
              .toLocaleLowerCase()
              .includes(query),
          )),
    )
    .sort((a, b) =>
      state.sort === "name"
        ? a.name.localeCompare(b.name)
        : new Date(b[state.sort === "updated" ? "updated_at" : "created_at"]) -
          new Date(a[state.sort === "updated" ? "updated_at" : "created_at"]),
    );
}
function renderResults() {
  const root = document.querySelector("#results"),
    foot = document.querySelector("#panel-footer");
  if (!root || !foot) return;
  root.setAttribute("aria-busy", String(state.loading));
  if (state.loading) {
    root.innerHTML = `<div class="loading-state" role="status" aria-label="Loading items">${Array.from({ length: 4 }, () => '<div class="skeleton"></div>').join("")}</div>`;
    foot.innerHTML = "";
    return;
  }
  if (state.error) {
    root.innerHTML = `<div class="empty-state"><div class="empty-icon">${icon("info")}</div><h3>Couldn't load your vault</h3><p>${e(state.error)}</p><button class="btn" data-action="retry-items">${icon("refresh")}Try again</button></div>`;
    foot.innerHTML = "";
    return;
  }
  const all = filteredItems();
  const totalPages = Math.max(1, Math.ceil(all.length / pageSize));
  state.page = Math.min(state.page, totalPages);
  const items = all.slice((state.page - 1) * pageSize, state.page * pageSize);
  if (!items.length) {
    const search = Boolean(state.query || state.tab !== "all");
    root.innerHTML = `<div class="empty-state"><div class="empty-icon">${icon(search ? "search" : "folder")}</div><h3>${search ? "Nothing found just yet" : state.legacyTest ? "No configured credentials in this view" : "Make yourself at home"}</h3><p>${search ? "Try a different search or clear your filters." : state.legacyTest ? "This test loads only the credential IDs configured in config.js. Return to All items to see them." : "Add your first item to start building your personal vault."}</p><button class="btn ${search ? "" : "btn-primary"}" data-action="${search ? "clear-search" : "new-item"}">${icon(search ? "refresh" : "plus")}${search ? "Clear search & filters" : "Add your first item"}</button></div>`;
    foot.innerHTML = "";
    applyLegacyPresentation();
    return;
  }
  root.innerHTML =
    preferences.view === "grid"
      ? `<div class="item-grid">${items.map((item) => itemCard(item)).join("")}</div>`
      : `<div class="table-head" aria-hidden="true"><span>Name</span><span class="column-username">Username</span><span>Collection</span><span class="column-date">Updated</span><span></span></div><div class="items-list">${items.map((item) => itemRow(item)).join("")}</div>`;
  foot.innerHTML = `<div class="panel-footer"><span>Showing ${(state.page - 1) * pageSize + 1}–${Math.min(state.page * pageSize, all.length)} of ${all.length} items</span><div class="pagination"><button class="btn btn-quiet" data-action="previous-page" ${state.page === 1 ? "disabled" : ""} aria-label="Previous page">Previous</button><span class="page-current">${state.page} / ${totalPages}</span><button class="btn btn-quiet" data-action="next-page" ${state.page === totalPages ? "disabled" : ""} aria-label="Next page">Next</button></div></div>`;
  applyLegacyPresentation();
}
function collectionTag(item) {
  return `<span class="collection-tag ${item.collection === "Work" ? "work" : ""}">${e(item.collection || "Personal")}</span>`;
}
function itemTitle(item) {
  return `<span class="item-title">${e(item.name)}${item.favorite ? icon("star") : ""}</span><span class="item-subtitle">${e(displayHost(item.url) || (item.type === "note" ? "Secure note" : item.type === "identity" ? "Personal details" : item.username || "Login"))}</span>`;
}
function itemRow(item) {
  return `<article class="item-row"><button class="item-main" data-action="open-item" data-id="${e(item.id)}" aria-label="Open ${e(item.name)}">${brand(item)}<span class="item-text">${itemTitle(item)}</span></button><span class="username">${e(item.username || "—")}</span>${collectionTag(item)}<span class="item-date">${e(formatDate(item.updated_at))}</span><div class="row-actions">${ui.iconButton("copy", item.type === "login" ? "Copy password" : "Copy " + (item.type === "note" ? "note" : "email"), "quick-copy", `data-id="${e(item.id)}"`)}${ui.iconButton("more", "Details for " + item.name, "open-item", `data-id="${e(item.id)}"`)}</div></article>`;
}
function itemCard(item) {
  return `<article class="item-card"><div class="item-card-top">${brand(item)}${ui.iconButton("more", "Details for " + item.name, "open-item", `data-id="${e(item.id)}"`)}</div><button class="item-main" data-action="open-item" data-id="${e(item.id)}">${itemTitle(item)}</button><div class="item-card-bottom">${collectionTag(item)}${ui.iconButton("copy", "Copy " + (item.type === "login" ? "password" : item.type === "note" ? "note" : "email"), "quick-copy", `data-id="${e(item.id)}"`)}</div></article>`;
}
async function loadItems() {
  const version = epoch;
  state.loading = true;
  state.error = "";
  renderResults();
  try {
    const data = await service.items();
    if (version !== epoch || state.locked) return;
    if (!Array.isArray(data?.items))
      throw new Error("The server returned an unexpected item list.");
    state.items = data.items.map(({ password, ...x }) => ({
      ...x,
      id: String(x.id),
      name: String(x.name || "Untitled"),
      type: ["login", "note", "identity"].includes(x.type) ? x.type : "login",
    }));
    state.loading = false;
    renderShell();
  } catch (error) {
    if (version !== epoch || !state.user || state.locked) return;
    if (error.status === 423) {
      await lockVault();
      return;
    }
    state.error = error.message;
    state.loading = false;
    renderResults();
  }
}
async function copyText(text) {
  if (!navigator.clipboard?.writeText)
    throw new Error(
      "Clipboard access needs HTTPS or localhost. Select and copy the value manually.",
    );
  await navigator.clipboard.writeText(String(text));
  toast("Copied to clipboard.");
}
async function quickCopy(id) {
  const version = epoch;
  const item = state.items.find((x) => x.id === id);
  if (!item) return;
  try {
    let value;
    if (state.legacyTest) {
      const data = await service.item(id);
      value = data.username;
    } else if (item.type === "login") {
      const data = await service.reveal(id);
      value = data.password;
    } else {
      const data = await service.item(id);
      value = item.type === "note" ? data.notes : data.username;
    }
    if (version !== epoch || state.locked) return;
    await copyText(value || "");
  } catch (error) {
    if (error.status === 423) await lockVault();
    else toast(error.message, true);
  }
}
async function openItem(id) {
  closeDrawer();
  drawerTrigger = document.activeElement;
  state.selected = id;
  const version = epoch;
  try {
    const item = await service.item(id);
    if (version !== epoch || state.selected !== id || state.locked) return;
    renderDrawer(item);
  } catch (error) {
    if (version !== epoch) return;
    if (error.status === 423) await lockVault();
    else toast(error.message, true);
  }
}
function detailField(label, value, copyAction = "", extra = "") {
  return `<div class="detail-field"><div><label>${e(label)}</label><div class="detail-value">${e(value || "—")}</div></div>${copyAction ? ui.iconButton("copy", "Copy " + label, copyAction, extra) : ""}</div>`;
}
function renderDrawer(item) {
  document.querySelector("#drawer-root")?.remove();
  const root = document.createElement("div");
  root.id = "drawer-root";
  root.innerHTML = `<div class="drawer-backdrop" data-action="close-drawer"></div><section class="detail-drawer" role="dialog" aria-modal="true" aria-labelledby="detail-title"><header class="drawer-header"><span>${e(typeLabels[item.type])} details</span><div class="drawer-actions">${ui.iconButton("star", item.favorite ? "Remove from favorites" : "Add to favorites", "favorite", `data-id="${e(item.id)}" aria-pressed="${Boolean(item.favorite)}"`)}${ui.iconButton("close", "Close item details", "close-drawer")}</div></header><div class="drawer-body"><div class="detail-hero">${brand(item)}<div><h2 id="detail-title">${e(item.name)}</h2><p>${e(typeLabels[item.type])} · ${e(item.collection || "Personal")}</p></div></div><p class="detail-section-label">${item.type === "identity" ? "Personal information" : "Item information"}</p>${item.type === "login" ? `${detailField("Username", item.username, "copy-field", 'data-field="username"')}<div class="detail-field"><div><label>Password</label><div class="detail-value mono" data-secret id="detail-password">••••••••••••</div></div>${ui.iconButton("eye", "Reveal password", "reveal-password", `data-id="${e(item.id)}"`)}${ui.iconButton("copy", "Copy password", "quick-copy", `data-id="${e(item.id)}"`)}</div>${detailField("Website", item.url)}${safeURL(item.url) ? `<a class="btn btn-quiet" style="font-size:11px;margin-top:10px" href="${e(safeURL(item.url))}" target="_blank" rel="noopener noreferrer">Open website ${icon("external")}</a>` : ""}` : item.type === "identity" ? `${detailField("Full name", item.full_name)}${detailField("Email", item.username, "copy-field", 'data-field="username"')}${detailField("Phone", item.phone)}${detailField("Address", item.address)}` : ""}<p class="detail-section-label">${item.type === "note" ? "Secure note" : "Notes"}</p><div class="detail-notes">${e(item.notes || "No notes added.")}</div><p class="detail-time">Created ${e(formatDate(item.created_at))}<br>Last updated ${e(formatDate(item.updated_at))}</p></div><footer class="drawer-footer"><button class="btn" data-action="edit-item" data-id="${e(item.id)}">${icon("edit")} Edit item</button><button class="btn btn-danger" data-action="delete-item" data-id="${e(item.id)}">${icon("trash")} Delete</button></footer></section>`;
  document.querySelector(".app-shell")?.setAttribute("inert", "");
  app.append(root);
  applyLegacyPresentation();
  root.querySelector('[data-action="close-drawer"]:is(button)')?.focus();
  // Keep only non-secret details attached to this active drawer.
  root._item = Object.fromEntries(
    Object.entries(item).filter(([key]) => key !== "password"),
  );
}
async function revealPassword(button) {
  if (button.dataset.visible === "true") {
    hideRevealed();
    return;
  }
  const version = epoch,
    id = state.selected;
  button.disabled = true;
  try {
    const data = await service.reveal(id);
    if (version !== epoch || id !== state.selected || state.locked) return;
    const node = document.querySelector("#detail-password");
    if (!node) return;
    node.textContent = data.password;
    button.innerHTML = icon("eyeOff");
    button.setAttribute("aria-label", "Hide password");
    button.dataset.visible = "true";
    revealTimer = setTimeout(hideRevealed, 30000);
  } catch (error) {
    if (error.status === 423) await lockVault();
    else toast(error.message, true);
  } finally {
    button.disabled = false;
  }
}
function hideRevealed() {
  clearTimeout(revealTimer);
  const node = document.querySelector("#detail-password");
  if (node) node.textContent = "••••••••••••";
  const button = document.querySelector('[data-action="reveal-password"]');
  if (button) {
    button.innerHTML = icon("eye");
    button.dataset.visible = "false";
    button.setAttribute("aria-label", "Reveal password");
  }
}
function showModal(content) {
  modalTrigger = document.activeElement;
  modal.innerHTML = content;
  modal.showModal();
}
async function editItem(id) {
  try {
    const version = epoch;
    const item = await service.item(id);
    if (version !== epoch || state.locked) return;
    closeDrawer();
    openEditor(item);
  } catch (error) {
    toast(error.message, true);
  }
}
function openEditor(item = null, type = null) {
  const editing = Boolean(item);
  const selectedType =
    type ||
    item?.type ||
    { notes: "note", identities: "identity" }[state.route] ||
    "login";
  const data = item || {
    name: "",
    username: "",
    url: "",
    notes: "",
    collection: state.route === "work" ? "Work" : "Personal",
    favorite: false,
  };
  const field = (name, label, placeholder = "", inputType = "text") =>
    `<div class="field"><label for="edit-${name}">${label}</label><input id="edit-${name}" name="${name}" type="${inputType}" value="${e(data[name] || "")}" placeholder="${placeholder}" maxlength="${name === "url" ? 2048 : 254}" ${name === "name" ? "required" : ""} autocomplete="off"></div>`;
  const content = `<form id="item-form" data-id="${e(item?.id || "")}" data-type="${selectedType}"><header class="modal-header"><h2 id="modal-title">${editing ? "Edit item" : "Add a new item"}</h2>${ui.iconButton("close", "Close form", "close-modal")}</header><div class="modal-body">${!editing ? `<div class="type-picker" role="group" aria-label="Item type">${["login", "note", "identity"].map((t) => `<button type="button" class="type-option ${t === selectedType ? "active" : ""}" data-action="editor-type" data-type="${t}" aria-pressed="${t === selectedType}">${icon(typeIcon(t))}${typeLabels[t]}</button>`).join("")}</div>` : ""}<div class="form-stack"><div data-form-error class="form-error" role="alert" hidden></div>${state.demo ? '<p class="field-help">Demo mode: use fictional details only. Changes are not saved.</p>' : ""}${field("name", "Item name", "e.g. GitHub")}${selectedType === "login" ? `${field("username", "Username or email", "you@example.com")}<div class="field"><div class="inline-actions"><label for="edit-password">${editing ? "New password" : "Password"}</label><button type="button" class="text-btn modal-generate" data-action="generate-editor">${icon("bolt")} Generate</button></div><div class="input-icon"><input id="edit-password" name="password" type="password" autocomplete="new-password" placeholder="${editing ? "Leave blank to keep your current password" : "Enter a password"}" ${editing ? "" : "required"} maxlength="1024" data-secret style="padding-left:13px">${ui.iconButton("eye", "Show password", "toggle-password", 'data-target="edit-password"')}</div></div>${field("url", "Website", "https://example.com", "url")}` : selectedType === "identity" ? `${field("full_name", "Full name", "Full name")}${field("username", "Email address", "you@example.com", "email")}<div class="form-row">${field("phone", "Phone number", "+31 …", "tel")}${field("address", "Address", "Street and city")}</div>` : ""}<div class="field"><label for="edit-collection">Collection</label><select id="edit-collection" name="collection"><option ${data.collection === "Personal" ? "selected" : ""}>Personal</option><option ${data.collection === "Work" ? "selected" : ""}>Work</option></select></div><div class="field"><label for="edit-notes">${selectedType === "note" ? "Secure note" : "Notes"}${selectedType === "note" ? "" : " (optional)"}</label><textarea id="edit-notes" name="notes" rows="${selectedType === "note" ? 6 : 3}" maxlength="20000" placeholder="${selectedType === "note" ? "What would you like to keep?" : "A little extra context…"}" ${selectedType === "note" ? "required" : ""}>${e(data.notes || "")}</textarea></div><label class="checkbox"><input type="checkbox" name="favorite" ${data.favorite ? "checked" : ""}> Add to favorites</label></div></div><footer class="modal-footer"><button type="button" class="btn btn-quiet" data-action="close-modal">Cancel</button><button type="submit" class="btn btn-primary">${icon("check")}${editing ? "Save changes" : "Save item"}</button></footer></form>`;
  if (modal.open) {
    modal.innerHTML = content;
    modal.querySelector("#edit-name")?.focus();
  } else showModal(content);
}
function confirmDelete(id) {
  const item = state.items.find((x) => x.id === id);
  if (!item) return;
  showModal(
    `<form id="delete-form" data-id="${e(id)}"><header class="modal-header"><h2 id="modal-title">Delete item?</h2>${ui.iconButton("close", "Cancel deletion", "close-modal")}</header><div class="modal-body"><div class="danger-icon">${icon("trash")}</div><p class="modal-description">This will permanently delete <span class="confirm-name">${e(item.name)}</span> from your vault. This action cannot be undone.</p><div data-form-error class="form-error" hidden role="alert"></div></div><footer class="modal-footer"><button type="button" class="btn btn-quiet" data-action="close-modal">Keep item</button><button type="submit" class="btn btn-danger">${icon("trash")} Delete item</button></footer></form>`,
  );
}
function settingsPage() {
  return `${pageHeading("Settings", "A few things to make AegisKey feel like yours.")}${demoBanner()}<div class="settings-layout"><section class="settings-card"><div class="settings-card-head"><h3>Your account</h3><p>Your personal workspace and sign-in details.</p></div><div class="settings-row"><div class="settings-profile"><div class="avatar">${e(initials(state.user.name))}</div><div><strong>${e(state.user.name)}</strong><p>${e(state.user.email)}</p></div></div><span class="pill pill-neutral">${state.demo ? "Demo account" : "Personal account"}</span></div><div class="settings-row"><div><h3>Account security</h3><p>${state.demo ? "This fictional account has no authentication settings." : state.user.mfa_enabled ? "Two-factor authentication is enabled." : "Manage your password, passkeys, and two-factor authentication."}</p></div><button class="btn" data-action="manage-account">Manage account ${icon("external")}</button></div></section><section class="settings-card"><div class="settings-card-head"><h3>Preferences</h3><p>Saved on this browser. Your vault data stays separate.</p></div><div class="settings-row"><div><h3>Appearance</h3><p>A lighter workspace or a quieter evening view.</p></div><label><span class="sr-only">Appearance</span><select id="theme-setting"><option value="light" ${preferences.theme === "light" ? "selected" : ""}>Light</option><option value="dark" ${preferences.theme === "dark" ? "selected" : ""}>Dark</option></select></label></div><div class="settings-row"><div><h3>Auto-lock</h3><p>Lock this view after a period of inactivity. Server session limits also apply.</p></div><label><span class="sr-only">Auto-lock timeout</span><select id="autolock-setting">${[1, 5, 15, 30].map((m) => `<option value="${m}" ${preferences.autoLock === m ? "selected" : ""}>After ${m} minute${m > 1 ? "s" : ""}</option>`).join("")}</select></label></div></section><section class="settings-card"><div class="settings-card-head"><h3>Your session</h3><p>Take a break. Your vault will be here when you're back.</p></div><div class="settings-row"><div><h3>Lock vault</h3><p>Clear the current view and require your vault password again.</p></div><button class="btn" data-action="lock">${icon("lock")} Lock now</button></div><div class="settings-row"><div><h3>Sign out</h3><p>${state.demo ? "Leave the demo and discard your temporary changes." : "End your session on this browser."}</p></div><button class="btn btn-danger" data-action="logout">${icon("logout")} Sign out</button></div></section></div>${footer()}`;
}
function generatorPage() {
  return `${pageHeading("Password generator", "One less thing to think of. One stronger password.")}${demoBanner()}<div class="generator-layout"><section class="generator-panel" aria-label="Password generator"><span class="eyebrow">YOUR NEXT PASSWORD</span><div class="generated-output"><code id="generated-password" data-secret></code>${ui.iconButton("refresh", "Generate another password", "generate")}</div><p class="generator-strength">${icon("check")} Randomly generated on your device</p><div class="generator-options"><div><label class="range-header" for="password-length"><span>Password length</span><output id="length-output">${generatorLength}</output></label><input type="range" id="password-length" min="8" max="64" value="${generatorLength}"></div><div class="generator-checks">${[
    ["uppercase", "Uppercase (A–Z)"],
    ["lowercase", "Lowercase (a–z)"],
    ["numbers", "Numbers (2–9)"],
    ["symbols", "Symbols (!@#)"],
  ]
    .map(
      ([key, label]) =>
        `<label class="checkbox"><input type="checkbox" data-generator-option="${key}" ${generatorOptions[key] ? "checked" : ""}>${label}</label>`,
    )
    .join(
      "",
    )}</div></div><div class="generator-buttons"><button class="btn" data-action="generate">${icon("refresh")} Regenerate</button><button class="btn btn-primary" data-action="copy-generated">${icon("copy")} Copy password</button></div><p class="field-help" style="margin-top:17px">Similar-looking characters are excluded. Generated passwords are never saved automatically.</p></section><aside class="generator-tip"><div class="tip-icon">${icon("shield")}</div><h3>A good habit starts here.</h3><p>A unique password for every account means one compromised login doesn't put everything else at risk.</p><ul><li>Longer is usually better.</li><li>Use each password only once.</li><li>Enable MFA where available.</li></ul><div class="divider"></div><p>Copy your new password, then save it in a vault item before using it.</p></aside></div>${footer()}`;
}
function updateGenerated() {
  try {
    generated = generatePassword(generatorLength, generatorOptions);
    const node = document.querySelector("#generated-password");
    if (node) node.textContent = generated;
    clearTimeout(secretTimer);
    secretTimer = setTimeout(() => {
      generated = "";
      const el = document.querySelector("#generated-password");
      if (el) el.textContent = "Generate a new password";
    }, 300000);
  } catch (error) {
    toast(error.message, true);
  }
}
async function lockVault() {
  if (state.legacyTest) {
    await logout();
    return;
  }
  if (!state.user || state.locked) return;
  const lockVersion = ++epoch;
  authPending = true;
  state.locked = true;
  state.items = [];
  state.error = "";
  generated = "";
  lockMarker(true);
  clearSecrets();
  closeModal();
  closeDrawer();
  lockedNotice = "";
  renderAuth();
  try {
    await service.lock();
  } catch {
    lockedNotice =
      "This view is locked, but the server could not confirm the lock. Reconnect before leaving a shared device.";
  } finally {
    if (lockVersion === epoch) {
      authPending = false;
      if (state.locked && state.user) renderAuth();
    }
  }
}
async function logout() {
  if (state.legacyTest) {
    resetSession();
    authView = "login";
    location.hash = "/login";
    renderAuth();
    toast("Local API test closed.");
    return;
  }
  if (authPending || !state.user) return;
  const wasDemo = state.demo;
  const activeService = service;
  const version = ++epoch;
  state.locked = true;
  state.items = [];
  authPending = true;
  generated = "";
  lockMarker(true);
  closeModal();
  closeDrawer();
  lockedNotice = "";
  renderAuth();
  try {
    await activeService.logout();
    if (version !== epoch) return;
    resetSession();
    lockMarker(false);
    authView = "login";
    location.hash = "/login";
    renderAuth();
    if (wasDemo) toast("Demo closed. Temporary changes discarded.");
  } catch {
    if (version !== epoch || !state.user) return;
    authPending = false;
    lockedNotice =
      "Sign-out could not be confirmed by the server. This view is locked. Reconnect and sign out again.";
    renderAuth();
  }
}
function startAuthRedirect(register = false) {
  const url = new URL(
    config.apiBaseUrl.replace(/\/$/, "") +
      `/auth/${register ? "register" : "login"}`,
    location.href,
  );
  url.searchParams.set("return_to", location.origin + location.pathname);
  location.assign(url.href);
}

// All app actions are handled here; rendering never attaches inline JS to user content.
document.addEventListener("click", async (event) => {
  if (
    event.target.closest(".sidebar a") &&
    matchMedia("(max-width: 700px)").matches
  )
    closeMenu();
  const button = event.target.closest("[data-action]");
  if (!button || button.disabled) return;
  const action = button.dataset.action,
    id = button.dataset.id;
  if (action === "start-legacy") {
    await startLegacy();
    return;
  }
  if (action === "start-demo") {
    await startDemo();
    return;
  }
  if (
    ["login-view", "register-view", "recover-view", "reset-view"].includes(
      action,
    )
  ) {
    mfaChallenge = null;
    verifiedUser = null;
    authView = action.split("-")[0];
    renderAuth();
    return;
  }
  if (action === "redirect-login" || action === "redirect-register") {
    startAuthRedirect(action === "redirect-register");
    return;
  }
  if (action === "toggle-password") {
    const input = document.getElementById(button.dataset.target);
    if (input) {
      const showing = input.type === "password";
      input.type = showing ? "text" : "password";
      button.innerHTML = icon(showing ? "eyeOff" : "eye");
      button.setAttribute(
        "aria-label",
        showing ? "Hide password" : "Show password",
      );
    }
    return;
  }
  if (action === "close-modal") {
    closeModal();
    return;
  }
  if (action === "logout" || action === "exit-demo") {
    await logout();
    return;
  }
  if (!state.user || state.locked) return;
  if (action === "open-menu") {
    const side = document.querySelector(".sidebar");
    side?.removeAttribute("inert");
    side?.removeAttribute("aria-hidden");
    document.querySelector(".workspace")?.setAttribute("inert", "");
    document.querySelector(".sidebar")?.classList.add("open");
    document.querySelector(".menu-overlay")?.classList.add("open");
    button.setAttribute("aria-expanded", "true");
    document.querySelector(".sidebar .nav-link")?.focus();
    return;
  }
  if (action === "close-menu") {
    closeMenu();
    return;
  }
  if (action === "lock") {
    await lockVault();
    return;
  }
  if (
    state.legacyTest &&
    [
      "new-item",
      "edit-item",
      "delete-item",
      "favorite",
      "reveal-password",
    ].includes(action)
  ) {
    toast(
      "This existing API connection is read-only. That endpoint is not connected yet.",
      true,
    );
    return;
  }
  if (action === "new-item") {
    openEditor();
    return;
  }
  if (action === "open-item") {
    await openItem(id);
    return;
  }
  if (action === "close-drawer") {
    closeDrawer();
    return;
  }
  if (action === "edit-item") {
    await editItem(id);
    return;
  }
  if (action === "delete-item") {
    confirmDelete(id);
    return;
  }
  if (action === "reveal-password") {
    await revealPassword(button);
    return;
  }
  if (action === "quick-copy") {
    await quickCopy(id);
    return;
  }
  if (action === "copy-field") {
    const item = document.querySelector("#drawer-root")?._item;
    if (item)
      try {
        await copyText(item[button.dataset.field] || "");
      } catch (error) {
        toast(error.message, true);
      }
    return;
  }
  if (action === "favorite") {
    const item = state.items.find((x) => x.id === id);
    if (item) {
      button.disabled = true;
      const version = epoch;
      try {
        const updated = await service.update(id, { favorite: !item.favorite });
        if (version !== epoch || state.locked) return;
        state.items = state.items.map((x) =>
          x.id === id ? { ...x, ...updated } : x,
        );
        closeDrawer();
        renderShell();
        await openItem(id);
      } catch (error) {
        toast(error.message, true);
      } finally {
        button.disabled = false;
      }
    }
    return;
  }
  if (action === "editor-type") {
    const form = document.querySelector("#item-form");
    const data = Object.fromEntries(new FormData(form));
    data.favorite = form.elements.favorite.checked;
    openEditor(null, button.dataset.type);
    for (const key of ["name", "username", "url", "notes", "collection"]) {
      const input = modal.querySelector(`[name="${key}"]`);
      if (input && data[key]) input.value = data[key];
    }
    modal.querySelector("[name=favorite]").checked = data.favorite;
    return;
  }
  if (action === "generate-editor") {
    const input = document.querySelector("#edit-password");
    input.value = generatePassword(24, {
      uppercase: true,
      lowercase: true,
      numbers: true,
      symbols: true,
    });
    input.type = "text";
    const toggle = modal.querySelector('[data-action="toggle-password"]');
    toggle.innerHTML = icon("eyeOff");
    toggle.setAttribute("aria-label", "Hide password");
    return;
  }
  if (action === "filter") {
    state.tab = button.dataset.filter;
    state.page = 1;
    document.querySelectorAll(".filter-tab").forEach((x) => {
      const active = x.dataset.filter === state.tab;
      x.classList.toggle("active", active);
      x.setAttribute("aria-pressed", String(active));
    });
    renderResults();
    return;
  }
  if (action === "clear-search") {
    state.query = "";
    state.tab = "all";
    state.page = 1;
    renderShell();
    document.querySelector("#vault-search")?.focus();
    return;
  }
  if (action === "view-list" || action === "view-grid") {
    preferences.view = action.slice(5);
    savePreferences();
    renderShell();
    return;
  }
  if (action === "previous-page" || action === "next-page") {
    state.page += action === "next-page" ? 1 : -1;
    renderResults();
    return;
  }
  if (action === "retry-items") {
    await loadItems();
    return;
  }
  if (action === "generate") {
    updateGenerated();
    return;
  }
  if (action === "copy-generated") {
    if (!generated) {
      toast("Generate a new password first.", true);
      return;
    }
    try {
      await copyText(generated);
    } catch (error) {
      toast(error.message, true);
    }
    return;
  }
  if (action === "manage-account") {
    if (state.demo || state.legacyTest) {
      toast(
        "Account settings are available when connected to your authentication server.",
      );
      return;
    }
    const url = new URL(
      config.apiBaseUrl.replace(/\/$/, "") + "/auth/account",
      location.href,
    );
    location.assign(url.href);
  }
});
function closeMenu() {
  document.querySelector(".workspace")?.removeAttribute("inert");
  document.querySelector(".sidebar")?.classList.remove("open");
  document.querySelector(".menu-overlay")?.classList.remove("open");
  const button = document.querySelector('[data-action="open-menu"]');
  button?.setAttribute("aria-expanded", "false");
  button?.focus();
  syncMobileNavigation();
}
function syncMobileNavigation() {
  const side = document.querySelector(".sidebar");
  if (!side) return;
  const hidden =
    matchMedia("(max-width: 700px)").matches &&
    !side.classList.contains("open");
  side.inert = hidden;
  if (hidden) side.setAttribute("aria-hidden", "true");
  else side.removeAttribute("aria-hidden");
}
matchMedia("(max-width: 700px)").addEventListener("change", () => {
  document.querySelector(".workspace")?.removeAttribute("inert");
  document.querySelector(".sidebar")?.classList.remove("open");
  document.querySelector(".menu-overlay")?.classList.remove("open");
  syncMobileNavigation();
});
document.addEventListener("input", (event) => {
  if (event.target.id === "vault-search") {
    state.query = event.target.value;
    state.page = 1;
    renderResults();
  }
  if (event.target.id === "password-length") {
    generatorLength = Number(event.target.value);
    document.querySelector("#length-output").textContent = generatorLength;
    updateGenerated();
  }
});
document.addEventListener("change", (event) => {
  const input = event.target;
  if (input.id === "sort-items") {
    state.sort = input.value;
    state.page = 1;
    renderResults();
  }
  if (input.id === "theme-setting") {
    preferences.theme = input.value;
    savePreferences();
  }
  if (input.id === "autolock-setting") {
    preferences.autoLock = Number(input.value);
    savePreferences();
    lastActivity = Date.now();
    toast("Auto-lock preference updated.");
  }
  if (input.dataset.generatorOption) {
    const key = input.dataset.generatorOption;
    generatorOptions[key] = input.checked;
    if (!Object.values(generatorOptions).some(Boolean)) {
      generatorOptions[key] = true;
      input.checked = true;
      toast("Keep at least one character type selected.", true);
      return;
    }
    updateGenerated();
  }
});
document.addEventListener("submit", (event) => {
  const form = event.target;
  if (!(form instanceof HTMLFormElement)) return;
  event.preventDefault();
  const version = epoch;
  busyForm(form, async () => {
    const data = Object.fromEntries(new FormData(form));
    if (form.id === "login-form") {
      let result;
      try {
        const submitLogin =
          config.loginMode === "prototype" ? checkPrototypeLogin : api.login;
        result = await submitLogin({
          email: data.email,
          password: data.password,
        });
      } finally {
        form.elements.password.value = "";
        data.password = "";
      }
      if (version !== epoch) return;
      if (config.loginMode === "prototype") {
        verifiedUser = result;
        rememberEmail(data.email, Boolean(data.remember));
        authView = "verified";
        renderAuth();
        return;
      }
      if (result?.mfa_required) {
        if (!result.challenge_id)
          throw new Error(
            "The server returned an incomplete verification challenge.",
          );
        mfaChallenge = result.challenge_id;
        authView = "mfa";
        renderAuth();
        return;
      }
      rememberEmail(data.email, Boolean(data.remember));
      await acceptSession(result);
      return;
    }
    if (form.id === "mfa-form") {
      let result;
      try {
        result = await api.verifyMFA({
          challenge_id: mfaChallenge,
          code: data.code,
        });
      } finally {
        form.elements.code.value = "";
        data.code = "";
      }
      if (version !== epoch) return;
      mfaChallenge = null;
      await acceptSession(result);
      return;
    }
    if (form.id === "register-form") {
      if (data.password !== data.confirm)
        throw new Error("Your passwords do not match.");
      if (data.password.length < 12)
        throw new Error(
          "Please choose an account password with at least 12 characters.",
        );
      try {
        await api.register({
          name: data.name,
          email: data.email,
          password: data.password,
        });
      } finally {
        form.elements.password.value = "";
        form.elements.confirm.value = "";
        data.password = "";
        data.confirm = "";
      }
      if (version !== epoch) return;
      authView = "login";
      renderAuth();
      toast("Registration submitted. Check your email for the next steps.");
      return;
    }
    if (form.id === "recover-form") {
      await api.recover({ email: data.email });
      if (version !== epoch) return;
      form.innerHTML =
        '<div class="form-success" role="status">If an account exists for this address, you will receive recovery instructions. Check your inbox.</div><button type="button" class="btn full" data-action="reset-view">I have a recovery code</button>';
      return;
    }
    if (form.id === "reset-form") {
      if (data.password !== data.confirm)
        throw new Error("Your passwords do not match.");
      if (data.password.length < 12)
        throw new Error("Please use at least 12 characters.");
      try {
        await api.resetPassword({
          email: data.email,
          code: data.code,
          password: data.password,
        });
      } finally {
        for (const key of ["password", "confirm", "code"]) {
          form.elements[key].value = "";
          data[key] = "";
        }
      }
      if (version !== epoch) return;
      authView = "login";
      renderAuth();
      toast("Account password reset. You can sign in now.");
      return;
    }
    if (form.id === "setup-form") {
      if (data.password !== data.confirm)
        throw new Error("Your vault passwords do not match.");
      if (data.password.length < 12)
        throw new Error("Please use at least 12 characters.");
      let result;
      try {
        result = await api.setupVault({ password: data.password });
      } finally {
        form.elements.password.value = "";
        form.elements.confirm.value = "";
        data.password = "";
        data.confirm = "";
      }
      if (version !== epoch) return;
      if (result?.vault_unlocked !== true)
        throw new Error("Your vault could not be created.");
      state.needsSetup = false;
      state.locked = false;
      lockMarker(false);
      lastActivity = Date.now();
      renderShell();
      await loadItems();
      return;
    }
    if (form.id === "unlock-form") {
      let result;
      try {
        result = await service.unlock(
          state.demo ? {} : { password: data.password },
        );
      } finally {
        if (form.elements.password) form.elements.password.value = "";
        data.password = "";
      }
      if (version !== epoch) return;
      if (result?.vault_unlocked !== true)
        throw new Error("Your vault could not be unlocked.");
      state.locked = false;
      lockMarker(false);
      lockedNotice = "";
      lastActivity = Date.now();
      renderShell();
      await loadItems();
      return;
    }
    if (!state.user || state.locked) return;
    if (state.legacyTest)
      throw new Error("The existing credential API is read-only.");
    if (form.id === "item-form") {
      const id = form.dataset.id,
        type = form.dataset.type;
      const payload = {
        type,
        name: data.name.trim(),
        collection: data.collection,
        favorite: Boolean(data.favorite),
        notes: data.notes || "",
      };
      if (!payload.name) throw new Error("Please give this item a name.");
      if (type === "login") {
        payload.username = data.username || "";
        payload.url = data.url || "";
        if (payload.url && !safeURL(payload.url))
          throw new Error(
            "Use a complete http:// or https:// website address.",
          );
        if (data.password) payload.password = data.password;
        else if (!id) throw new Error("Please enter a password.");
      }
      if (type === "identity")
        Object.assign(payload, {
          username: data.username || "",
          full_name: data.full_name || "",
          phone: data.phone || "",
          address: data.address || "",
        });
      let item;
      try {
        item = id
          ? await service.update(id, payload)
          : await service.create(payload);
      } finally {
        if (form.elements.password) form.elements.password.value = "";
        delete payload.password;
        data.password = "";
      }
      if (version !== epoch || state.locked) return;
      if (!item?.id)
        throw new Error("The server did not return the saved item.");
      closeModal();
      state.page = 1;
      await loadItems();
      if (version !== epoch || state.locked) return;
      toast(id ? "Changes saved." : "Your new item is saved.");
      return;
    }
    if (form.id === "delete-form") {
      await service.remove(form.dataset.id);
      if (version !== epoch || state.locked) return;
      closeModal();
      closeDrawer();
      await loadItems();
      toast("Item deleted.");
    }
  });
});
function focusTrap(event, root) {
  const focusable = [
    ...root.querySelectorAll(
      'a[href],button:not([disabled]),input:not([disabled]),select,textarea,[tabindex="0"]',
    ),
  ].filter((x) => x.getClientRects().length);
  if (!focusable.length) return;
  const first = focusable[0],
    last = focusable.at(-1);
  if (event.shiftKey && document.activeElement === first) {
    event.preventDefault();
    last.focus();
  } else if (!event.shiftKey && document.activeElement === last) {
    event.preventDefault();
    first.focus();
  }
}
document.addEventListener("keydown", (event) => {
  if (event.key === "Escape") {
    if (modal.open) {
      event.preventDefault();
      closeModal();
    } else if (state.selected) closeDrawer();
    else if (document.querySelector(".sidebar.open")) closeMenu();
    return;
  }
  if (event.key === "Tab" && !modal.open) {
    const drawer = document.querySelector(".detail-drawer");
    const sidebar = document.querySelector(".sidebar.open");
    if (drawer) focusTrap(event, drawer);
    else if (sidebar) focusTrap(event, sidebar);
  }
  if (
    event.key === "/" &&
    !modal.open &&
    !state.selected &&
    state.user &&
    !state.locked &&
    !["INPUT", "TEXTAREA", "SELECT"].includes(event.target.tagName)
  ) {
    const search = document.querySelector("#vault-search");
    if (search) {
      event.preventDefault();
      search.focus();
    }
  }
});
modal.addEventListener("cancel", (event) => {
  event.preventDefault();
  closeModal();
});
modal.addEventListener("click", (event) => {
  if (event.target === modal) {
    const r = modal.getBoundingClientRect();
    if (
      event.clientX < r.left ||
      event.clientX > r.right ||
      event.clientY < r.top ||
      event.clientY > r.bottom
    )
      closeModal();
  }
});
window.addEventListener("hashchange", () => {
  if (!state.user) {
    if (config.enableLegacyTestApi && location.hash === "#/test-api")
      startLegacy();
    else if (config.enableDemo && location.hash === "#/demo") startDemo();
    return;
  }
  if (state.locked) return;
  clearSecrets();
  generated = "";
  closeDrawer();
  closeModal();
  state.route = routeFromHash();
  state.query = "";
  state.tab = "all";
  state.page = 1;
  renderShell();
  document.querySelector("#main-content")?.focus({ preventScroll: true });
});
for (const event of ["pointerdown", "keydown", "touchstart"])
  document.addEventListener(
    event,
    () => {
      if (state.user && !state.locked) {
        if (Date.now() - lastActivity >= preferences.autoLock * 60000) {
          lockVault();
          return;
        }
        lastActivity = Date.now();
      }
    },
    { passive: true },
  );
setInterval(() => {
  if (
    state.user &&
    !state.locked &&
    Date.now() - lastActivity >= preferences.autoLock * 60000
  )
    lockVault();
}, 1000);
document.addEventListener("visibilitychange", () => {
  hideRevealed();
  if (
    !document.hidden &&
    state.user &&
    !state.locked &&
    Date.now() - lastActivity >= preferences.autoLock * 60000
  )
    lockVault();
});
window.addEventListener("pagehide", () => {
  clearSecrets();
  generated = "";
});
async function initialize() {
  const version = epoch;
  if (location.protocol === "file:") {
    renderAuth(
      "Open this frontend through a local web server, not directly as a file. See docs/frontend/README.md.",
    );
    return;
  }
  if (config.enableLegacyTestApi && location.hash === "#/test-api") {
    await startLegacy();
    return;
  }
  if (!config.enableDemo && location.hash === "#/demo")
    location.hash = "/login";
  if (config.enableDemo && location.hash === "#/demo") {
    await startDemo();
    return;
  }
  if (config.loginMode === "prototype") {
    renderAuth();
    return;
  }
  try {
    const data = await api.session();
    if (version !== epoch) return;
    if (wasLocked()) {
      data.vault_unlocked = false;
    }
    await acceptSession(data);
  } catch (error) {
    if (state.user || version !== epoch) return;
    authView = "login";
    renderAuth(
      error.status === 401
        ? ""
        : error.status === 404
          ? config.enableDemo
            ? "Sign-in is currently unavailable. You can use the test options below."
            : "Sign-in is currently unavailable. Please try again later."
          : error.message,
    );
  }
}
initialize();
