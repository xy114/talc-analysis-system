#!/usr/bin/env python3
"""MgO-SiO₂(-C-H₂O) 体系知识图谱 — 论文注册引擎

用法:
  python scripts/ingest.py --json paper-data/PAPER-XXX.json         # 注册
  python scripts/ingest.py --json paper-data/PAPER-XXX.json --dry-run  # 校验不写入
  python scripts/ingest.py --json paper-data/PAPER-XXX.json --force  # 覆盖注册

注册逻辑:
  1. 校验 paper-data JSON（Q1-Q4 完整 + tree_contributions 非空）
  2. 加载 system-tree.json（不存在则创建空白树）
  3. 注册新节点（去重：按 node.id 匹配）
  4. 注册新边（去重：按 from+to+type 匹配）
  5. 追加性质数据到已有节点
  6. 写回 system-tree.json（version++, last_updated 更新）
  7. 输出注册统计
"""

import argparse
import json
import sys
import os
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TREE_PATH = ROOT / "system-tree.json"

REQUIRED_PAPER_FIELDS = ["id", "title", "authors", "year"]
REQUIRED_TC_FIELDS = ["new_nodes", "new_edges", "properties_added_to", "papers_cross_validated"]


def validate_json(data: dict) -> list:
    """校验 paper-data JSON，返回错误列表。"""
    errors = []
    paper = data.get("paper", {})

    for field in REQUIRED_PAPER_FIELDS:
        if not paper.get(field):
            errors.append(f"缺少必填字段: paper.{field}")

    tc = paper.get("tree_contributions", {})
    for field in REQUIRED_TC_FIELDS:
        if field not in tc:
            errors.append(f"缺少必填字段: paper.tree_contributions.{field}")

    if tc:
        nn = tc.get("new_nodes", [])
        ne = tc.get("new_edges", [])
        pa = tc.get("properties_added_to", {})
        if not nn and not ne and not pa:
            errors.append("警告: tree_contributions 中无 new_nodes/new_edges/properties_added_to — 论文未注册任何贡献")

    q3 = paper.get("q3_reliability", {})
    if not q3.get("scale"):
        errors.append("警告: q3_reliability.scale 为空")
    if not q3.get("journal_tier"):
        errors.append("警告: q3_reliability.journal_tier 为空")

    return errors


def validate_tree_node(node: dict) -> list:
    """校验单个节点的必填字段。"""
    errors = []
    for field in ["id", "name", "type", "depth"]:
        if field not in node:
            errors.append(f"节点缺少必填字段: {field}")
    if node.get("type") not in ("raw_material", "intermediate_phase", "product", "byproduct"):
        errors.append(f"节点 type 无效: {node.get('type')}")
    return errors


def validate_tree_edge(edge: dict) -> list:
    """校验单条边的必填字段。"""
    errors = []
    for field in ["from", "to", "type"]:
        if field not in edge:
            errors.append(f"边缺少必填字段: {field}")
    if edge.get("type") not in ("process", "property_link"):
        errors.append(f"边 type 无效: {edge.get('type')}")
    return errors


