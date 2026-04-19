from __future__ import annotations

from dataclasses import dataclass

from repo_analysis_tools.anchors.models import AnchorRecord, AnchorSnapshot
from repo_analysis_tools.impact.models import ImpactTarget


@dataclass(frozen=True)
class PropagationResult:
    targets: list[ImpactTarget]
    notes: list[str]


def reverse_callers_for_paths(
    snapshot: AnchorSnapshot,
    changed_paths: list[str],
) -> PropagationResult:
    changed_path_set = set(changed_paths)
    changed_anchors = [
        anchor
        for anchor in snapshot.anchors
        if anchor.path in changed_path_set and anchor.kind == "function_definition"
    ]
    direct_call_propagation = reverse_callers_for_anchors(snapshot, changed_anchors)
    include_propagation = include_dependents_for_paths(snapshot, changed_path_set)

    if not changed_anchors and not include_propagation.targets:
        return PropagationResult(
            targets=[],
            notes=[
                "No function-definition anchors or include dependents were found in the changed paths, so propagation is bounded by available anchor relations."
            ],
        )

    combined_targets = {
        (target.anchor_id or "", target.path, target.anchor_name or "", target.kind or ""): target
        for target in [*direct_call_propagation.targets, *include_propagation.targets]
    }
    combined_notes: list[str] = []
    if changed_anchors:
        combined_notes.extend(direct_call_propagation.notes)
    else:
        combined_notes.append(
            "No function-definition anchors were found in the changed paths; direct-call propagation is bounded by available anchor relations."
        )
    if include_propagation.targets:
        combined_notes.extend(include_propagation.notes)

    return PropagationResult(
        targets=sorted(
            combined_targets.values(),
            key=lambda item: (
                item.path,
                item.anchor_name or "",
                item.kind or "",
            ),
        ),
        notes=combined_notes,
    )


def reverse_callers_for_anchor(
    snapshot: AnchorSnapshot,
    seed_anchor: AnchorRecord,
) -> PropagationResult:
    return reverse_callers_for_anchors(snapshot, [seed_anchor])


def reverse_callers_for_anchors(
    snapshot: AnchorSnapshot,
    seed_anchors: list[AnchorRecord],
) -> PropagationResult:
    anchors_by_id = {anchor.anchor_id: anchor for anchor in snapshot.anchors}
    callers: dict[str, ImpactTarget] = {}
    seed_anchor_ids = {anchor.anchor_id for anchor in seed_anchors}
    seed_names = sorted({anchor.name for anchor in seed_anchors})

    for relation in snapshot.relations:
        if relation.kind != "direct_call":
            continue
        if relation.target_anchor_id not in seed_anchor_ids:
            continue
        caller_anchor = anchors_by_id.get(relation.source_anchor_id)
        if caller_anchor is None:
            continue
        callers[caller_anchor.anchor_id] = ImpactTarget(
            path=caller_anchor.path,
            anchor_id=caller_anchor.anchor_id,
            anchor_name=caller_anchor.name,
            kind=caller_anchor.kind,
            reason=f"{caller_anchor.name} directly calls {relation.target_name}",
        )

    names_text = ", ".join(seed_names) if seed_names else "the selected anchors"
    return PropagationResult(
        targets=sorted(
            callers.values(),
            key=lambda item: (
                item.path,
                item.anchor_name or "",
                item.kind or "",
            ),
        ),
        notes=[
            f"Reverse-caller propagation for {names_text} is limited to direct_call relations with explicit target anchors and is bounded by available anchor relations."
        ],
    )


def include_dependents_for_paths(
    snapshot: AnchorSnapshot,
    changed_path_set: set[str],
) -> PropagationResult:
    anchors_by_id = {anchor.anchor_id: anchor for anchor in snapshot.anchors}
    dependents: dict[str, ImpactTarget] = {}

    for relation in snapshot.relations:
        if relation.kind != "includes":
            continue
        if relation.target_path not in changed_path_set:
            continue
        source_anchor = anchors_by_id.get(relation.source_anchor_id)
        if source_anchor is None:
            continue
        dependents[source_anchor.anchor_id] = ImpactTarget(
            path=source_anchor.path,
            anchor_id=source_anchor.anchor_id,
            anchor_name=source_anchor.name,
            kind=source_anchor.kind,
            reason=f"{source_anchor.name} includes {relation.target_name}",
        )

    return PropagationResult(
        targets=sorted(
            dependents.values(),
            key=lambda item: (
                item.path,
                item.anchor_name or "",
                item.kind or "",
            ),
        ),
        notes=[
            "Include-based propagation is limited to explicit includes relations whose resolved target_path matches a changed path."
        ]
        if dependents
        else [],
    )
