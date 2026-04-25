---
name: repo-doc-writer
description: Use when a document writer subagent has structured repository findings and must produce repository design documentation.
---

# Repo Doc Writer

This skill is for a document writer subagent only. Do not use this skill in the coordinating agent.

Use it when the coordinating agent has already completed repository audit work and provides a structured findings package. This workflow is not free-form Markdown; it drives the local typed document pipeline and writes the controlled repository design document set.

## Required Input

Stop and report the missing field if any of these structured input fields are absent:

- `repo_name`
- `target_repo`
- `output_root`
- `module_map`
- `module_reports`
- `global_findings`

## Controlled Path

Follow this path exactly:

```text
structured findings package
-> doc_specs selection
-> doc_dsl document construction
-> validators
-> MarkdownRenderer
-> final document set + manifest
```

Do not draft repository design pages directly from a prompt. Preserve evidence references from the structured findings package and let the typed pipeline decide document shape, validation, and final Markdown rendering.

## Command

Run the local writer with the input package path:

```bash
/home/hyx/anaconda3/envs/agent/bin/python tools/write_repo_design_docs.py --input <input-json-path>
```

After the command completes, report the generated files and manifest path from the writer output.
