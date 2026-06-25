#!/usr/bin/env python3
"""滑石粉论文分析体系 — 入库引擎

用法:
  python scripts/ingest.py --json data.json           # 入库
  python scripts/ingest.py --json data.json --force   # 覆盖已存在论文
  python scripts/ingest.py --json data.json --dry-run # 校验但不写入
"""

import argparse
import json
import sqlite3
import sys
import os
from datetime import date
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent.parent / "db" / "thesis.db"

REQUIRED_PAPER_FIELDS = [
    "title", "tech_route_category", "target_product_category"
]

SYNERGY_RULES = [
    {
        "name": "对标竞争",
        "sql": """
            SELECT id FROM papers
            WHERE target_product_category = ?
              AND tech_route_category != ?
              AND id != ?
        """
    },
    {
        "name": "副产品利用",
        "sql": """
            SELECT DISTINCT p.id FROM papers p
            JOIN environmental e ON e.paper_id = p.id
            WHERE e.byproduct_name LIKE '%' || ? || '%'
              AND p.id != ?
        """
    },
    {
        "name": "工艺互补",
        "sql": """
            SELECT id FROM papers
            WHERE tech_route_category = 'H'
              AND tech_route_detail LIKE '%' || ? || '%'
              AND id != ?
        """
    },
    {
        "name": "上下游衔接",
        "sql": """
            SELECT DISTINCT p.id FROM papers p
            JOIN paper_attributes a ON a.paper_id = p.id
            WHERE a.category = 'auxiliary_material'
              AND a.attr_value LIKE '%' || ? || '%'
              AND p.id != ?
        """
    },
    {
        "name": "设备共用",
        "sql": """
            SELECT DISTINCT p.id FROM papers p
            JOIN paper_attributes a ON a.paper_id = p.id
            WHERE a.category = 'equipment'
              AND a.attr_key = 'core_reactor_type'
              AND a.attr_value = ?
              AND p.id != ?
        """
    },
    {
        "name": "联合生产",
        "sql": """
            SELECT DISTINCT p.id FROM papers p
            JOIN paper_attributes a1 ON a1.paper_id = p.id
            JOIN paper_attributes a2 ON a2.paper_id = ?
            WHERE a1.category = 'raw_material_spec'
              AND a1.attr_key = 'source_mineral'
              AND a2.category = 'raw_material_spec'
              AND a2.attr_key = 'source_mineral'
              AND a1.attr_value = a2.attr_value
              AND p.target_product_category != ?
              AND p.id != ?
        """
    },
    {
        "name": "条件优化借鉴",
        "sql": """
            SELECT DISTINCT p.id FROM papers p
            JOIN paper_attributes a1 ON a1.paper_id = p.id
            JOIN paper_attributes a2 ON a2.paper_id = ?
            WHERE a1.category = 'process_params'
              AND a2.category = 'process_params'
              AND a1.attr_key = a2.attr_key
              AND p.tech_route_category = ?
              AND p.id != ?
        """
    },
]


def connect_db():
    """连接数据库，确保外键开启。"""
    conn = sqlite3.connect(str(DB_PATH))
    conn.execute("PRAGMA foreign_keys = ON")
    conn.row_factory = sqlite3.Row
    return conn


def validate_json(data: dict) -> list:
    """校验 JSON 结构完整性，返回错误列表。"""
    errors = []
    paper = data.get("paper", {})
    for field in REQUIRED_PAPER_FIELDS:
        if not paper.get(field):
            errors.append(f"缺少必填字段: paper.{field}")
    if not paper.get("doi"):
        errors.append("警告: paper.doi 为空，将无法自动去重")
    return errors


def check_doi_exists(conn, doi: str):
    """检查 DOI 是否已入库，返回 paper_id 或 None。"""
    if not doi:
        return None
    row = conn.execute("SELECT id FROM papers WHERE doi = ?", (doi,)).fetchone()
    return row["id"] if row else None


