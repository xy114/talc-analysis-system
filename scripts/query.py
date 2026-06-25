#!/usr/bin/env python3
"""滑石粉论文分析体系 — 查询引擎

用法:
  python scripts/query.py --list-all                    # 全论文列表
  python scripts/query.py --paper-id N                  # 单论文详情
  python scripts/query.py --product "氧化镁"             # 按产品筛选
  python scripts/query.py --route C                     # 按技术路线筛选
  python scripts/query.py --min-margin 30               # 毛利率筛选
  python scripts/query.py --compare 3,5,7               # 多论文对比
  python scripts/query.py --synergies-for N             # 关联查询
  python scripts/query.py --unlinked                    # 孤立论文
  python scripts/query.py --top 10                      # Top N
  python scripts/query.py --export --format csv         # CSV 导出
"""

import argparse
import csv
import sqlite3
import sys
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent.parent / "db" / "thesis.db"

HEADER_FIELDS = [
    ("id", 4), ("title", 50), ("route", 4), ("product", 14),
    ("purity", 8), ("yield", 8), ("trl", 4), ("margin", 8), ("score", 6)
]


def connect_db():
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    return conn


def format_row(row, fields=None):
    """将 Row 格式化为对齐字符串。"""
    if fields is None:
        fields = HEADER_FIELDS
    parts = []
    for name, width in fields:
        if isinstance(row, dict):
            val = row.get(name, "")
        else:
            val = row[name] if name in row.keys() else ""
        if val is None:
            val = "-"
        s = str(val)[:width]
        parts.append(s.ljust(width))
    return " | ".join(parts)


def list_all(conn):
    """列出所有论文摘要。"""
    rows = conn.execute(
        """SELECT id, title, tech_route_category AS route,
           target_product_name AS product, target_product_purity AS purity,
           total_yield AS yield, trl_level AS trl, gross_margin AS margin,
           composite_score AS score
           FROM papers ORDER BY composite_score DESC"""
    ).fetchall()

    if not rows:
        print("(论文库为空)")
        return

    header = format_row(dict(zip(
        [f[0] for f in HEADER_FIELDS],
        [f[0].upper() for f in HEADER_FIELDS]
    )), HEADER_FIELDS)
    print(header)
    print("-" * len(header))
    for row in rows:
        print(format_row(row))


def show_detail(conn, paper_id: int):
    """显示单论文完整信息。"""
    row = conn.execute("SELECT * FROM papers WHERE id = ?", (paper_id,)).fetchone()
    if not row:
        print(f"论文 #{paper_id} 不存在")
        return

    print(f"\n{'='*60}")
    print(f"  PAPER-{row['id']:03d}: {row['title']}")
    print(f"{'='*60}\n")

    sections = [
        ("元信息", ["authors", "institution", "country", "year", "journal",
                     "doi", "research_type", "experiment_scale"]),
        ("研究问题", ["problem_statement", "benchmark_tech"]),
        ("技术路线", ["tech_route_category", "tech_route_detail",
                      "target_product_category", "target_product_name",
                      "target_product_purity", "total_yield"]),
        ("成熟度", ["trl_level", "trl_scale"]),
        ("经济数据", ["capex_has_data", "capex_equipment",
                      "total_cost_per_ton", "product_price_per_ton",
                      "gross_profit_per_ton", "gross_margin", "payback_period"]),
        ("综合评分", ["tech_feasibility_score", "econ_feasibility_score",
                      "market_attractiveness_score", "scaleup_feasibility_score",
                      "composite_score"]),
    ]

    for section_name, fields in sections:
        print(f"[{section_name}]")
        for f in fields:
            val = row[f] if row[f] is not None else "-"
            label = f.replace("_", " ").title()
            print(f"  {label}: {val}")
        print()

    # 子表
    steps = conn.execute(
        "SELECT * FROM process_steps WHERE paper_id=? ORDER BY step_order",
        (paper_id,)).fetchall()
    if steps:
        print("[产率链]")
        for s in steps:
            bn = " !!瓶颈" if s["is_bottleneck"] else ""
            print(f"  步骤{s['step_order']}: {s['step_name']} "
                  f"-> {s['conversion_rate']}%{bn}")
        print()

    env = conn.execute(
        "SELECT * FROM environmental WHERE paper_id=?", (paper_id,)).fetchone()
    if env:
        print("[环保与副产品]")
        print(f"  副产品: {env['byproduct_name'] or '-'} "
              f"价值: {env['byproduct_value'] or '-'} 元/吨")
        print()


