#!/usr/bin/env python3
"""滑石粉论文分析体系 — 报告生成器

用法:
  python scripts/report.py --paper-id N         # 单篇报告
  python scripts/report.py --all                # 批量全量
  python scripts/report.py --synergy-report     # 全局关联网络报告
"""

import argparse
import sqlite3
import sys
from datetime import date
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent.parent / "db" / "thesis.db"
PAPERS_DIR = Path(__file__).resolve().parent.parent / "papers"


def connect_db():
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    return conn


def build_report(conn, paper_id: int):
    """生成单篇论文的 Markdown 报告。返回字符串或 None。"""
    row = conn.execute(
        "SELECT * FROM papers WHERE id = ?", (paper_id,)
    ).fetchone()
    if not row:
        return None

    def v(key, default="-"):
        val = row[key] if row[key] is not None else default
        return str(val)

    # 产率链
    steps = conn.execute(
        "SELECT * FROM process_steps WHERE paper_id=? ORDER BY step_order",
        (paper_id,)).fetchall()
    steps_md = ""
    for s in steps:
        bn = " !!瓶颈" if s["is_bottleneck"] else ""
        cr = s['conversion_rate']
        cr_str = f"{cr}%" if cr is not None else "-"
        steps_md += (f"| {s['step_order']} | {s['step_name'] or '-'} | "
                     f"{cr_str} |{bn} |\n")

    # 关联论文
    synergies = conn.execute(
        """SELECT s.*, p.title AS other_title
           FROM synergies s
           JOIN papers p ON (
             CASE WHEN s.paper_id_a = ? THEN s.paper_id_b
                  ELSE s.paper_id_a
             END = p.id
           )
           WHERE s.paper_id_a = ? OR s.paper_id_b = ?""",
        (paper_id, paper_id, paper_id)).fetchall()
    if synergies:
        related = ", ".join(
            f"#{s['paper_id_b'] if s['paper_id_a'] == paper_id else s['paper_id_a']}"
            for s in synergies)
    else:
        related = "暂无"

    # EAV 属性
    attrs = conn.execute(
        """SELECT * FROM paper_attributes WHERE paper_id=?
           ORDER BY category, attr_key""",
        (paper_id,)).fetchall()

    # 按 category 分组
    attr_groups = {}
    for a in attrs:
        cat = a["category"]
        if cat not in attr_groups:
            attr_groups[cat] = []
        unit = a["attr_unit"] or ""
        attr_groups[cat].append(
            f"{a['attr_key']}: {a['attr_value']}{unit}")

    report = f"""# PAPER-{paper_id:03d}: {v('title')[:60]}

> **入库日期**: {v('analysis_date')} | **分析者**: Claude | **DOI**: {v('doi')}
> **关联论文**: {related}

## 1. 论文元信息

| 字段 | 值 |
|------|-----|
| 标题 | {v('title')} |
| 作者 / 机构 / 国家 | {v('authors')} / {v('institution')} / {v('country')} |
| 期刊 / 年份 | {v('journal')} ({v('year')}) |
| 研究类型 | {v('research_type')} |
| 实验规模 | {v('experiment_scale')} |
| 可信度标记 | 实验数据: {v('has_experiment')} \\| 经济数据: {v('has_economic_data')} \\| 引用: {v('citation_quality')} |

### 研究背景

{v('problem_statement')}

**对标技术**: {v('benchmark_tech')}

---

## 2. 原料体系

**原料来源**: {v('raw_material_source')}

"""
    # 原料相关 EAV 属性
    raw_cats = ["raw_material_spec", "raw_material_pretreatment",
                "auxiliary_material", "raw_material_constraint"]
    for cat in raw_cats:
        if cat in attr_groups:
            report += f"**{cat}**:\n"
            for item in attr_groups[cat]:
                report += f"- {item}\n"
            report += "\n"

    report += f"""---

## 3. 工艺技术

### 技术路线
- **大类**: {v('tech_route_category')}
- **详细描述**: {v('tech_route_detail')}

### 产率链

| 步骤 | 名称 | 转化率 | 瓶颈? |
|------|------|--------|-------|
{steps_md}
| **总产率** | | **{v('total_yield')}%** | |

"""
    # 工艺参数 EAV
    if "process_params" in attr_groups:
        report += "### 核心工艺参数\n"
        for item in attr_groups["process_params"]:
            report += f"- {item}\n"
        report += "\n"

    # 设备 EAV
    if "equipment" in attr_groups:
        report += "### 设备体系\n"
        for item in attr_groups["equipment"]:
            report += f"- {item}\n"
        report += "\n"

    # 能耗
    energy_rows = conn.execute(
        "SELECT * FROM energy_breakdown WHERE paper_id=?",
        (paper_id,)).fetchall()
    if energy_rows:
        report += "### 能耗体系\n\n"
        report += "| 步骤 | 热耗(标煤吨/t) | 电耗(kWh/t) | 占比 |\n"
        report += "|------|---------------|------------|------|\n"
        for e in energy_rows:
            he = e['heat_energy']
            el = e['electricity']
            es = e['energy_share_pct']
            report += (f"| {e['step_name'] or '-'} | "
                       f"{he if he is not None else '-'} | "
                       f"{el if el is not None else '-'} | "
                       f"{es if es is not None else '-'}% |\n")
        report += "\n"

    # 环保
    env = conn.execute(
        "SELECT * FROM environmental WHERE paper_id=?",
        (paper_id,)).fetchone()
    if env:
        report += f"""### 环保与副产品

| 维度 | 详情 |
|------|------|
| 废气 | {env['waste_gas_type'] or '-'} |
| 废水 | {env['waste_water_type'] or '-'} |
| 废渣 | {env['solid_waste_type'] or '-'} |
| 副产品及价值 | {env['byproduct_name'] or '-'} ({env['byproduct_value'] if env['byproduct_value'] is not None else '-'} 元/吨) |
| 环保合规 | {env['meets_env_policy'] or '-'} |

"""

    report += f"""---

## 4. 产物分析

| 维度 | 详情 |
|------|------|
| 主产品 | {v('target_product_name')} |
| 产品类别 | {v('target_product_category')} |
| 纯度 | {v('target_product_purity')}% |
"""

    if "product_quality" in attr_groups:
        report += "\n### 质量指标\n"
        for item in attr_groups["product_quality"]:
            report += f"- {item}\n"

    if "product_market" in attr_groups:
        report += "\n### 市场定位\n"
        for item in attr_groups["product_market"]:
            report += f"- {item}\n"

    report += f"""
---

## 5. 工程放大评估

| 维度 | 详情 |
|------|------|
| TRL | {v('trl_level')} |
| 当前规模 | {v('trl_scale')} |
"""

    for cat in ["scaleup_risk", "scaleup_path", "scaleup_precedent"]:
        if cat in attr_groups:
            report += f"\n### {cat}\n"
            for item in attr_groups[cat]:
                report += f"- {item}\n"

    report += f"""
---

## 6. 技术经济分析

| 指标 | 数值 |
|------|------|
| 设备投资 | {v('capex_equipment')} 万元 |
| 万吨产能投资 | {v('capex_total_per_10kt')} 万元 |
| 原料成本 | {v('opex_raw_material_per_ton')} 元/吨 |
| 能耗成本 | {v('opex_energy_per_ton')} 元/吨 |
| 吨总成本 | {v('total_cost_per_ton')} 元 |
| 吨售价 | {v('product_price_per_ton')} 元 |
| 吨毛利 | {v('gross_profit_per_ton')} 元 |
| 毛利率 | {v('gross_margin')}% |
| 投资回收期 | {v('payback_period')} 年 |
"""

    for cat in ["sensitivity", "competition"]:
        if cat in attr_groups:
            report += f"\n### {cat}\n"
            for item in attr_groups[cat]:
                report += f"- {item}\n"

    report += f"""
---

## 7. 商业化综合评估

### 综合评分

| 维度 | 评分 (0-10) |
|------|------------|
| 技术可行性 | {v('tech_feasibility_score')} |
| 经济可行性 | {v('econ_feasibility_score')} |
| 市场吸引力 | {v('market_attractiveness_score')} |
| 放大可行性 | {v('scaleup_feasibility_score')} |
| **综合推荐** | **{v('composite_score')}** |
"""

    for cat in ["value_proposition", "barrier", "commercial_path",
                 "competitive_landscape"]:
        if cat in attr_groups:
            report += f"\n### {cat}\n"
            for item in attr_groups[cat]:
                report += f"- {item}\n"

    # 关联分析
    if synergies:
        report += "\n---\n\n## 8. 关联分析\n\n"
        for s in synergies:
            other_id = (s["paper_id_b"] if s["paper_id_a"] == paper_id
                        else s["paper_id_a"])
            other_t = s["other_title"] or ""
            desc = s["synergy_description"] or other_t[:40]
            report += (f"- **#{other_id}** [{s['synergy_type']}] "
                       f"强度:{s['synergy_strength']} | {desc}\n")

    report += f"""

---

*分析完成日期: {v('analysis_date')} | 分析者备注: {v('analyst_notes')}*
"""
    return report


