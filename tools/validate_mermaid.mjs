import mermaid from "mermaid";
import { readFileSync } from "node:fs";

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
