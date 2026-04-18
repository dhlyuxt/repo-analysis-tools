# M1 Architecture Baseline

This document records the M1 architecture seams that later milestones must preserve while real analysis behavior is added.

## Package Boundaries

The repository keeps a visible top-level split between:

- `core`: shared IDs, path rules, envelope helpers, and common error types.
- `storage`: domain-owned runtime directories and persistence boundaries.
- `scan`: repository scan lifecycle and scan handles.
- `scope`: scope summaries and scope-node views derived from scans.
- `anchors`: anchor discovery and anchor descriptions.
- `slice`: slice planning, expansion, and inspection.
- `evidence`: evidence pack creation, reading, and source span access.
- `impact`: impact analysis from paths, anchors, or broader focus areas.
- `report`: report rendering before export.
- `export`: externalized bundles and snapshots.
- `mcp`: server bootstrap, registry, contracts, and tool adapters.
- `skills`: workflow-facing skill packaging.
- `doc_specs`: typed document intent models.
- `doc_dsl`: document-building primitives and validation.
- `renderers`: output renderers for structured documents.
- `tests`: contract, unit, integration, and golden verification layers.

The intended workflow spine remains `scan -> scope -> anchors -> slice -> evidence -> impact -> report -> export`.

## Runtime Root And Path Rules

All runtime-owned artifacts live under `<target_repo>/.codewiki/`.

The runtime contract is:

- path normalization always resolves against the target repository root and emits repo-relative POSIX paths
- attempts to escape the repository root are rejected
- domain storage is allocated by declared ownership, not by ad hoc tool decisions

## Stable Identifier Families

M1 reserves these stable ID prefixes for reusable artifacts:

| Artifact | Prefix | Notes |
| --- | --- | --- |
| scan handle | `scan_` | Used for scan lifecycle and scan-derived reads. |
| slice handle | `slice_` | Used for slice planning and later expansion. |
| evidence pack | `evidence_pack_` | Used to reopen evidence and source spans. |
| report payload | `report_` | Used for rendered reports before export. |
| export bundle | `export_` | Used for exported snapshots and bundles. |

## Storage Ownership

Every runtime directory is owned by one domain under `<target_repo>/.codewiki/`:

| Domain | Directory | Owned artifacts |
| --- | --- | --- |
| `scan` | `scan` | scan metadata and scan handles |
| `scope` | `scope` | scope snapshots derived from scans |
| `anchors` | `anchors` | anchor extraction outputs |
| `slice` | `slice` | slice manifests and expansions |
| `evidence` | `evidence` | evidence packs and citations |
| `impact` | `impact` | impact analysis artifacts |
| `report` | `report` | report payloads before export |
| `export` | `export` | exported analysis bundles |

## MCP Response Envelope

Every MCP-facing tool response uses the same top-level envelope:

| Field | Meaning |
| --- | --- |
| `schema_version` | Contract schema version for the envelope. |
| `status` | `ok` on success or `error` on failure. |
| `data` | Tool-specific payload or error object. |
| `messages` | Structured info or error messages. |
| `recommended_next_tools` | Ordered hints for the next likely workflow step. |

The envelope exists to keep clients MCP-first and client-neutral instead of depending on any chat-runtime-specific format.

## MCP-Facing Error Taxonomy

The shared error code set is:

- `invalid_input`: caller supplied malformed or incomplete input.
- `not_found`: requested runtime artifact or repository target does not exist.
- `conflict`: the requested action collides with existing state or ownership.
- `runtime_state`: runtime prerequisites are missing or the runtime is not ready.
- `internal`: an unexpected internal failure escaped a lower layer.

These errors are exposed through the common envelope instead of domain-specific ad hoc payloads.
