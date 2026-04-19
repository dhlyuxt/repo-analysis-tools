import { readFileSync } from "node:fs";

const dompurifyModule = await import("dompurify");
const dompurify = dompurifyModule.default ?? dompurifyModule;

if (typeof dompurify.addHook !== "function") {
  dompurify.addHook = () => {};
}
if (typeof dompurify.removeHook !== "function") {
  dompurify.removeHook = () => {};
}
if (typeof dompurify.removeAllHooks !== "function") {
  dompurify.removeAllHooks = () => {};
}
if (typeof dompurify.setConfig !== "function") {
  dompurify.setConfig = () => {};
}
if (typeof dompurify.sanitize !== "function") {
  dompurify.sanitize = (value) => value;
}

const mermaidModule = await import("mermaid");
const mermaid = mermaidModule.default ?? mermaidModule;

mermaid.initialize({ startOnLoad: false });

const payload = JSON.parse(readFileSync(0, "utf8"));

try {
  const result = await mermaid.parse(payload.source);
  process.stdout.write(
    JSON.stringify({
      ok: true,
      diagramType: result.diagramType ?? payload.diagram_kind ?? null
    })
  );
} catch (error) {
  process.stdout.write(
    JSON.stringify({
      ok: false,
      error: error?.message ?? String(error)
    })
  );
  process.exitCode = 1;
}