def filter_by_product(conn, product: str):
    """按产品名称模糊筛选。"""
    rows = conn.execute(
        """SELECT id, title, target_product_name, gross_margin, composite_score
           FROM papers WHERE target_product_name LIKE ?
           ORDER BY composite_score DESC""",
        (f"%{product}%",)
    ).fetchall()
    if not rows:
        print(f"未找到产品包含 '{product}' 的论文")
        return
    print(f"\n产品筛选: {product} ({len(rows)} 篇)")
    print("-" * 60)
    for r in rows:
        print(f"  #{r['id']} | {r['target_product_name']} | "
              f"毛利率:{r['gross_margin'] or '-'}% | 评分:{r['composite_score']}")


def filter_by_route(conn, route: str):
    """按技术路线筛选。"""
    route_labels = {
        "A": "物理法", "B": "热化学法", "C": "湿法酸法",
        "D": "湿法碱法", "E": "碳化法", "F": "电化学法",
        "G": "生物法", "H": "组合/耦合工艺"
    }
    rows = conn.execute(
        """SELECT id, title, target_product_name, gross_margin, composite_score
           FROM papers WHERE tech_route_category = ?
           ORDER BY composite_score DESC""",
        (route.upper(),)
    ).fetchall()
    label = route_labels.get(route.upper(), route)
    if not rows:
        print(f"未找到技术路线为 '{label}' 的论文")
        return
    print(f"\n技术路线: {route.upper()} - {label} ({len(rows)} 篇)")
    print("-" * 60)
    for r in rows:
        print(f"  #{r['id']} | {r['target_product_name']} | "
              f"毛利率:{r['gross_margin'] or '-'}% | 评分:{r['composite_score']}")


def filter_by_margin(conn, min_margin: float):
    """按最低毛利率筛选。"""
    rows = conn.execute(
        """SELECT id, title, target_product_name, gross_margin, composite_score
           FROM papers WHERE gross_margin >= ?
           ORDER BY gross_margin DESC""",
        (min_margin,)
    ).fetchall()
    if not rows:
        print(f"未找到毛利率 >= {min_margin}% 的论文")
        return
    print(f"\n毛利率 >= {min_margin}% ({len(rows)} 篇)")
    print("-" * 60)
    for r in rows:
        print(f"  #{r['id']} | {r['target_product_name']} | "
              f"毛利率:{r['gross_margin']}% | 评分:{r['composite_score']}")


def compare_papers(conn, ids: list):
    """多论文横向对比。"""
    placeholders = ",".join("?" for _ in ids)
    rows = conn.execute(
        f"""SELECT id, title, tech_route_category, target_product_name,
            target_product_purity, total_yield, trl_level,
            total_cost_per_ton, product_price_per_ton,
            gross_margin, payback_period, composite_score
            FROM papers WHERE id IN ({placeholders})
            ORDER BY id""",
        ids
    ).fetchall()

    if not rows:
        print("未找到指定论文")
        return

    comp_fields = [
        ("id", "ID", 4), ("target_product_name", "产品", 14),
        ("tech_route_category", "路线", 4),
        ("target_product_purity", "纯度%", 7),
        ("total_yield", "产率%", 7), ("trl_level", "TRL", 4),
        ("total_cost_per_ton", "成本元/t", 10),
        ("product_price_per_ton", "售价元/t", 10),
        ("gross_margin", "毛利率%", 8), ("payback_period", "回收期年", 8),
        ("composite_score", "评分", 5)
    ]

    print(f"\n{'='*80}")
    print(f"  论文横向对比 ({len(rows)} 篇)")
    print(f"{'='*80}\n")

    header = " | ".join(label.ljust(w) for _, label, w in comp_fields)
    print(header)
    print("-" * len(header))
    for row in rows:
        parts = []
        for key, _, width in comp_fields:
            val = row[key] if key in row.keys() else "-"
            if val is None:
                val = "-"
            parts.append(str(val)[:width].ljust(width))
        print(" | ".join(parts))


def show_synergies(conn, paper_id: int):
    """显示某论文的所有关联。"""
    rows = conn.execute(
        """SELECT s.*, p.title AS other_title
           FROM synergies s
           JOIN papers p ON (
             CASE WHEN s.paper_id_a = ? THEN s.paper_id_b
                  ELSE s.paper_id_a
             END = p.id
           )
           WHERE s.paper_id_a = ? OR s.paper_id_b = ?
           ORDER BY s.synergy_type""",
        (paper_id, paper_id, paper_id)
    ).fetchall()

    if not rows:
        print(f"论文 #{paper_id} 暂无关联")
        return

    print(f"\n论文 #{paper_id} 的关联网络 ({len(rows)} 条)")
    print("-" * 60)
    for r in rows:
        other_id = (r["paper_id_b"] if r["paper_id_a"] == paper_id
                    else r["paper_id_a"])
        print(f"  -> #{other_id} [{r['synergy_type']}] "
              f"强度:{r['synergy_strength']} | {r['other_title'][:40]}")


