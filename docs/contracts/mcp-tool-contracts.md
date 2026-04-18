# MCP Tool Contracts Baseline

This document records the M1 contract stubs for `src/repo_analysis_tools/mcp/contracts/`. It is a documentation baseline for shape stability, not a claim of full domain behavior.

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

## `scan`

| Tool | Inputs | Outputs | Stable IDs | Failure modes | Next tools |
| --- | --- | --- | --- | --- | --- |
| `scan_repo` | `target_repo` | `target_repo`, `runtime_root`, `scan_id` | `scan` | `invalid_input`, `runtime_state`, `internal` | `get_scan_status`, `show_scope` |
| `refresh_scan` | `target_repo`, `scan_id` | `target_repo`, `runtime_root`, `scan_id`, `refreshed` | `scan` | `invalid_input`, `not_found`, `internal` | `get_scan_status`, `show_scope` |
| `get_scan_status` | `target_repo`, `scan_id` | `target_repo`, `runtime_root`, `scan_id`, `status_detail` | `scan` | `invalid_input`, `not_found`, `internal` | `show_scope`, `list_anchors` |

## `scope`

| Tool | Inputs | Outputs | Stable IDs | Failure modes | Next tools |
| --- | --- | --- | --- | --- | --- |
| `show_scope` | `target_repo`, `scan_id` | `target_repo`, `runtime_root`, `scan_id`, `scope_summary` | `scan` | `invalid_input`, `not_found`, `internal` | `list_scope_nodes`, `list_anchors` |
| `list_scope_nodes` | `target_repo`, `scan_id` | `target_repo`, `runtime_root`, `scan_id`, `nodes` | `scan` | `invalid_input`, `not_found`, `internal` | `explain_scope_node`, `list_anchors` |
| `explain_scope_node` | `target_repo`, `scan_id`, `node_id` | `target_repo`, `runtime_root`, `scan_id`, `node_id`, `summary` | `scan` | `invalid_input`, `not_found`, `internal` | `list_anchors`, `plan_slice` |

## `anchors`

| Tool | Inputs | Outputs | Stable IDs | Failure modes | Next tools |
| --- | --- | --- | --- | --- | --- |
| `list_anchors` | `target_repo`, `scan_id` | `target_repo`, `runtime_root`, `scan_id`, `anchors` | `scan` | `invalid_input`, `not_found`, `internal` | `find_anchor`, `plan_slice` |
| `find_anchor` | `target_repo`, `scan_id`, `anchor_name` | `target_repo`, `runtime_root`, `scan_id`, `anchor_name`, `matches` | `scan` | `invalid_input`, `not_found`, `internal` | `describe_anchor`, `plan_slice` |
| `describe_anchor` | `target_repo`, `scan_id`, `anchor_name` | `target_repo`, `runtime_root`, `scan_id`, `anchor_name`, `description` | `scan` | `invalid_input`, `not_found`, `internal` | `plan_slice`, `impact_from_anchor` |

## `slice`

| Tool | Inputs | Outputs | Stable IDs | Failure modes | Next tools |
| --- | --- | --- | --- | --- | --- |
| `plan_slice` | `target_repo`, `question` | `target_repo`, `runtime_root`, `slice_id`, `seed_summary` | `slice` | `invalid_input`, `not_found`, `internal` | `expand_slice`, `build_evidence_pack` |
| `expand_slice` | `target_repo`, `slice_id` | `target_repo`, `runtime_root`, `slice_id`, `expanded` | `slice` | `invalid_input`, `not_found`, `internal` | `inspect_slice`, `build_evidence_pack` |
| `inspect_slice` | `target_repo`, `slice_id` | `target_repo`, `runtime_root`, `slice_id`, `members` | `slice` | `invalid_input`, `not_found`, `internal` | `build_evidence_pack`, `render_focus_report` |

## `evidence`

| Tool | Inputs | Outputs | Stable IDs | Failure modes | Next tools |
| --- | --- | --- | --- | --- | --- |
| `build_evidence_pack` | `target_repo`, `slice_id` | `target_repo`, `runtime_root`, `slice_id`, `evidence_pack_id` | `slice`, `evidence_pack` | `invalid_input`, `not_found`, `internal` | `read_evidence_pack`, `open_span` |
| `read_evidence_pack` | `target_repo`, `evidence_pack_id` | `target_repo`, `runtime_root`, `evidence_pack_id`, `summary` | `evidence_pack` | `invalid_input`, `not_found`, `internal` | `open_span`, `render_focus_report` |
| `open_span` | `target_repo`, `evidence_pack_id`, `path`, `line_start`, `line_end` | `target_repo`, `runtime_root`, `evidence_pack_id`, `path`, `lines` | `evidence_pack` | `invalid_input`, `not_found`, `internal` | `render_focus_report`, `summarize_impact` |

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
