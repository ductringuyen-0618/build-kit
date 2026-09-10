"""Code-only AST graphify build. Run with cwd = repo dir. Writes graphify-out/."""
import json
from pathlib import Path
from graphify.detect import detect
from graphify.extract import collect_files, extract
from graphify.build import build_from_json
from graphify.cluster import cluster, score_all
from graphify.analyze import god_nodes, surprising_connections, suggest_questions
from graphify.report import generate
from graphify.export import to_json


def main():
    root = Path('.')
    out = Path('graphify-out')
    out.mkdir(exist_ok=True)

    detection = detect(root)
    (out / '.graphify_detect.json').write_text(
        json.dumps(detection, ensure_ascii=False), encoding='utf-8')
    print(f"DETECT: {detection.get('total_files', 0)} files, "
          f"{detection.get('total_words', 0):,} words, "
          f"code={len(detection.get('files', {}).get('code', []))}")

    # AST extraction (code only)
    code_files = []
    for f in detection.get('files', {}).get('code', []):
        p = Path(f)
        code_files.extend(collect_files(p) if p.is_dir() else [p])
    if code_files:
        ast = extract(code_files)
    else:
        ast = {'nodes': [], 'edges': [], 'input_tokens': 0, 'output_tokens': 0}
    print(f"AST: {len(ast['nodes'])} nodes, {len(ast['edges'])} edges "
          f"from {len(code_files)} files")

    # empty semantic merge (Part C)
    extraction = {
        'nodes': ast['nodes'],
        'edges': ast['edges'],
        'hyperedges': [],
        'input_tokens': 0,
        'output_tokens': 0,
    }
    (out / '.graphify_extract.json').write_text(
        json.dumps(extraction, indent=2, ensure_ascii=False), encoding='utf-8')

    G = build_from_json(extraction)
    if G.number_of_nodes() == 0:
        print('ERROR: empty graph')
        raise SystemExit(1)
    communities = cluster(G)
    cohesion = score_all(G, communities)
    gods = god_nodes(G)
    surprises = surprising_connections(G, communities)
    labels = {cid: 'Community ' + str(cid) for cid in communities}
    questions = suggest_questions(G, communities, labels)
    tokens = {'input': 0, 'output': 0}

    report = generate(G, communities, cohesion, labels, gods, surprises,
                      detection, tokens, str(root), suggested_questions=questions)
    (out / 'GRAPH_REPORT.md').write_text(report, encoding='utf-8')
    to_json(G, communities, 'graphify-out/graph.json')

    # dump per-community node labels so we can name them
    comm_labels = {}
    for cid, members in communities.items():
        comm_labels[str(cid)] = [G.nodes[n].get('label', n) for n in members]

    analysis = {
        'communities': {str(k): v for k, v in communities.items()},
        'cohesion': {str(k): v for k, v in cohesion.items()},
        'gods': gods,
        'surprises': surprises,
        'questions': questions,
        'community_node_labels': comm_labels,
    }
    (out / '.graphify_analysis.json').write_text(
        json.dumps(analysis, indent=2, ensure_ascii=False), encoding='utf-8')

    print(f"GRAPH: {G.number_of_nodes()} nodes, {G.number_of_edges()} edges, "
          f"{len(communities)} communities")


if __name__ == '__main__':
    main()