def insert_paper(conn, paper: dict) -> int:
    """写入 papers 表，返回 paper_id。"""
    fields = [
        "title", "authors", "institution", "country", "year", "journal",
        "doi", "research_type", "problem_statement", "raw_material_source",
        "benchmark_tech", "has_experiment", "has_economic_data",
        "experiment_scale", "citation_quality", "tech_route_category",
        "tech_route_detail", "target_product_category", "target_product_name",
        "target_product_purity", "total_yield", "trl_level", "trl_scale",
        "capex_has_data", "capex_equipment", "capex_total_per_10kt",
        "opex_has_data", "opex_raw_material_per_ton", "opex_energy_per_ton",
        "total_cost_per_ton", "product_price_per_ton", "gross_profit_per_ton",
        "gross_margin", "payback_period", "tech_feasibility_score",
        "econ_feasibility_score", "market_attractiveness_score",
        "scaleup_feasibility_score", "composite_score", "analyst_notes"
    ]
    values = {f: paper.get(f) for f in fields}
    values["analysis_date"] = paper.get("analysis_date", str(date.today()))

    columns = ", ".join(values.keys())
    placeholders = ", ".join("?" for _ in values)
    sql = f"INSERT INTO papers ({columns}) VALUES ({placeholders})"

    cursor = conn.execute(sql, list(values.values()))
    return cursor.lastrowid