def generate_single(conn, paper_id: int):
    """生成单篇报告并保存。"""
    report = build_report(conn, paper_id)
    if not report:
        print(f"[ERROR] 论文 #{paper_id} 不存在")
        return

    PAPERS_DIR.mkdir(parents=True, exist_ok=True)

    row = conn.execute(
        "SELECT title FROM papers WHERE id=?", (paper_id,)).fetchone()
    short_name = (row["title"] or "")[:30].replace("/", "-").replace(":", "-").strip()
    filename = f"PAPER-{paper_id:03d}-{short_name}.md"
    filepath = PAPERS_DIR / filename

    with open(filepath, "w", encoding="utf-8") as f:
        f.write(report)

    print(f"[OK] 报告已生成: {filepath}")


def generate_all(conn):
    """批量生成所有论文报告。"""
    rows = conn.execute("SELECT id FROM papers ORDER BY id").fetchall()
    if not rows:
        print("(论文库为空)")
        return
    for r in rows:
        generate_single(conn, r["id"])
    print(f"\n[OK] 共生成 {len(rows)} 篇报告")


def generate_synergy_report(conn):
    """生成全局关联网络报告。"""
    rows = conn.execute(
        """SELECT s.*, p1.title AS title_a, p2.title AS title_b
           FROM synergies s
           JOIN papers p1 ON s.paper_id_a = p1.id
           JOIN papers p2 ON s.paper_id_b = p2.id
           ORDER BY s.synergy_type, s.combined_potential_score DESC"""
    ).fetchall()

    if not rows:
        print("(暂无关联)")
        return

    PAPERS_DIR.mkdir(parents=True, exist_ok=True)
    filepath = PAPERS_DIR / "SYNERGY-NETWORK-REPORT.md"

    report = f"""# 论文关联网络报告

> 生成日期: {date.today()} | 总关联数: {len(rows)}

---

"""
    # 按关联类型分组
    groups = {}
    for r in rows:
        t = r["synergy_type"]
        if t not in groups:
            groups[t] = []
        groups[t].append(r)

    for stype, items in groups.items():
        report += f"## {stype} ({len(items)} 条)\n\n"
        for r in items:
            report += (f"- **#{r['paper_id_a']}** <-> **#{r['paper_id_b']}** "
                       f"强度:{r['synergy_strength']}\n")
            report += f"  - A: {(r['title_a'] or '')[:50]}\n"
            report += f"  - B: {(r['title_b'] or '')[:50]}\n"
            if r["synergy_description"]:
                report += f"  - 描述: {r['synergy_description']}\n"
            report += "\n"
        report += "\n"

    with open(filepath, "w", encoding="utf-8") as f:
        f.write(report)

    print(f"[OK] 关联网络报告已生成: {filepath} ({len(rows)} 条关联)")


def main():
    parser = argparse.ArgumentParser(
        description="滑石粉论文分析体系 — 报告生成器")
    parser.add_argument("--paper-id", type=int, help="生成单篇报告")
    parser.add_argument("--all", action="store_true", help="批量生成全量报告")
    parser.add_argument("--synergy-report", action="store_true",
                        help="生成全局关联网络报告")

    args = parser.parse_args()

    if not any(vars(args).values()):
        parser.print_help()
        sys.exit(0)

    conn = connect_db()

    if args.paper_id:
        generate_single(conn, args.paper_id)
    elif args.all:
        generate_all(conn)
    elif args.synergy_report:
        generate_synergy_report(conn)

    conn.close()


if __name__ == "__main__":
    main()
