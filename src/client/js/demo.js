// Fictional, disposable examples. Never persist demo passwords or user-entered data.
// This adapter only exists in memory and never contacts an API.
const samples = [
  {
    id: "github",
    type: "login",
    name: "GitHub",
    username: "diego@aegiskey.dev",
    url: "https://github.com",
    collection: "Personal",
    favorite: true,
    notes: "My personal development workspace.",
    brand: "github",
    password: "Demo-only-GitHub!42",
  },
  {
    id: "google",
    type: "login",
    name: "Google",
    username: "diego@aegiskey.dev",
    url: "https://accounts.google.com",
    collection: "Personal",
    favorite: true,
    notes: "Personal email and calendar.",
    brand: "google",
    password: "Demo-only-Google!42",
  },
  {
    id: "notion",
    type: "login",
    name: "Notion",
    username: "diego@aegiskey.dev",
    url: "https://notion.so",
    collection: "Personal",
    favorite: false,
    notes: "Projects, ideas, and things to learn.",
    brand: "notion",
    password: "Demo-only-Notion!42",
  },
  {
    id: "figma",
    type: "login",
    name: "Figma",
    username: "design@aegiskey.dev",
    url: "https://figma.com",
    collection: "Work",
    favorite: false,
    notes: "Design workspace.",
    brand: "figma",
    password: "Demo-only-Figma!42",
  },
  {
    id: "stripe",
    type: "login",
    name: "Stripe",
    username: "billing@aegiskey.dev",
    url: "https://dashboard.stripe.com",
    collection: "Work",
    favorite: true,
    notes: "Test environment only.",
    brand: "stripe",
    password: "Demo-only-Stripe!42",
  },
  {
    id: "aws",
    type: "login",
    name: "AWS Console",
    username: "admin@aegiskey.dev",
    url: "https://aws.amazon.com",
    collection: "Work",
    favorite: false,
    notes: "Development sandbox.",
    brand: "aws",
    password: "Demo-only-AWS!42",
  },
  {
    id: "wifi",
    type: "note",
    name: "Home network",
    username: "",
    url: "",
    collection: "Personal",
    favorite: false,
    notes:
      "Router: 192.168.1.1\nGuest network: Aegis Guest\nThis is a fictional example note.",
    brand: "note",
  },
  {
    id: "identity",
    type: "identity",
    name: "Personal identity",
    username: "diego@aegiskey.dev",
    url: "",
    collection: "Personal",
    favorite: false,
    full_name: "Diego Wuck",
    phone: "+31 6 1234 5678",
    address: "Example Street 12\n1234 AB Amsterdam",
    notes: "Fictional contact details for the demo.",
    brand: "identity",
  },
];
export function createDemo() {
  let records = structuredClone(samples).map((item, i) => ({
    ...item,
    created_at: new Date(Date.now() - (30 + i) * 86400000).toISOString(),
    updated_at: new Date(Date.now() - i * 86400000).toISOString(),
  }));
  const metadata = ({ password, ...item }) => structuredClone(item);
  return {
    async items() {
      return {
        items: records.map(({ notes, full_name, phone, address, ...record }) =>
          metadata(record),
        ),
      };
    },
    async item(id) {
      const item = records.find((x) => x.id === id);
      if (!item) throw new Error("Item not found.");
      return metadata(item);
    },
    async create(data) {
      const item = {
        ...structuredClone(data),
        id:
          crypto.randomUUID?.() ||
          Array.from(crypto.getRandomValues(new Uint8Array(16)), (n) =>
            n.toString(16).padStart(2, "0"),
          ).join(""),
        created_at: new Date().toISOString(),
        updated_at: new Date().toISOString(),
      };
      records.push(item);
      return metadata(item);
    },
    async update(id, data) {
      const index = records.findIndex((x) => x.id === id);
      if (index < 0) throw new Error("Item not found.");
      records[index] = {
        ...records[index],
        ...structuredClone(data),
        updated_at: new Date().toISOString(),
      };
      return metadata(records[index]);
    },
    async remove(id) {
      records = records.filter((x) => x.id !== id);
    },
    async reveal(id) {
      return { password: records.find((x) => x.id === id)?.password || "" };
    },
    async lock() {},
    async unlock() {
      return { vault_unlocked: true };
    },
    async logout() {
      records = [];
    },
  };
}