def show_unlinked(conn):
    """找出没有任何关联的孤立论文。"""
    rows = conn.execute(
        """SELECT id, title FROM papers
           WHERE id NOT IN (
             SELECT paper_id_a FROM synergies
             UNION
             SELECT paper_id_b FROM synergies
           )
           ORDER BY id"""
    ).fetchall()
    if not rows:
        print("所有论文均已建立关联。")
        return
    print(f"\n未建立关联的论文 ({len(rows)} 篇):")
    for r in rows:
        print(f"  #{r['id']}: {r['title'][:50]}")


def show_top(conn, n: int):
    """按综合评分排序 Top N。"""
    rows = conn.execute(
        """SELECT id, title, target_product_name, tech_route_category,
           gross_margin, composite_score
           FROM papers ORDER BY composite_score DESC LIMIT ?""",
        (n,)
    ).fetchall()
    if not rows:
        print("(论文库为空)")
        return
    print(f"\n综合评分 Top {n}:")
    print("-" * 60)
    for i, r in enumerate(rows, 1):
        print(f"  {i}. #{r['id']} [{r['composite_score']}] "
              f"{r['target_product_name']} | {r['title'][:40]}")


def export_csv(conn):
    """导出全量数据为 CSV。"""
    out_path = Path(__file__).resolve().parent.parent / "papers_export.csv"
    rows = conn.execute("SELECT * FROM papers ORDER BY id").fetchall()
    if not rows:
        print("(论文库为空，无数据可导出)")
        return

    with open(out_path, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.writer(f)
        writer.writerow(rows[0].keys())
        for row in rows:
            writer.writerow(row)

    print(f"[OK] 已导出 {len(rows)} 篇论文至: {out_path}")


def main():
    parser = argparse.ArgumentParser(
        description="滑石粉论文分析体系 — 查询引擎")
    parser.add_argument("--list-all", action="store_true",
                        help="列出所有论文摘要")
    parser.add_argument("--paper-id", type=int, help="查看单论文详情")
    parser.add_argument("--product", type=str, help="按产品名称筛选")
    parser.add_argument("--route", type=str, help="按技术路线筛选 (A-H)")
    parser.add_argument("--min-margin", type=float, help="最低毛利率筛选")
    parser.add_argument("--compare", type=str, help="多论文对比，逗号分隔ID")
    parser.add_argument("--synergies-for", type=int, help="查看某论文关联")
    parser.add_argument("--unlinked", action="store_true", help="孤立论文")
    parser.add_argument("--top", type=int, help="Top N")
    parser.add_argument("--export", action="store_true", help="导出 CSV")
    parser.add_argument("--format", type=str, choices=["csv"],
                        help="导出格式")

    args = parser.parse_args()

    has_args = (args.list_all or args.product or args.route
                or args.unlinked or args.export
                or args.paper_id is not None
                or args.min_margin is not None
                or args.compare is not None
                or args.synergies_for is not None
                or args.top is not None)
    if not has_args:
        parser.print_help()
        sys.exit(0)

    conn = connect_db()

    if args.list_all:
        list_all(conn)
    elif args.paper_id is not None:
        show_detail(conn, args.paper_id)
    elif args.product:
        filter_by_product(conn, args.product)
    elif args.route:
        filter_by_route(conn, args.route)
    elif args.min_margin is not None:
        filter_by_margin(conn, args.min_margin)
    elif args.compare is not None:
        try:
            ids = [int(x.strip()) for x in args.compare.split(",") if x.strip()]
            if not ids:
                print("[ERROR] --compare 需要有效的论文 ID 列表，例如 --compare 1,2,3")
                sys.exit(1)
            compare_papers(conn, ids)
        except ValueError:
            print("[ERROR] --compare 参数格式错误，请使用逗号分隔的整数 ID，例如 --compare 1,2,3")
            sys.exit(1)
    elif args.synergies_for is not None:
        show_synergies(conn, args.synergies_for)
    elif args.unlinked:
        show_unlinked(conn)
    elif args.top is not None:
        if args.top <= 0:
            print("[ERROR] --top 需要正整数")
            sys.exit(1)
        show_top(conn, args.top)
    elif args.export:
        export_csv(conn)

    conn.close()


if __name__ == "__main__":
    main()