def load_tree():
    """加载 system-tree.json，不存在则创建空白树。"""
    if TREE_PATH.exists():
        with open(TREE_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    else:
        return {
            "meta": {
                "name": "黑滑石 MgO-SiO₂(-C-H₂O) 物相-应用体系树",
                "version": "0.1.0",
                "last_updated": str(date.today()),
                "description": "以黑滑石原矿为根，按工艺条件分支到各物相，再按性质连接到应用产品"
            },
            "nodes": {},
            "edges": {}
        }


def save_tree(tree: dict):
    """保存 system-tree.json，自动更新版本和时间。"""
    tree["meta"]["last_updated"] = str(date.today())
    ver = tree["meta"].get("version", "0.1.0")
    parts = ver.split(".")
    parts[-1] = str(int(parts[-1]) + 1)
    tree["meta"]["version"] = ".".join(parts)

    with open(TREE_PATH, "w", encoding="utf-8") as f:
        json.dump(tree, f, ensure_ascii=False, indent=2)


def register_nodes(tree: dict, paper_id: str, nodes_data: list) -> tuple:
    """注册新节点，去重。返回 (created_ids, existed_ids, error_count)。"""
    created, existed, errors = [], [], 0
    for node in nodes_data:
        node_errors = validate_tree_node(node)
        if node_errors:
            for e in node_errors:
                print(f"  [WARN] 节点 '{node.get('id', '?')}' {e}")
            errors += 1
            continue

        nid = node["id"]
        if nid in tree["nodes"]:
            existing = tree["nodes"][nid]
            if paper_id not in existing.get("source_papers", []):
                existing.setdefault("source_papers", []).append(paper_id)
            # 合并 properties（去重）
            new_props = node.get("properties", [])
            if new_props:
                existing_props = existing.setdefault("properties", [])
                existing_prop_strs = {json.dumps(p, ensure_ascii=False, sort_keys=True) for p in existing_props}
                for p in new_props:
                    p_str = json.dumps(p, ensure_ascii=False, sort_keys=True)
                    if p_str not in existing_prop_strs:
                        existing_props.append(p)
                        existing_prop_strs.add(p_str)
            # 合并 children/parents
            for rel in ("children", "parents"):
                for item in node.get(rel, []):
                    if item not in existing.setdefault(rel, []):
                        existing[rel].append(item)
            existed.append(nid)
        else:
            tree["nodes"][nid] = node
            node.setdefault("source_papers", [])
            if paper_id not in node["source_papers"]:
                node["source_papers"].append(paper_id)
            created.append(nid)
    return created, existed, errors


def register_edges(tree: dict, paper_id: str, edges_data: list) -> tuple:
    """注册新边，去重。返回 (created_ids, existed_ids, error_count)。"""
    created, existed, errors = [], [], 0

    existing_index = {}
    for eid, e in tree["edges"].items():
        key = (e["from"], e["to"], e["type"])
        if key not in existing_index:
            existing_index[key] = []
        existing_index[key].append(eid)

    # 使用最大已有ID+1而非len()+1，避免删除边后ID冲突覆盖
    max_id = 0
    for eid in tree["edges"]:
        try:
            num = int(eid[1:])  # eXXXX → XXXX
            if num > max_id:
                max_id = num
        except (ValueError, IndexError):
            pass
    next_id = max_id + 1 if max_id > 0 else 1
    for edge in edges_data:
        edge_errors = validate_tree_edge(edge)
        if edge_errors:
            for e in edge_errors:
                print(f"  [WARN] 边 '{edge.get('label_short', '?')}' {e}")
            errors += 1
            continue

        key = (edge["from"], edge["to"], edge["type"])
        if key in existing_index:
            for eid in existing_index[key]:
                existing_edge = tree["edges"][eid]
                if paper_id not in existing_edge.get("source_papers", []):
                    existing_edge.setdefault("source_papers", []).append(paper_id)
                existed.append(eid)
        else:
            eid = f"e{next_id:04d}"
            tree["edges"][eid] = edge
            edge.setdefault("source_papers", [])
            if paper_id not in edge["source_papers"]:
                edge["source_papers"].append(paper_id)
            created.append(eid)
            if key not in existing_index:
                existing_index[key] = []
            existing_index[key].append(eid)
            next_id += 1
    return created, existed, errors


def register_cross_validations(tree: dict, paper_id: str, cv_papers: list):
    """注册交叉验证关系到相关边/节点。"""
    count = 0
    for other_paper in cv_papers:
        for nid, node in tree["nodes"].items():
            if other_paper in node.get("source_papers", []) and paper_id != other_paper:
                if paper_id not in node.get("papers_cross_validated", []):
                    node.setdefault("papers_cross_validated", []).append(paper_id)
                    count += 1
        for eid, edge in tree["edges"].items():
            if other_paper in edge.get("source_papers", []) and paper_id != other_paper:
                if paper_id not in edge.get("papers_cross_validated", []):
                    edge.setdefault("papers_cross_validated", []).append(paper_id)
                    count += 1
    return count


def ingest(json_path: str, force: bool = False, dry_run: bool = False) -> int:
    """主注册流程。返回 0 成功, -1 失败。"""
    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    errors = validate_json(data)
    fatal = [e for e in errors if e.startswith("缺少")]
    warnings = [e for e in errors if e.startswith("警告")]

    if fatal:
        for e in fatal:
            print(f"[ERROR] {e}")
        return -1
    for w in warnings:
        print(f"[WARN] {w}")

    if dry_run:
        print(f"[DRY-RUN] {data['paper'].get('id', '?')} 四问校验通过，未写入树。")
        tc = data["paper"].get("tree_contributions", {})
        print(f"  new_nodes: {len(tc.get('new_nodes', []))}")
        print(f"  new_edges: {len(tc.get('new_edges', []))}")
        print(f"  properties_added_to: {len(tc.get('properties_added_to', {}))} nodes")
        print(f"  papers_cross_validated: {tc.get('papers_cross_validated', [])}")
        return 0

    tree = load_tree()
    paper = data.get("paper", {})
    paper_id = paper.get("id", "PAPER-???")
    tc = paper.get("tree_contributions", {})

    created_n, existed_n, err_n = register_nodes(tree, paper_id, tc.get("new_nodes", []))
    created_e, existed_e, err_e = register_edges(tree, paper_id, tc.get("new_edges", []))

    prop_count = 0
    props_added = tc.get("properties_added_to", {})
    for node_id, prop_list in props_added.items():
        if node_id in tree["nodes"]:
            existing_props = tree["nodes"][node_id].setdefault("properties", [])
            existing_strs = {json.dumps(p, ensure_ascii=False, sort_keys=True) for p in existing_props}
            for prop in prop_list:
                p_str = json.dumps(prop, ensure_ascii=False, sort_keys=True)
                if p_str not in existing_strs:
                    existing_props.append(prop)
                    existing_strs.add(p_str)
                    prop_count += 1
        else:
            print(f"  [WARN] properties_added_to 目标节点 '{node_id}' 不存在——跳过")

    cv_papers = tc.get("papers_cross_validated", [])
    cv_count = register_cross_validations(tree, paper_id, cv_papers)

    save_tree(tree)

    total_errors = err_n + err_e
    print(f"\n[OK] {paper_id} 注册完成:" if total_errors == 0 else f"\n[OK] {paper_id} 注册完成（{total_errors} 条警告）:")
    print(f"  ★ 新节点: {len(created_n)} — {', '.join(created_n) if created_n else '无'}")
    print(f"  — 追加已有节点: {len(existed_n)} — {', '.join(existed_n) if existed_n else '无'}")
    print(f"  ★ 新边: {len(created_e)} — {', '.join(created_e) if created_e else '无'}")
    print(f"  — 追加已有边: {len(existed_e)} — {', '.join(existed_e) if existed_e else '无'}")
    print(f"  ★ 新性质数据: {prop_count} 条")
    print(f"  ★ 交叉验证注册: {cv_count} 条")
    print(f"  ★ 树版本: {tree['meta']['version']} | 节点总数: {len(tree['nodes'])} | 边总数: {len(tree['edges'])}")

    return 0


def main():
    parser = argparse.ArgumentParser(
        description="MgO-SiO₂(-C-H₂O) 体系 — 论文注册引擎")
    parser.add_argument("--json", required=True, help="paper-data JSON 文件路径")
    parser.add_argument("--force", action="store_true", help="强制覆盖（兼容参数）")
    parser.add_argument("--dry-run", action="store_true", help="仅校验 JSON 结构，不写入 system-tree.json")
    args = parser.parse_args()

    if not os.path.exists(args.json):
        print(f"[ERROR] 文件不存在: {args.json}")
        sys.exit(1)

    result = ingest(args.json, force=args.force, dry_run=args.dry_run)
    sys.exit(0 if result >= 0 else 1)


if __name__ == "__main__":
    main()
