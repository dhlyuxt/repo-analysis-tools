# MCP Tool Contracts

This document records the M2 runtime contract surface for `src/repo_analysis_tools/mcp/contracts/`. It mirrors the real analysis-first mainline behavior rather than the old M1 stub baseline.

## Standard Response Envelope

All tool responses use the same outer envelope:

| Field | Meaning |
| --- | --- |
| `schema_version` | Shared envelope version. |
| `status` | `ok` or `error`. |
| `data` | Tool-specific output payload or wrapped error payload. |
| `messages` | Structured info or error messages. |
| `recommended_next_tools` | Ordered hints for the next likely tool call. |

## Stable ID Families

The current contract set uses these stable ID families:

- `scan`: emitted as `scan_<12-hex>`
- `slice`: emitted as `slice_<12-hex>`
- `evidence_pack`: emitted as `evidence_pack_<12-hex>`
- `report`: emitted as `report_<12-hex>`
- `export`: emitted as `export_<12-hex>`

## Standard Failure Modes

Contract stubs currently reuse the shared MCP-facing error taxonomy:

- `invalid_input`
- `not_found`
- `conflict`
- `runtime_state`
- `internal`

## Analysis-First Mainline

The supported mainline path is:

```text
scan_repo
-> get_scan_status
-> show_scope
-> list_anchors / find_anchor / describe_anchor
-> plan_slice
-> build_evidence_pack
-> read_evidence_pack
-> open_span
```

Contract consumers should treat `read_evidence_pack` as the handoff point from structured evidence to raw source access. `open_span` remains bounded by evidence citations and `MAX_OPEN_SPAN_LINES`; it is not a generic repository reader.

## `scan`

| Tool | Inputs | Outputs | Stable IDs | Failure modes | Next tools |
| --- | --- | --- | --- | --- | --- |
| `scan_repo` | `target_repo` | `target_repo`, `runtime_root`, `scan_id`, `repo_root`, `file_count`, `latest_completed_at`, `git_head`, `workspace_dirty` | `scan` | `invalid_input`, `runtime_state`, `internal` | `get_scan_status`, `show_scope` |
| `refresh_scan` | `target_repo`, `scan_id` | `target_repo`, `runtime_root`, `scan_id`, `repo_root`, `file_count`, `latest_completed_at`, `git_head`, `workspace_dirty` | `scan` | `invalid_input`, `not_found`, `internal` | `get_scan_status`, `show_scope` |
| `get_scan_status` | `target_repo`, `scan_id` | `target_repo`, `runtime_root`, `scan_id`, `repo_root`, `file_count`, `latest_completed_at`, `git_head`, `workspace_dirty` | `scan` | `invalid_input`, `not_found`, `internal` | `show_scope`, `list_anchors` |

## `scope`

| Tool | Inputs | Outputs | Stable IDs | Failure modes | Next tools |
| --- | --- | --- | --- | --- | --- |
| `show_scope` | `target_repo`, `scan_id` | `target_repo`, `runtime_root`, `scan_id`, `scope_summary`, `role_counts` | `scan` | `invalid_input`, `not_found`, `internal` | `list_scope_nodes`, `list_anchors` |
| `list_scope_nodes` | `target_repo`, `scan_id` | `target_repo`, `runtime_root`, `scan_id`, `nodes` | `scan` | `invalid_input`, `not_found`, `internal` | `explain_scope_node`, `list_anchors` |
| `explain_scope_node` | `target_repo`, `scan_id`, `node_id` | `target_repo`, `runtime_root`, `scan_id`, `node_id`, `summary`, `related_files` | `scan` | `invalid_input`, `not_found`, `internal` | `list_anchors`, `plan_slice` |

## `anchors`

| Tool | Inputs | Outputs | Stable IDs | Failure modes | Next tools |
| --- | --- | --- | --- | --- | --- |
| `list_anchors` | `target_repo`, `scan_id` | `target_repo`, `runtime_root`, `scan_id`, `anchors` | `scan` | `invalid_input`, `not_found`, `internal` | `find_anchor`, `plan_slice` |
| `find_anchor` | `target_repo`, `scan_id`, `anchor_name` | `target_repo`, `runtime_root`, `scan_id`, `anchor_name`, `matches` | `scan` | `invalid_input`, `not_found`, `internal` | `describe_anchor`, `plan_slice` |
| `describe_anchor` | `target_repo`, `scan_id`, `anchor_name` | `target_repo`, `runtime_root`, `scan_id`, `anchor_name`, `description`, `relations` | `scan` | `invalid_input`, `not_found`, `internal` | `plan_slice`, `impact_from_anchor` |

## `slice`

