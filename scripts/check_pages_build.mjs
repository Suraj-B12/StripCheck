import assert from "node:assert/strict";
import { readFile, readdir } from "node:fs/promises";
import { dirname, extname, join, resolve } from "node:path";
import { fileURLToPath } from "node:url";

const root = resolve(
  dirname(fileURLToPath(import.meta.url)),
  "../web/dist-pages",
);
const html = await readFile(join(root, "index.html"), "utf8");
const references = [...html.matchAll(/(?:src|href)="([^"]+)"/g)].map(
  (match) => match[1],
);
assert(
  references.some((value) => value.endsWith(".js")),
  "No application bundle",
);
for (const value of references) {
  assert(
    value.startsWith("/StripCheck/"),
    `Incorrect Pages asset path: ${value}`,
  );
  await readFile(join(root, value.slice("/StripCheck/".length)));
}
const allowed = new Set([
  ".html",
  ".js",
  ".css",
  ".svg",
  ".png",
  ".webp",
  ".ico",
]);
let count = 0;
async function inspect(directory) {
  for (const entry of await readdir(directory, { withFileTypes: true })) {
    assert(!entry.isSymbolicLink(), "Deployment must not contain symlinks");
    assert(
      !["data", "runs", "node_modules", ".git"].includes(entry.name),
      "Private runtime directory",
    );
    const path = join(directory, entry.name);
    if (entry.isDirectory()) await inspect(path);
    else {
      assert(
        allowed.has(extname(entry.name)),
        `Unexpected deployment file: ${entry.name}`,
      );
      const bytes = await readFile(path);
      assert(
        bytes.length < 5 * 1024 * 1024,
        `Oversized deployment file: ${entry.name}`,
      );
      count++;
    }
  }
}
await inspect(root);
console.log(
  `Pages artifact verified: ${count} static files; correct project paths; no runtime data.`,
);
