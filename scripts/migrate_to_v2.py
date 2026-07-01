#!/usr/bin/env python3
"""MgO-SiO₂(-C-H₂O) 体系树 — v1 → v2 schema 迁移
将 product 节点按 source_papers / process_route 拆分为独立节点。

用法:
  python scripts/migrate_to_v2.py --dry-run   # 预览变更，不写入
  python scripts/migrate_to_v2.py              # 执行迁移
"""

import argparse
import json
import sys
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
LEGACY_PATH = ROOT / "system-tree-v0.1.19-legacy.json"
TREE_PATH = ROOT / "system-tree.json"


# ===== 命名映射表 =====
# key: (old_node_id, source_paper)
# value: (new_node_id, new_node_name, route_description)

PRODUCT_SPLIT_MAP = {
    # black_talc_mw_ceramic → 3 routes
    ("black_talc_mw_ceramic", "PAPER-004"): (
        "black_talc_mw_direct",
        "黑滑石微波介质陶瓷(原矿1325°C)",
        "enstatite 原矿直接烧结 1325°C"
    ),
    ("black_talc_mw_ceramic", "PAPER-010"): (
        "black_talc_mw_cu",
        "黑滑石微波介质陶瓷(Cu²⁺掺杂)",
        "Cu²⁺掺杂→抑制proto→ortho相变"
    ),
    ("black_talc_mw_ceramic", "PAPER-011"): (
        "black_talc_mw_co",
        "黑滑石微波介质陶瓷(Co²⁺掺杂)",
        "Co²⁺掺杂→Q×f=145846 近零τf"
    ),
    # forsterite_mw_ceramic → 2 routes
    ("forsterite_mw_ceramic", "PAPER-018"): (
        "forsterite_mw_pure",
        "镁橄榄石微波介质陶瓷(纯试剂+LPD-TiO₂)",
        "高纯Mg(OH)₂+SiO₂→多孔Mg₂SiO₄→LPD TiO₂ τf补偿"
    ),
    ("forsterite_mw_ceramic", "PAPER-020"): (
        "forsterite_mw_talc",
        "镁橄榄石微波介质陶瓷(黑滑石+B₂O₃)",
        "广丰黑滑石+MgO补Mg→B₂O₃助烧 1350°C"
    ),
    # 单路线产品 — ID 不变，名称加工艺描述
    ("camgsio4_ceramic", "PAPER-008"): (
        "camgsio4_ceramic",
        "钙镁橄榄石微波介质陶瓷(CaO固相反应)",
        "CaO+MgSiO₃→CaMgSiO₄ 成本降80%"
    ),
    ("li2mgsio4_ceramic", "PAPER-009"): (
        "li2mgsio4_ceramic",
        "硅酸镁锂微波介质陶瓷(Li₂CO₃低温烧结)",
        "MgSiO₃+Li₂CO₃→Li₂MgSiO₄+CO₂↑ 1075°C"
    ),
    ("cordierite_ceramic", "PAPER-002"): (
        "cordierite_ceramic",
        "堇青石陶瓷(煤矸石+铝矾土)",
        "2MgSiO₃+2Al₂O₃+3SiO₂→Mg₂Al₄Si₅O₁₈"
    ),
    ("forsterite_tbc", "PAPER-019"): (
        "forsterite_tbc",
        "镁橄榄石热障涂层(APS喷涂)",
        "Mg₂SiO₄→APS喷涂→>830次热循环 1273K"
    ),
    ("refractory_brick", "PAPER-002"): (
        "refractory_brick",
        "镁橄榄石耐火砖(高温烧结)",
        ">1100°C煅烧→Mg₂SiO₄→成型烧结→耐火砖"
    ),
    ("talc_photocatalyst", "PAPER-002"): (
        "talc_photocatalyst",
        "黑滑石光催化剂(TiO₂限域)",
        "溶胶凝胶TiO₂/黑滑石→光催化降解"
    ),
    ("talc_antibacterial", "PAPER-002"): (
        "talc_antibacterial",
        "黑滑石抗菌材料(离子交换)",
        "酸活化→Ag⁺/Cu²⁺/Zn²⁺植入→缓释抗菌"
    ),
    ("zn_enstatite_antibacterial", "PAPER-003"): (
        "zn_enstatite_antibacterial",
        "Zn-顽火辉石抗菌材料(ZnSO₄晶格重建)",
        "HCl酸活化→ZnSO₄处理→Zn²⁺晶格重建→缓释抗菌"
    ),
}


