"""Aggregate Phase A batch YAMLs into a per-section synthesis for Phase B template design.

Reads all _phase-a-batch-NN.yaml files, walks their section_observations, and
produces a single _phase-b-synthesis.yaml that for each section captures:

- total samples observed across all batches
- aggregated sub_purposes_seen counts
- collected shape assessments (consensus + dissents)
- common_description snippets per batch (for template designer to read)
- merged outliers list
- merged issues list (the template-design questions)
"""

import subprocess
from collections import Counter
from dataclasses import dataclass, field
from pathlib import Path

import yaml

ROOT = Path(
    subprocess.run(
        ["git", "-C", str(Path(__file__).resolve().parent), "rev-parse", "--show-toplevel"],
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()
)
RESEARCH = ROOT / "logs/research"


@dataclass
class SectionAccumulator:
    total_samples: int = 0
    sub_purposes_seen: Counter = field(default_factory=Counter)
    shape_observations: Counter = field(default_factory=Counter)
    common_descriptions: list = field(default_factory=list)
    outliers: list = field(default_factory=list)
    issues: list = field(default_factory=list)


def aggregate_batches(subject: str) -> dict:
    by_section: dict[str, SectionAccumulator] = {}
    files_processed: set[str] = set()

    for batch_yaml in sorted(RESEARCH.glob("_phase-a-batch-*.yaml")):
        data = yaml.safe_load(batch_yaml.read_text())
        batch_id = batch_yaml.stem.replace("_phase-a-batch-", "batch-")
        for fp in data.get("files_processed", []):
            files_processed.add(Path(fp["path"]).name)
        for obs in data.get("section_observations", []):
            if obs.get("subject") != subject:
                continue
            sec = obs["section"]
            entry = by_section.setdefault(sec, SectionAccumulator())
            entry.total_samples += obs.get("samples_in_batch", 0)
            for sub, count in (obs.get("sub_purposes_seen") or {}).items():
                entry.sub_purposes_seen[sub] += count
            shape = obs.get("shape")
            if shape:
                entry.shape_observations[shape] += 1
            desc = obs.get("common_description")
            if desc:
                entry.common_descriptions.append({batch_id: desc.strip()})
            for out in obs.get("outliers") or []:
                entry.outliers.append({**out, "batch": batch_id})
            for iss in obs.get("issues") or []:
                entry.issues.append({batch_id: iss})

    return {
        "subject": subject,
        "files_processed": sorted(files_processed),
        "files_processed_count": len(files_processed),
        "sections": {
            sec: {
                "total_samples": entry.total_samples,
                "sub_purposes_seen": dict(entry.sub_purposes_seen.most_common()),
                "shape_consensus": dict(entry.shape_observations),
                "common_descriptions": entry.common_descriptions,
                "outliers": entry.outliers,
                "issues": entry.issues,
            }
            for sec, entry in by_section.items()
        },
    }


if __name__ == "__main__":
    synth = aggregate_batches("mcp")
    target = RESEARCH / "_phase-b-mcp-synthesis.yaml"
    target.write_text(yaml.safe_dump(synth, sort_keys=False, width=120, allow_unicode=True))
    print(f"Wrote {target}")
    print(f"  files_processed: {synth['files_processed_count']}")
    print(f"  sections: {len(synth['sections'])}")
    for sec, e in synth["sections"].items():
        print(f"    {sec}: {e['total_samples']} samples, {len(e['sub_purposes_seen'])} sub-purposes, {len(e['issues'])} issues")
