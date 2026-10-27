import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";
export default defineConfig(({ mode }) => ({
  base: mode === "pages" ? "/StripCheck/" : "/",
  plugins: [
    react(),
    {
      name: "pages-showcase-description",
      transformIndexHtml(html) {
        if (mode !== "pages") return html;
        return html
          .replace(
            "<title>StripCheck — A closer look.</title>",
            "<title>StripCheck — Interactive showcase</title>",
          )
          .replace(
            "A closer look at your medicine. Check exact batch details against CDSCO drug quality alert lists, with clear evidence and local image reading.",
            "Explore StripCheck through fictional, interactive examples. This public showcase does not check real medicines; use the local app for photo and batch checks.",
          );
      },
    },
  ],
  server: { host: "127.0.0.1", proxy: { "/api": "http://127.0.0.1:8765" } },
  build: { sourcemap: false, outDir: mode === "pages" ? "dist-pages" : "dist" },
}));