def load_legacy():
    with open(LEGACY_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def migrate(old_tree: dict) -> dict:
    old_nodes = old_tree["nodes"]
    old_edges = old_tree["edges"]

    # ===== 1. 拆分产品节点 =====
    new_nodes = {}
    node_id_map = {}  # old_node_id → [(new_node_id, paper_id, cv_list), ...]

    for nid, node in old_nodes.items():
        if node.get("type") == "product":
            all_props = node.get("properties", [])
            # 按每个 property 的 source_papers 分组
            prop_groups = {}
            for p in all_props:
                for sp in p.get("source_papers", []):
                    prop_groups.setdefault(sp, []).append(p)

            # 确保 node.source_papers 中的论文都有条目（即使无独立 properties）
            node_sps = node.get("source_papers", [])
            for sp in node_sps:
                if sp not in prop_groups:
                    prop_groups[sp] = []

            cv_list = node.get("papers_cross_validated", [])

            for sp, props in prop_groups.items():
                key = (nid, sp)
                if key in PRODUCT_SPLIT_MAP:
                    new_nid, new_name, route_desc = PRODUCT_SPLIT_MAP[key]
                else:
                    new_nid = f"{nid}_{sp.lower().replace('-','_')}"
                    new_name = f"{node['name']}({sp})"
                    route_desc = sp
                    print(f"  [INFO] 自动命名: {new_nid} = {new_name}")

                new_node = {
                    "id": new_nid,
                    "name": new_name,
                    "name_en": node.get("name_en", new_name),
                    "formula": node.get("formula", ""),
                    "type": "product",
                    "depth": node.get("depth", 2),
                    "children": [],
                    "parents": list(node.get("parents", [])),
                    "properties": props,
                    "source_papers": [sp],
                    "notes": node.get("notes", ""),
                }
                new_nodes[new_nid] = new_node

                if nid not in node_id_map:
                    node_id_map[nid] = []
                node_id_map[nid].append((new_nid, sp, cv_list))
        else:
            # 中间相/原料：原样保留
            new_nodes[nid] = node
            # 清理 children 列表——后面从边重新推导
            node_id_map[nid] = [(nid, None, node.get("papers_cross_validated", []))]

    # ===== 2. 重建边 =====
    new_edges = {}

    # 确定起始边 ID
    max_eid = 0
    for eid_key in old_edges:
        try:
            num = int(eid_key[1:])
            if num > max_eid:
                max_eid = num
        except (ValueError, IndexError):
            pass
    edge_id_counter = max_eid + 1

    # 用于追踪哪些 product 节点已通过边连接
    connected_products = set()

    for eid_key, edge in old_edges.items():
        old_to = edge["to"]
        edge_sps = edge.get("source_papers", [])

        if old_to in node_id_map and len(node_id_map[old_to]) > 1:
            # product 被拆分 → 按 source_papers 拆边
            new_targets = node_id_map[old_to]
            for sp in edge_sps:
                matched = [nt for nt in new_targets if nt[1] == sp]
                if matched:
                    new_to, _, cv_list = matched[0]
                    new_edge = dict(edge)
                    new_edge["to"] = new_to
                    new_edge["source_papers"] = [sp]
                    new_edge["papers_cross_validated"] = list(cv_list)
                    new_eid = f"e{edge_id_counter:04d}"
                    new_edges[new_eid] = new_edge
                    edge_id_counter += 1
                    connected_products.add(new_to)
                else:
                    print(f"  [WARN] 边 {eid_key}: source_paper {sp} 无匹配新节点 — 跳过")

            # 如果旧边只有一个 source_paper 但 product 有多个 source_paper，
            # 其他 product 子节点可能缺少边（如 PAPER-011 被去重合并）
        else:
            # 单路线 product 或中间相 → 直接映射
            new_to = node_id_map[old_to][0][0]
            cv_list = node_id_map[old_to][0][2]
            new_edge = dict(edge)
            new_edge["to"] = new_to
            new_edge["papers_cross_validated"] = list(cv_list)
            new_eid = f"e{edge_id_counter:04d}"
            new_edges[new_eid] = new_edge
            edge_id_counter += 1
            if new_nodes[new_to].get("type") == "product":
                connected_products.add(new_to)

    # ===== 3. 为缺少边的 product 节点补建边 =====
    # 查找 product 节点的父中间相 → 新建 process 边
    orphan_products = []
    for nid, node in new_nodes.items():
        if node.get("type") == "product" and nid not in connected_products:
            orphan_products.append(nid)

    for nid in orphan_products:
        node = new_nodes[nid]
        sp = node.get("source_papers", ["?"])[0]
        parents = node.get("parents", [])

        if parents:
            parent_id = parents[0]
            desc = PRODUCT_SPLIT_MAP.get((None, sp), ("", "", ""))
            # 从映射表取 route 描述
            route_desc = ""
            for (old_nid, paper), (new_nid, name, rd) in PRODUCT_SPLIT_MAP.items():
                if new_nid == nid:
                    route_desc = rd
                    old_nid_for_lookup = old_nid
                    break
            else:
                route_desc = sp
                old_nid_for_lookup = "?"

            # 从旧边中找一条同类型边作模板
            template = None
            for old_eid, old_e in old_edges.items():
                if old_e["type"] == "process":
                    template = old_e
                    break

            label = route_desc[:60] if route_desc else f"{sp}路线"

            new_edge = {
                "from": parent_id,
                "to": nid,
                "type": "process",
                "label_short": label,
                "conditions": template.get("conditions", {}) if template else {},
                "source_papers": [sp],
                "trl": template.get("trl", 3) if template else 3,
                "notes": f"自动补建边 (PAPER-011 在旧 schema 中被去重合并丢失)",
            }
            new_eid = f"e{edge_id_counter:04d}"
            new_edges[new_eid] = new_edge
            edge_id_counter += 1
            connected_products.add(nid)
            print(f"  [FIX] {new_eid}: {parent_id} → {nid} (孤儿节点补建边)")

    # ===== 4. 重建 children/parents 引用 =====
    # 4a. 清空所有中间相节点的 children（按边重新推导）
    for nid, node in new_nodes.items():
        if node.get("type") != "product":
            node["children"] = []

    # 4b. 从边重建 children
    child_map = {}
    for eid, edge in new_edges.items():
        parent = edge["from"]
        child = edge["to"]
        if parent in new_nodes:
            child_map.setdefault(parent, [])
            if child not in child_map[parent]:
                child_map[parent].append(child)

    for parent_id, children in child_map.items():
        if parent_id in new_nodes:
            new_nodes[parent_id]["children"] = children

    # 4c. 从边重建 product parents
    for nid, node in new_nodes.items():
        if node.get("type") == "product":
            derived_parents = []
            for eid, edge in new_edges.items():
                if edge["to"] == nid and edge["from"] not in derived_parents:
                    derived_parents.append(edge["from"])
            node["parents"] = derived_parents

    return {
        "meta": {
            "name": "黑滑石 MgO-SiO₂(-C-H₂O) 物相-应用体系树",
            "version": "0.2.0",
            "last_updated": str(date.today()),
            "description": "v2 schema: 产品节点按工艺路线拆分，边=工艺路线，性质=该路线数据"
        },
        "nodes": new_nodes,
        "edges": new_edges,
    }


def print_diff(old_tree: dict, new_tree: dict):
    old_n = len(old_tree["nodes"])
    new_n = len(new_tree["nodes"])
    old_e = len(old_tree["edges"])
    new_e = len(new_tree["edges"])

    print(f"\n===== 迁移摘要 =====")
    print(f"节点: {old_n} → {new_n} (+{new_n - old_n})")
    print(f"边:   {old_e} → {new_e} (+{new_e - old_e})")
    print(f"版本: {old_tree['meta']['version']} → 0.2.0")

    old_product_ids = {nid for nid, n in old_tree["nodes"].items() if n.get("type") == "product"}
    new_product_ids = {nid for nid, n in new_tree["nodes"].items() if n.get("type") == "product"}

    print(f"\n===== 新产品节点 ({len(new_product_ids)}个) =====")
    for nid in sorted(new_product_ids):
        node = new_tree["nodes"][nid]
        sp = node.get("source_papers", ["?"])[0]
        props = len(node.get("properties", []))
        mark = " ★NEW" if nid not in old_product_ids else ""
        print(f"  {nid}: {node['name'][:55]} [{sp}] ({props} props){mark}")

    print(f"\n===== 已移除旧产品节点 =====")
    for nid in sorted(old_product_ids - new_product_ids):
        print(f"  - {nid}: {old_tree['nodes'][nid]['name']}")


def main():
    parser = argparse.ArgumentParser(description="v1 → v2 schema 迁移")
    parser.add_argument("--dry-run", action="store_true", help="仅预览变更")
    parser.add_argument("--legacy", default=str(LEGACY_PATH), help="旧版树路径")
    args = parser.parse_args()

    legacy_path = Path(args.legacy)
    if not legacy_path.exists():
        print(f"[ERROR] 旧版树不存在: {legacy_path}")
        sys.exit(1)

    old_tree = json.loads(legacy_path.read_text(encoding="utf-8"))
    new_tree = migrate(old_tree)
    print_diff(old_tree, new_tree)

    if args.dry_run:
        print(f"\n[DRY-RUN] 未写入。使用 'python scripts/migrate_to_v2.py' 执行迁移。")
        return 0

    TREE_PATH.write_text(json.dumps(new_tree, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\n[OK] 迁移完成 → {TREE_PATH}")
    print(f"  节点: {len(new_tree['nodes'])} | 边: {len(new_tree['edges'])}")
    return 0


if __name__ == "__main__":
    main()