def insert_child_rows(conn, paper_id: int, data: dict):
    """写入子表：process_steps, energy_breakdown, environmental, attributes。"""
    # process_steps
    for step in data.get("process_steps", []):
        conn.execute(
            """INSERT INTO process_steps (paper_id, step_order, step_name,
               conversion_rate, is_bottleneck, notes)
               VALUES (?, ?, ?, ?, ?, ?)""",
            (paper_id, step.get("step_order"), step.get("step_name"),
             step.get("conversion_rate"), step.get("is_bottleneck", 0),
             step.get("notes"))
        )

    # energy_breakdown
    for e in data.get("energy", []):
        conn.execute(
            """INSERT INTO energy_breakdown (paper_id, step_name, heat_energy,
               electricity, energy_share_pct, heat_recovery_potential)
               VALUES (?, ?, ?, ?, ?, ?)""",
            (paper_id, e.get("step_name"), e.get("heat_energy"),
             e.get("electricity"), e.get("energy_share_pct"),
             e.get("heat_recovery_potential"))
        )

    # environmental (only one row per paper, UNIQUE constraint)
    env = data.get("environmental", {})
    if env:
        conn.execute(
            """INSERT INTO environmental (paper_id, waste_gas_type,
               waste_gas_amount, waste_gas_treatment, waste_gas_cost,
               waste_water_type, waste_water_amount, waste_water_treatment,
               waste_water_cost, solid_waste_type, solid_waste_amount,
               solid_waste_reusable, byproduct_name, byproduct_value,
               byproduct_revenue_share, meets_env_policy)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (paper_id, env.get("waste_gas_type"), env.get("waste_gas_amount"),
             env.get("waste_gas_treatment"), env.get("waste_gas_cost"),
             env.get("waste_water_type"), env.get("waste_water_amount"),
             env.get("waste_water_treatment"), env.get("waste_water_cost"),
             env.get("solid_waste_type"), env.get("solid_waste_amount"),
             env.get("solid_waste_reusable", 0), env.get("byproduct_name"),
             env.get("byproduct_value"), env.get("byproduct_revenue_share"),
             env.get("meets_env_policy"))
        )

    # paper_attributes (EAV)
    for attr in data.get("attributes", []):
        conn.execute(
            """INSERT INTO paper_attributes (paper_id, category, attr_key,
               attr_value, attr_unit, source_context)
               VALUES (?, ?, ?, ?, ?, ?)""",
            (paper_id, attr.get("category"), attr.get("attr_key"),
             attr.get("attr_value"), attr.get("attr_unit"),
             attr.get("source_context"))
        )

    # synergies (手动指定)
    for syn in data.get("synergies", []):
        conn.execute(
            """INSERT INTO synergies (paper_id_a, paper_id_b, synergy_type,
               synergy_strength, synergy_description, combined_potential_score)
               VALUES (?, ?, ?, ?, ?, ?)""",
            (paper_id, syn.get("paper_id_b"), syn.get("synergy_type"),
             syn.get("synergy_strength", "中"), syn.get("synergy_description"),
             syn.get("combined_potential_score"))
        )


def auto_detect_synergies(conn, paper_id: int, paper: dict) -> list:
    """自动检测新论文与已有论文的潜在关联。"""
    found = []
    product = paper.get("target_product_name", "")
    route_cat = paper.get("tech_route_category", "")
    product_cat = paper.get("target_product_category", "")

    for rule in SYNERGY_RULES:
        try:
            if rule["name"] == "对标竞争":
                rows = conn.execute(rule["sql"],
                    (product_cat, route_cat, paper_id)).fetchall()
            elif rule["name"] == "副产品利用":
                rows = conn.execute(rule["sql"],
                    (product, paper_id)).fetchall()
            elif rule["name"] == "工艺互补":
                if route_cat in ("B", "C", "E"):
                    rows = conn.execute(rule["sql"],
                        (route_cat, paper_id)).fetchall()
                else:
                    continue
            elif rule["name"] == "上下游衔接":
                rows = conn.execute(rule["sql"],
                    (product, paper_id)).fetchall()
            elif rule["name"] == "设备共用":
                attr = conn.execute(
                    """SELECT attr_value FROM paper_attributes
                       WHERE paper_id = ? AND category = 'equipment'
                       AND attr_key = 'core_reactor_type'""",
                    (paper_id,)).fetchone()
                if attr:
                    rows = conn.execute(rule["sql"],
                        (attr["attr_value"], paper_id)).fetchall()
                else:
                    continue
            elif rule["name"] == "联合生产":
                rows = conn.execute(rule["sql"],
                    (paper_id, product_cat, paper_id)).fetchall()
            elif rule["name"] == "条件优化借鉴":
                rows = conn.execute(rule["sql"],
                    (paper_id, route_cat, paper_id)).fetchall()
            else:
                continue

            for row in rows:
                found.append({
                    "paper_id_b": row["id"],
                    "synergy_type": rule["name"],
                    "synergy_strength": "中",
                    "auto_detected": True
                })
        except sqlite3.Error:
            continue

    return found


def ingest(json_path: str, force: bool = False, dry_run: bool = False) -> int:
    """主入库流程。返回入库的 paper_id，失败返回 -1。"""
    # 读取 JSON
    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    # 校验
    errors = validate_json(data)
    if errors:
        for e in errors:
            print(f"[ERROR] {e}")
        if any(e.startswith("缺少") for e in errors):
            return -1

    if dry_run:
        print("[DRY-RUN] JSON 结构校验通过，未写入数据库。")
        return 0

    conn = connect_db()
    paper = data.get("paper", {})

    try:
        # 去重检查
        existing_id = check_doi_exists(conn, paper.get("doi", ""))
        if existing_id and not force:
            print(f"[SKIP] DOI 已存在: paper_id={existing_id}")
            print(f"       使用 --force 覆盖更新")
            return existing_id

        if existing_id and force:
            conn.execute("DELETE FROM papers WHERE id = ?", (existing_id,))
            print(f"[UPDATE] 覆盖已有论文 paper_id={existing_id}")

        # 写入主表
        paper_id = insert_paper(conn, paper)
        print(f"[OK] 论文入库: paper_id={paper_id} 标题: {paper.get('title', '')[:60]}")

        # 写入子表
        insert_child_rows(conn, paper_id, data)

        # 自动关联检测
        found = auto_detect_synergies(conn, paper_id, paper)
        if found:
            print(f"\n[SYNERGY] 检测到 {len(found)} 条潜在关联:")
            for s in found:
                row = conn.execute(
                    "SELECT title FROM papers WHERE id = ?",
                    (s["paper_id_b"],)).fetchone()
                other_title = row["title"][:50] if row else "?"
                conn.execute(
                    """INSERT INTO synergies (paper_id_a, paper_id_b,
                       synergy_type, synergy_strength, synergy_description)
                       VALUES (?, ?, ?, ?, ?)""",
                    (paper_id, s["paper_id_b"], s["synergy_type"],
                     s["synergy_strength"],
                     f"自动检测: {s['synergy_type']} - 论文#{s['paper_id_b']}")
                )
                print(f"  → #{s['paper_id_b']} [{s['synergy_type']}] {other_title}")
        else:
            print("\n[SYNERGY] 未检测到关联（或论文库为空）")

        conn.commit()
        return paper_id

    except sqlite3.Error as e:
        print(f"[ERROR] 数据库错误: {e}")
        conn.rollback()
        return -1
    finally:
        conn.close()


def main():
    parser = argparse.ArgumentParser(
        description="滑石粉论文分析体系 — 入库引擎")
    parser.add_argument("--json", required=True, help="JSON 数据文件路径")
    parser.add_argument("--force", action="store_true",
                        help="覆盖已存在的论文 (按 DOI 匹配)")
    parser.add_argument("--dry-run", action="store_true",
                        help="仅校验 JSON 结构，不写入数据库")
    args = parser.parse_args()

    if not os.path.exists(args.json):
        print(f"[ERROR] 文件不存在: {args.json}")
        sys.exit(1)

    result = ingest(args.json, force=args.force, dry_run=args.dry_run)
    sys.exit(0 if result >= 0 else 1)


if __name__ == "__main__":
    main()