| Tool | Inputs | Outputs | Stable IDs | Failure modes | Next tools |
| --- | --- | --- | --- | --- | --- |
| `plan_slice` | `target_repo`, `question` | `target_repo`, `runtime_root`, `slice_id`, `scan_id`, `query_kind`, `status`, `selected_files`, `selected_anchor_names`, `notes` | `slice` | `invalid_input`, `not_found`, `internal` | `inspect_slice`, `build_evidence_pack` |
| `expand_slice` | `target_repo`, `slice_id` | `target_repo`, `runtime_root`, `slice_id`, `expanded` | `slice` | `invalid_input`, `not_found`, `internal` | `inspect_slice`, `build_evidence_pack` |
| `inspect_slice` | `target_repo`, `slice_id` | `target_repo`, `runtime_root`, `slice_id`, `members` | `slice` | `invalid_input`, `not_found`, `internal` | `build_evidence_pack`, `render_focus_report` |

## `evidence`

| Tool | Inputs | Outputs | Stable IDs | Failure modes | Next tools |
| --- | --- | --- | --- | --- | --- |
| `build_evidence_pack` | `target_repo`, `slice_id` | `target_repo`, `runtime_root`, `slice_id`, `evidence_pack_id`, `citation_count`, `summary` | `slice`, `evidence_pack` | `invalid_input`, `not_found`, `internal` | `read_evidence_pack`, `open_span` |
| `read_evidence_pack` | `target_repo`, `evidence_pack_id` | `target_repo`, `runtime_root`, `evidence_pack_id`, `summary`, `citations` | `evidence_pack` | `invalid_input`, `not_found`, `internal` | `open_span` |
| `open_span` | `target_repo`, `evidence_pack_id`, `path`, `line_start`, `line_end` | `target_repo`, `runtime_root`, `evidence_pack_id`, `path`, `line_start`, `line_end`, `lines` | `evidence_pack` | `invalid_input`, `not_found`, `internal` | `read_evidence_pack` |

## `impact`

| Tool | Inputs | Outputs | Stable IDs | Failure modes | Next tools |
| --- | --- | --- | --- | --- | --- |
| `impact_from_paths` | `target_repo`, `scan_id`, `paths` | `target_repo`, `runtime_root`, `scan_id`, `impact_summary` | `scan` | `invalid_input`, `not_found`, `internal` | `summarize_impact`, `build_evidence_pack` |
| `impact_from_anchor` | `target_repo`, `scan_id`, `anchor_name` | `target_repo`, `runtime_root`, `scan_id`, `impact_summary` | `scan` | `invalid_input`, `not_found`, `internal` | `summarize_impact`, `build_evidence_pack` |
| `summarize_impact` | `target_repo`, `scan_id`, `focus` | `target_repo`, `runtime_root`, `scan_id`, `risks` | `scan` | `invalid_input`, `not_found`, `internal` | `render_analysis_outline`, `render_focus_report` |

## `report`

| Tool | Inputs | Outputs | Stable IDs | Failure modes | Next tools |
| --- | --- | --- | --- | --- | --- |
| `render_focus_report` | `target_repo`, `evidence_pack_id` | `target_repo`, `runtime_root`, `evidence_pack_id`, `report_id` | `evidence_pack`, `report` | `invalid_input`, `not_found`, `internal` | `render_module_summary`, `export_analysis_bundle` |
| `render_module_summary` | `target_repo`, `evidence_pack_id`, `module_name` | `target_repo`, `runtime_root`, `evidence_pack_id`, `report_id` | `evidence_pack`, `report` | `invalid_input`, `not_found`, `internal` | `render_analysis_outline`, `export_analysis_bundle` |
| `render_analysis_outline` | `target_repo`, `focus` | `target_repo`, `runtime_root`, `report_id`, `sections` | `report` | `invalid_input`, `not_found`, `internal` | `export_analysis_bundle`, `export_scope_snapshot` |

## `export`

| Tool | Inputs | Outputs | Stable IDs | Failure modes | Next tools |
| --- | --- | --- | --- | --- | --- |
| `export_analysis_bundle` | `target_repo`, `report_id` | `target_repo`, `runtime_root`, `report_id`, `export_id` | `report`, `export` | `invalid_input`, `not_found`, `internal` | `export_scope_snapshot`, `export_evidence_bundle` |
| `export_scope_snapshot` | `target_repo`, `scan_id` | `target_repo`, `runtime_root`, `scan_id`, `export_id` | `scan`, `export` | `invalid_input`, `not_found`, `internal` | `export_evidence_bundle` |
| `export_evidence_bundle` | `target_repo`, `evidence_pack_id` | `target_repo`, `runtime_root`, `evidence_pack_id`, `export_id` | `evidence_pack`, `export` | `invalid_input`, `not_found`, `internal` | none |
