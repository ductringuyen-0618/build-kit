"""Finalize a code-only graphify build: auto-label communities, regenerate
report, write HTML, manifest, benchmark. Run with cwd = repo dir."""
import json
import os
from collections import Counter
from pathlib import Path

from graphify.build import build_from_json
from graphify.cluster import score_all
from graphify.analyze import god_nodes, surprising_connections, suggest_questions
from graphify.report import generate
from graphify.export import to_html
from graphify.detect import save_manifest
from graphify.benchmark import run_benchmark, print_benchmark


def common_dir(paths):
    parts = [Path(p).parts for p in paths if p]
    if not parts:
        return ""
    pref = []
    for tup in zip(*parts):
        if len(set(tup)) == 1:
            pref.append(tup[0])
        else:
            break
    # drop the filename component if it slipped in; keep up to 2 dir levels
    return "/".join(pref[-2:]) if pref else ""


def label_for(G, members):
    # most-connected node in the community = the hub
    hub = max(members, key=lambda n: G.degree(n))
    hub_label = G.nodes[hub].get("label", hub).rstrip("()")
    # dominant directory among member source files
    dirs = []
    for n in members:
        sf = G.nodes[n].get("source_file") or ""
        d = os.path.dirname(sf)
        if d:
            dirs.append(d)
    name = ""
    if dirs:
        top_dir = Counter(dirs).most_common(1)[0][0]
        name = "/".join(Path(top_dir).parts[-2:])
    if name and hub_label:
        return f"{name}: {hub_label}"[:48]
    return (name or hub_label or "misc")[:48]


def main():
    out = Path("graphify-out")
    extraction = json.loads((out / ".graphify_extract.json").read_text(encoding="utf-8"))
    detection = json.loads((out / ".graphify_detect.json").read_text(encoding="utf-8"))
    analysis = json.loads((out / ".graphify_analysis.json").read_text(encoding="utf-8"))

    G = build_from_json(extraction)
    communities = {int(k): v for k, v in analysis["communities"].items()}
    cohesion = {int(k): v for k, v in analysis["cohesion"].items()}

    labels = {cid: label_for(G, members) for cid, members in communities.items()}
    questions = suggest_questions(G, communities, labels)
    tokens = {"input": 0, "output": 0}

    report = generate(G, communities, cohesion, labels, analysis["gods"],
                      analysis["surprises"], detection, tokens, ".",
                      suggested_questions=questions)
    (out / "GRAPH_REPORT.md").write_text(report, encoding="utf-8")
    (out / ".graphify_labels.json").write_text(
        json.dumps({str(k): v for k, v in labels.items()}, ensure_ascii=False),
        encoding="utf-8")

    n = G.number_of_nodes()
    if n > 5000:
        print(f"Graph has {n} nodes - too large for HTML viz, skipping.")
    else:
        to_html(G, communities, "graphify-out/graph.html", community_labels=labels)
        print("graph.html written")

    save_manifest(detection["files"])
    print("manifest saved")

    print("\n--- BENCHMARK ---")
    result = run_benchmark("graphify-out/graph.json",
                           corpus_words=detection["total_words"])
    print_benchmark(result)


if __name__ == "__main__":
    main()
