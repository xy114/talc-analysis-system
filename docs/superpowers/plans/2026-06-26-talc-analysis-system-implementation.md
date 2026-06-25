# 滑石粉论文商业化分析体系 实现计划

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 搭建滑石粉/硫酸镁论文商业化分析的完整基础设施：数据库 + Python 工具链 + 分析模板 + Claude 工作流配置。

**Architecture:** Claude 驱动分析引擎 + 薄 Python 脚本层（ingest/query/report）+ SQLite 混合模式数据库（宽表+EAV）。分析归 Claude，确定性操作归脚本。

**Tech Stack:** Python 3.8+, SQLite3 (标准库), 无第三方依赖

## Global Constraints

- Python 3.8+，仅使用标准库 (`sqlite3`, `json`, `argparse`, `csv`, `os`, `sys`, `pathlib`)
- 数据库文件路径：`db/thesis.db`（项目根目录相对路径）
- 论文 Markdown 报告输出目录：`papers/`
- 脚本从项目根目录运行（`python scripts/ingest.py ...`）
- 所有 CLI 参数使用 `--kebab-case` 风格
- 论文 ID 从 1 开始自增
- JSON 输入文件编码 UTF-8

---

## 文件结构

```
d:\claude-me\thesis analysis\
├── .claude\
│   └── claude.md                    ← Task 6: 修改（当前为空文件）
├── db\
│   └── schema.sql                   ← Task 1: 新建
├── scripts\
│   ├── ingest.py                    ← Task 3: 新建
│   ├── query.py                     ← Task 4: 新建
│   └── report.py                    ← Task 5: 新建
└── templates\
    └── paper-analysis-template.md   ← Task 2: 新建
```

---

### Task 1: 数据库建表脚本

**Files:**
- Create: `db/schema.sql`

**Interfaces:**
- Produces: 6 张表 (`papers`, `process_steps`, `energy_breakdown`, `environmental`, `synergies`, `paper_attributes`) + 3 个索引
- 被所有 Python 脚本消费（通过 `sqlite3 thesis.db < db/schema.sql`）

- [ ] **Step 1: 编写 schema.sql**

```sql
-- 滑石粉/硫酸镁 论文商业化分析体系 · 数据库 Schema
-- 使用方法: sqlite3 db/thesis.db < db/schema.sql

PRAGMA foreign_keys = ON;

-- 1. 论文主表 (宽表，高频字段)
CREATE TABLE IF NOT EXISTS papers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    -- 元信息
    title TEXT NOT NULL,
    authors TEXT,
    institution TEXT,
    country TEXT,
    year INTEGER,
    journal TEXT,
    doi TEXT UNIQUE,
    research_type TEXT,          -- 综述/实验/模拟/中试/工业化
    problem_statement TEXT,
    raw_material_source TEXT,
    benchmark_tech TEXT,
    has_experiment INTEGER DEFAULT 0,   -- 0/1
    has_economic_data INTEGER DEFAULT 0,
    experiment_scale TEXT,       -- 实验室/小试/中试/工业化
    citation_quality TEXT,
    -- 技术路线
    tech_route_category TEXT,    -- A/B/C/D/E/F/G/H
    tech_route_detail TEXT,
    target_product_category TEXT,
    target_product_name TEXT,
    target_product_purity REAL,  -- %
    total_yield REAL,            -- %
    -- 成熟度
    trl_level INTEGER,           -- 1-9
    trl_scale TEXT,
    -- 经济数据
    capex_has_data TEXT,         -- 有/无/可推算
    capex_equipment REAL,        -- 万元
    capex_total_per_10kt REAL,   -- 万元/万吨产能
    opex_has_data TEXT,
    opex_raw_material_per_ton REAL,  -- 元/吨产品
    opex_energy_per_ton REAL,
    total_cost_per_ton REAL,
    product_price_per_ton REAL,
    gross_profit_per_ton REAL,
    gross_margin REAL,           -- %
    payback_period REAL,         -- 年
    -- 综合评分
    tech_feasibility_score INTEGER DEFAULT 0,     -- 0-10
    econ_feasibility_score INTEGER DEFAULT 0,
    market_attractiveness_score INTEGER DEFAULT 0,
    scaleup_feasibility_score INTEGER DEFAULT 0,
    composite_score REAL DEFAULT 0.0,
    -- 元数据
    analysis_date TEXT DEFAULT (date('now')),
    analyst_notes TEXT
);

-- 2. 工艺步骤 (产率链)
CREATE TABLE IF NOT EXISTS process_steps (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    paper_id INTEGER NOT NULL,
    step_order INTEGER NOT NULL,
    step_name TEXT NOT NULL,
    conversion_rate REAL,        -- %
    is_bottleneck INTEGER DEFAULT 0,
    notes TEXT,
    FOREIGN KEY (paper_id) REFERENCES papers(id) ON DELETE CASCADE
);

-- 3. 能耗分项
CREATE TABLE IF NOT EXISTS energy_breakdown (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    paper_id INTEGER NOT NULL,
    step_name TEXT,
    heat_energy REAL,            -- 标煤吨/吨产品
    electricity REAL,            -- kWh/吨产品
    energy_share_pct REAL,       -- %
    heat_recovery_potential TEXT,
    FOREIGN KEY (paper_id) REFERENCES papers(id) ON DELETE CASCADE
);

-- 4. 环保与副产品
CREATE TABLE IF NOT EXISTS environmental (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    paper_id INTEGER NOT NULL UNIQUE,
    waste_gas_type TEXT,
    waste_gas_amount TEXT,
    waste_gas_treatment TEXT,
    waste_gas_cost REAL,
    waste_water_type TEXT,
    waste_water_amount TEXT,
    waste_water_treatment TEXT,
    waste_water_cost REAL,
    solid_waste_type TEXT,
    solid_waste_amount TEXT,
    solid_waste_reusable INTEGER DEFAULT 0,
    byproduct_name TEXT,
    byproduct_value REAL,
    byproduct_revenue_share REAL,
    meets_env_policy TEXT,
    FOREIGN KEY (paper_id) REFERENCES papers(id) ON DELETE CASCADE
);

-- 5. 论文关联网络
CREATE TABLE IF NOT EXISTS synergies (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    paper_id_a INTEGER NOT NULL,
    paper_id_b INTEGER NOT NULL,
    synergy_type TEXT NOT NULL,  -- 对标竞争/副产品利用/工艺互补/条件优化借鉴/上下游衔接/设备共用/联合生产
    synergy_strength TEXT,       -- 强/中/弱
    synergy_description TEXT,
    combined_potential_score REAL,
    created_date TEXT DEFAULT (date('now')),
    FOREIGN KEY (paper_id_a) REFERENCES papers(id) ON DELETE CASCADE,
    FOREIGN KEY (paper_id_b) REFERENCES papers(id) ON DELETE CASCADE,
    CHECK (paper_id_a != paper_id_b)
);

-- 6. EAV 扩展属性表
CREATE TABLE IF NOT EXISTS paper_attributes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    paper_id INTEGER NOT NULL,
    category TEXT NOT NULL,      -- raw_material_spec / process_params / product_quality / ...
    attr_key TEXT NOT NULL,
    attr_value TEXT,
    attr_unit TEXT,
    source_context TEXT,
    FOREIGN KEY (paper_id) REFERENCES papers(id) ON DELETE CASCADE
);

-- 索引
CREATE INDEX IF NOT EXISTS idx_papers_year ON papers(year);
CREATE INDEX IF NOT EXISTS idx_papers_route ON papers(tech_route_category);
CREATE INDEX IF NOT EXISTS idx_papers_product ON papers(target_product_category);
CREATE INDEX IF NOT EXISTS idx_papers_composite ON papers(composite_score DESC);
CREATE INDEX IF NOT EXISTS idx_process_steps_paper ON process_steps(paper_id);
CREATE INDEX IF NOT EXISTS idx_energy_paper ON energy_breakdown(paper_id);
CREATE INDEX IF NOT EXISTS idx_attributes_paper ON paper_attributes(paper_id);
CREATE INDEX IF NOT EXISTS idx_attributes_category ON paper_attributes(paper_id, category);
CREATE INDEX IF NOT EXISTS idx_synergies_a ON synergies(paper_id_a);
CREATE INDEX IF NOT EXISTS idx_synergies_b ON synergies(paper_id_b);
```

- [ ] **Step 2: 验证建表**

```bash
cd "d:\claude-me\thesis analysis"
mkdir -p db
sqlite3 db/thesis.db < db/schema.sql
sqlite3 db/thesis.db ".tables"
```

Expected output:
```
energy_breakdown   environmental   paper_attributes   papers
process_steps      synergies
```

- [ ] **Step 3: Commit**

```bash
git add db/schema.sql
git commit -m "feat: add database schema for thesis analysis system"
```

---

### Task 2: 标准化分析模板

**Files:**
- Create: `templates/paper-analysis-template.md`

**Interfaces:**
- Produces: Markdown 模板，被 Claude 在入库 Step 4 中使用，被 `report.py` 读取渲染

- [ ] **Step 1: 编写模板**

创建 `templates/paper-analysis-template.md`：

```markdown
# PAPER-{{id}}: {{title_cn}}

> **入库日期**: {{analysis_date}} | **分析者**: Claude | **DOI**: {{doi}}
> **关联论文**: {{related_papers}}

## 1. 论文元信息

| 字段 | 值 |
|------|-----|
| 标题 (EN) | {{title_en}} |
| 作者 / 机构 / 国家 | {{authors}} / {{institution}} / {{country}} |
| 期刊 / 年份 | {{journal}} ({{year}}) |
| 研究类型 | {{research_type}} |
| 实验规模 | {{experiment_scale}} |
| 可信度标记 | 实验数据: {{has_experiment}} \| 经济数据: {{has_economic_data}} \| 引用: {{citation_quality}} |

### 研究背景

{{problem_statement}}

**对标技术**: {{benchmark_tech}}

---

## 2. 原料体系

| 维度 | 详情 |
|------|------|
| 滑石粉来源 / 品位 | {{raw_material_source}} |
| 关键杂质限制 | {{impurity_limits}} |
| 粒度要求 | {{particle_size}} |
| 预处理方式 | {{pretreatment}} |
| 辅助试剂及用量 | {{auxiliary_materials}} |
| 试剂成本估算 | {{reagent_cost}} |

### 原料约束

{{raw_material_constraints}}

---

## 3. 工艺技术

### 技术路线

- **大类**: {{tech_route_category}}
- **详细描述**: {{tech_route_detail}}

### 核心工艺参数

| 参数 | 最优值 | 范围 |
|------|--------|------|
{{process_params_table}}

### 产率链

| 步骤 | 名称 | 转化率 | 瓶颈? |
|------|------|--------|-------|
{{process_steps_table}}
| **总产率** | | **{{total_yield}}%** | |

**产率瓶颈**: {{yield_bottleneck}}

### 设备体系

| 维度 | 详情 |
|------|------|
| 核心反应器 | {{core_reactor}} |
| 材质要求 | {{material_req}} |
| 分离设备 | {{separation_equip}} |
| 干燥设备 | {{drying_equip}} |
| 设备国产化 | {{equip_localization}} |
| 设备投资估算 | {{equip_investment}} |

### 能耗体系

| 步骤 | 热耗 (标煤吨/吨) | 电耗 (kWh/吨) | 占比 |
|------|------------------|---------------|------|
{{energy_table}}

**余热回收潜力**: {{heat_recovery}}

### 环保与副产品

| 维度 | 详情 |
|------|------|
| 废气 | {{waste_gas}} |
| 废水 | {{waste_water}} |
| 废渣 | {{solid_waste}} |
| 副产品及价值 | {{byproducts}} |
| 环保合规 | {{env_compliance}} |

---

## 4. 产物分析

| 维度 | 详情 |
|------|------|
| 主产品 | {{product_name}} |
| 产品类别 | {{product_category}} |
| 纯度 | {{product_purity}}% |
| 形态 | {{product_form}} |
| 达标情况 | {{product_standards}} |

### 市场定位

| 维度 | 详情 |
|------|------|
| 应用场景 | {{market_applications}} |
| 该纯度市场价 | {{product_price}} 元/吨 |
| 高纯溢价空间 | {{premium_potential}} |
| 市场规模与增长 | {{market_size}} |

### 副产品价值

{{byproduct_value_detail}}

---

## 5. 工程放大评估

| 维度 | 详情 |
|------|------|
| TRL | {{trl_level}} |
| 当前规模 | {{trl_scale}} |
| 目标工业规模 | {{target_scale}} |

### 放大风险

{{scaleup_risks}}

### 同类工业化先例

{{industrial_precedents}}

---

## 6. 技术经济分析

### 投资估算 (CAPEX)

| 项目 | 金额 (万元) | 数据来源 |
|------|------------|---------|
| 设备投资 | {{capex_equipment}} | {{capex_source}} |
| 单位产能投资 | {{capex_per_10kt}} 万元/万吨 | |

### 运营成本 (OPEX)

| 成本项 | 元/吨产品 | 占比 |
|--------|----------|------|
| 原料 | {{opex_raw}} | {{opex_raw_pct}}% |
| 能耗 | {{opex_energy}} | {{opex_energy_pct}}% |
| 人工 | {{opex_labor}} | {{opex_labor_pct}}% |
| 折旧 | {{opex_depreciation}} | {{opex_depreciation_pct}}% |
| 环保 | {{opex_env}} | {{opex_env_pct}}% |
| **总成本** | **{{total_cost}}** | 100% |

### 盈利分析

| 指标 | 数值 |
|------|------|
| 吨产品总成本 | {{total_cost}} 元 |
| 吨产品售价 | {{product_price}} 元 |
| 吨毛利 | {{gross_profit}} 元 |
| 毛利率 | {{gross_margin}}% |
| 投资回收期 | {{payback_period}} 年 |

### 敏感性分析

| 变动因素 | 对利润影响 |
|----------|-----------|
| 原料价格 +10% | {{sensitivity_raw}} |
| 产品价格 -10% | {{sensitivity_price}} |
| 能耗价格 +10% | {{sensitivity_energy}} |

### 与现有工艺对比

{{competition_comparison}}

---

## 7. 商业化综合评估

### 综合评分

| 维度 | 评分 (0-10) | 依据 |
|------|------------|------|
| 技术可行性 | {{score_tech}} | {{score_tech_reason}} |
| 经济可行性 | {{score_econ}} | {{score_econ_reason}} |
| 市场吸引力 | {{score_market}} | {{score_market_reason}} |
| 放大可行性 | {{score_scaleup}} | {{score_scaleup_reason}} |
| **综合推荐** | **{{composite_score}}** | |

### 价值主张

{{value_proposition}}

### 商业化障碍

{{commercial_barriers}}

### 建议路径

{{commercial_path}}

### 竞争格局

{{competitive_landscape}}

---

## 8. 关联分析

### 与本库中其他论文的关联

{{synergy_analysis}}

---

*分析完成日期: {{analysis_date}} | 下次更新: {{next_review_date}}*
```

- [ ] **Step 2: Commit**

```bash
git add templates/paper-analysis-template.md
git commit -m "feat: add paper analysis markdown template"
```

---

### Task 3: 入库引擎脚本

**Files:**
- Create: `scripts/ingest.py`

**Interfaces:**
- Consumes: `db/schema.sql`（数据库已初始化）
- Consumes: JSON 文件（由 Claude 生成的结构化论文数据）
- Produces: SQLite 行数据 + 终端入库报告
- CLI: `python scripts/ingest.py --json <path> [--force] [--dry-run]`

- [ ] **Step 1: 编写 ingest.py**

```python
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


def validate_json(data: dict) -> list[str]:
    """校验 JSON 结构完整性，返回错误列表。"""
    errors = []
    paper = data.get("paper", {})
    for field in REQUIRED_PAPER_FIELDS:
        if not paper.get(field):
            errors.append(f"缺少必填字段: paper.{field}")
    if not paper.get("doi"):
        errors.append("警告: paper.doi 为空，将无法自动去重")
    return errors


def check_doi_exists(conn, doi: str) -> int | None:
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

    # environmental
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


def auto_detect_synergies(conn, paper_id: int, paper: dict) -> list[dict]:
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
                # 获取关联论文标题
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
```

- [ ] **Step 2: 创建测试 JSON 并验证 dry-run**

```bash
cd "d:\claude-me\thesis analysis"

# 创建测试 JSON
cat > test_paper.json << 'EOF'
{
  "paper": {
    "title": "测试论文: 滑石粉酸浸制备硫酸镁研究",
    "doi": "10.0000/test.001",
    "tech_route_category": "C",
    "target_product_category": "硫酸镁",
    "target_product_name": "七水硫酸镁",
    "composite_score": 7.5
  },
  "process_steps": [
    {"step_order": 1, "step_name": "酸浸", "conversion_rate": 95.0},
    {"step_order": 2, "step_name": "结晶", "conversion_rate": 90.0}
  ],
  "energy": [
    {"step_name": "酸浸", "heat_energy": 0.5, "electricity": 120}
  ],
  "environmental": {
    "waste_gas_type": "无",
    "byproduct_name": "白炭黑"
  },
  "attributes": [
    {"category": "process_params", "attr_key": "temperature", "attr_value": "90", "attr_unit": "°C"}
  ],
  "synergies": []
}
EOF

python scripts/ingest.py --json test_paper.json --dry-run
```

Expected output:
```
[DRY-RUN] JSON 结构校验通过，未写入数据库。
```

- [ ] **Step 3: 真实入库测试**

```bash
# 确保数据库已初始化
sqlite3 db/thesis.db < db/schema.sql

# 入库
python scripts/ingest.py --json test_paper.json
```

Expected output:
```
[OK] 论文入库: paper_id=1 标题: 测试论文: 滑石粉酸浸制备硫酸镁研究

[SYNERGY] 未检测到关联（或论文库为空）
```

- [ ] **Step 4: 验证数据已写入**

```bash
sqlite3 db/thesis.db "SELECT id, title, tech_route_category FROM papers;"
sqlite3 db/thesis.db "SELECT * FROM process_steps WHERE paper_id=1;"
```

Expected:
```
1|测试论文: 滑石粉酸浸制备硫酸镁研究|C
1|1|1|酸浸|95.0|0|
2|1|2|结晶|90.0|0|
```

- [ ] **Step 5: 测试去重**

```bash
python scripts/ingest.py --json test_paper.json
```

Expected output:
```
[SKIP] DOI 已存在: paper_id=1
       使用 --force 覆盖更新
```

- [ ] **Step 6: 清理测试数据并 Commit**

```bash
rm test_paper.json
sqlite3 db/thesis.db "DELETE FROM papers WHERE doi='10.0000/test.001';"
git add scripts/ingest.py
git commit -m "feat: add paper ingest engine with auto synergy detection"
```

---

### Task 4: 查询引擎脚本

**Files:**
- Create: `scripts/query.py`

**Interfaces:**
- Consumes: `db/thesis.db`（由 ingest.py 写入的数据）
- Produces: 终端表格输出 / CSV 文件
- CLI: 多个查询子命令

- [ ] **Step 1: 编写 query.py**

```python
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
        val = row.get(name, "") if isinstance(row, dict) else (
            row[name] if name in row.keys() else "")
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
            bn = " ⚠瓶颈" if s["is_bottleneck"] else ""
            print(f"  步骤{s['step_order']}: {s['step_name']} "
                  f"→ {s['conversion_rate']}%{bn}")
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


def compare_papers(conn, ids: list[int]):
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

    fields = [
        ("id", "ID", 4), ("target_product_name", "产品", 14),
        ("tech_route_category", "路线", 4), ("target_product_purity", "纯度%", 7),
        ("total_yield", "产率%", 7), ("trl_level", "TRL", 4),
        ("total_cost_per_ton", "成本元/t", 10), ("product_price_per_ton", "售价元/t", 10),
        ("gross_margin", "毛利率%", 8), ("payback_period", "回收期年", 8),
        ("composite_score", "评分", 5)
    ]

    print(f"\n{'='*80}")
    print(f"  论文横向对比 ({len(rows)} 篇)")
    print(f"{'='*80}\n")

    header = " | ".join(label.ljust(w) for _, label, w in fields)
    print(header)
    print("-" * len(header))
    for row in rows:
        parts = []
        for key, _, width in fields:
            val = row.get(key, "-") if isinstance(row, dict) else (
                row[key] if key in row.keys() else "-")
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
             CASE WHEN s.paper_id_a = ? THEN s.paper_id_b ELSE s.paper_id_a END = p.id
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
        other_id = r["paper_id_b"] if r["paper_id_a"] == paper_id else r["paper_id_a"]
        print(f"  → #{other_id} [{r['synergy_type']}] "
              f"强度:{r['synergy_strength']} | {r['other_title'][:40]}")


def show_unlinked(conn):
    """找出没有任何关联的孤立的论文。"""
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
    print(f"\n🏆 综合评分 Top {n}:")
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
    parser.add_argument("--list-all", action="store_true", help="列出所有论文摘要")
    parser.add_argument("--paper-id", type=int, help="查看单论文详情")
    parser.add_argument("--product", type=str, help="按产品名称筛选")
    parser.add_argument("--route", type=str, help="按技术路线筛选 (A-H)")
    parser.add_argument("--min-margin", type=float, help="最低毛利率筛选")
    parser.add_argument("--compare", type=str, help="多论文对比，逗号分隔ID")
    parser.add_argument("--synergies-for", type=int, help="查看某论文关联")
    parser.add_argument("--unlinked", action="store_true", help="孤立论文")
    parser.add_argument("--top", type=int, help="Top N")
    parser.add_argument("--export", action="store_true", help="导出 CSV")
    parser.add_argument("--format", type=str, choices=["csv"], help="导出格式")

    args = parser.parse_args()

    if not any(vars(args).values()):
        parser.print_help()
        sys.exit(0)

    conn = connect_db()

    if args.list_all:
        list_all(conn)
    elif args.paper_id:
        show_detail(conn, args.paper_id)
    elif args.product:
        filter_by_product(conn, args.product)
    elif args.route:
        filter_by_route(conn, args.route)
    elif args.min_margin is not None:
        filter_by_margin(conn, args.min_margin)
    elif args.compare:
        ids = [int(x.strip()) for x in args.compare.split(",") if x.strip()]
        compare_papers(conn, ids)
    elif args.synergies_for:
        show_synergies(conn, args.synergies_for)
    elif args.unlinked:
        show_unlinked(conn)
    elif args.top:
        show_top(conn, args.top)
    elif args.export:
        export_csv(conn)

    conn.close()


if __name__ == "__main__":
    main()
```

- [ ] **Step 2: 验证查询命令**

```bash
# 先用测试数据入库
cat > test_paper2.json << 'EOF'
{
  "paper": {
    "title": "测试2: 滑石粉煅烧制备氧化镁",
    "doi": "10.0000/test.002",
    "tech_route_category": "B",
    "target_product_category": "氧化镁",
    "target_product_name": "轻质氧化镁",
    "target_product_purity": 98.5,
    "total_yield": 85.0,
    "trl_level": 5,
    "total_cost_per_ton": 8000,
    "product_price_per_ton": 15000,
    "gross_margin": 46.7,
    "composite_score": 8.0
  },
  "process_steps": [{"step_order": 1, "step_name": "煅烧", "conversion_rate": 85.0}],
  "energy": [],
  "environmental": {},
  "attributes": [],
  "synergies": []
}
EOF

python scripts/ingest.py --json test_paper2.json
python scripts/query.py --list-all
python scripts/query.py --paper-id 2
python scripts/query.py --top 5
python scripts/query.py --compare 1,2
python scripts/query.py --unlinked
```

Expected: 各项命令正常输出表格数据。

- [ ] **Step 3: 清理测试数据并 Commit**

```bash
rm test_paper2.json
sqlite3 db/thesis.db "DELETE FROM papers WHERE doi LIKE '10.0000/test.%';"
git add scripts/query.py
git commit -m "feat: add query engine with filtering, comparison, and export"
```

---

### Task 5: 报告生成器脚本

**Files:**
- Create: `scripts/report.py`

**Interfaces:**
- Consumes: `db/thesis.db` + `templates/paper-analysis-template.md`
- Produces: `papers/PAPER-XXX-[简称].md` Markdown 报告文件
- CLI: `python scripts/report.py --paper-id N [--all] [--synergy-report]`

- [ ] **Step 1: 编写 report.py**

```python
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
import os
from datetime import date
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent.parent / "db" / "thesis.db"
PAPERS_DIR = Path(__file__).resolve().parent.parent / "papers"


def connect_db():
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    return conn


def build_report(conn, paper_id: int) -> str | None:
    """生成单篇论文的 Markdown 报告。"""
    row = conn.execute("SELECT * FROM papers WHERE id = ?", (paper_id,)).fetchone()
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
        bn = " ⚠瓶颈" if s["is_bottleneck"] else ""
        steps_md += f"| {s['step_order']} | {s['step_name']} | {s['conversion_rate']}% |{bn} |\n"

    # 关联论文
    synergies = conn.execute(
        """SELECT s.*, p.title AS other_title
           FROM synergies s
           JOIN papers p ON (
             CASE WHEN s.paper_id_a = ? THEN s.paper_id_b ELSE s.paper_id_a END = p.id
           )
           WHERE s.paper_id_a = ? OR s.paper_id_b = ?""",
        (paper_id, paper_id, paper_id)).fetchall()
    related = ", ".join(
        f"#{s['paper_id_b'] if s['paper_id_a'] == paper_id else s['paper_id_a']}"
        for s in synergies
    ) if synergies else "暂无"

    # EAV 属性
    attrs = conn.execute(
        "SELECT * FROM paper_attributes WHERE paper_id=? ORDER BY category, attr_key",
        (paper_id,)).fetchall()

    # 按 category 分组
    attr_groups = {}
    for a in attrs:
        cat = a["category"]
        if cat not in attr_groups:
            attr_groups[cat] = []
        attr_groups[cat].append(f"{a['attr_key']}: {a['attr_value']}{a['attr_unit'] or ''}")

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
    for cat in ["raw_material_spec", "raw_material_pretreatment",
                 "auxiliary_material", "raw_material_constraint"]:
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
            report += (f"| {e['step_name']} | {e['heat_energy'] or '-'} | "
                       f"{e['electricity'] or '-'} | {e['energy_share_pct'] or '-'}% |\n")
        report += "\n"

    # 环保
    env = conn.execute(
        "SELECT * FROM environmental WHERE paper_id=?", (paper_id,)).fetchone()
    if env:
        report += f"""### 环保与副产品

| 维度 | 详情 |
|------|------|
| 废气 | {env['waste_gas_type'] or '-'} |
| 废水 | {env['waste_water_type'] or '-'} |
| 废渣 | {env['solid_waste_type'] or '-'} |
| 副产品及价值 | {env['byproduct_name'] or '-'} ({env['byproduct_value'] or '-'} 元/吨) |
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
            other_id = s["paper_id_b"] if s["paper_id_a"] == paper_id else s["paper_id_a"]
            report += (f"- **#{other_id}** [{s['synergy_type']}] "
                       f"强度:{s['synergy_strength']} | {s['synergy_description'] or s['other_title'][:40]}\n")

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

    # 获取论文简称
    row = conn.execute("SELECT title FROM papers WHERE id=?", (paper_id,)).fetchone()
    short_name = row["title"][:30].replace("/", "-").replace(":", "-").strip()
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
            report += (f"- **#{r['paper_id_a']}** ↔ **#{r['paper_id_b']}** "
                       f"强度:{r['synergy_strength']}\n")
            report += f"  - A: {r['title_a'][:50]}\n"
            report += f"  - B: {r['title_b'][:50]}\n"
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
```

- [ ] **Step 2: 验证报告生成**

```bash
# 确保已有一条测试数据入库 (Task 3 的残留或重新入库)
python scripts/report.py --paper-id 1
ls papers/
cat "papers/PAPER-001-"*.md | head -30
python scripts/report.py --synergy-report
```

Expected: papers/ 目录下生成 Markdown 文件，内容包含论文完整分析。

- [ ] **Step 3: Commit**

```bash
git add scripts/report.py
git commit -m "feat: add report generator for papers and synergy networks"
```

---

### Task 6: Claude 工作流配置

**Files:**
- Modify: `.claude/claude.md`

**Interfaces:**
- 被 Claude 在每次会话启动时自动加载
- 定义触发规则、7 步入库流程、Skills 使用规则

- [ ] **Step 1: 编写 claude.md**

将 `.claude/claude.md` 的内容替换为：

```markdown
# 滑石粉/硫酸镁 论文商业化分析 · Claude 工作流配置

> 本项目为企业寻找滑石粉（硅酸镁，MgSiO₃）的大规模商业化路径。
> 参考文件: `体系基础架构.md`（完整分析维度树 + 数据库设计）
> 设计规范: `docs/superpowers/specs/2026-06-26-talc-analysis-system-design.md`

---

## 触发规则

| 用户表述 | 执行动作 |
|---------|---------|
| "入库新论文" / "分析这篇论文" / "分析新论文" | 执行 7 步标准入库流程 |
| "分析商业路径" / "有什么机会" / "推荐方向" / "商业化建议" | 商业路径综合推荐流程 |
| "搜索论文" / "找论文" / "补充论文" | 论文搜索流程 |
| 拖入/粘贴论文文件 (Word/PDF) | 自动识别 → 询问是否入库 |

---

## 标准入库流程 (7 步)

> 当用户触发论文入库时，严格按以下流程执行：

### Step 1: 读取论文
- Word 文档 → `Read` 工具直接读取
- PDF 文件 → `Read` 工具读取
- DOI/URL → `WebFetch` 抓取摘要 + 尝试获取全文
- 用户粘贴 → 直接使用粘贴内容
- 如信息不足 → 告知用户缺失内容，请求补充

### Step 2: 按维度提取信息
严格按照 `体系基础架构.md` 树状图的 8 大分支逐项提取：
1. 论文元信息
2. 原料体系
3. 工艺技术体系
4. 产物体系
5. 工程放大评估
6. 技术经济分析
7. 商业化综合评估
8. 论文间关联（Step 5 执行）

**重要原则：**
- 论文中明确提供的信息 → 直接提取
- 论文中未提供的信息 → 标注"论文未提供"，不做无依据推测
- 可从论文数据推算的信息 → 标注"推算"，并给出推算逻辑
- 评分维度 (0-10) 基于论文数据和行业常识综合判断

### Step 3: 生成结构化 JSON
将提取的信息按 `scripts/ingest.py` 的输入格式组装为 JSON。
- 必填字段不可为空
- 与论文无关的字段省略
- JSON 保存到项目根目录，命名 `paper-data-XXX.json`

### Step 4: 生成 Markdown 分析报告
按 `templates/paper-analysis-template.md` 模板生成报告。
- 保存到 `papers/PAPER-XXX-[论文英文简称].md`
- 编号按入库顺序，从 001 起。如库中已有 N 篇，新论文编号自动为 N+1
- 报告中的 {{变量}} 需全部替换为实际数据
- 缺失数据标注"论文未提供"

### Step 5: 自动比对已有论文库
- 读取 `db/thesis.db` 中已有论文（如库存在）
- 按 7 条关联检测规则逐条匹配（对标竞争/副产品利用/工艺互补/上下游衔接/设备共用/联合生产/条件优化借鉴）
- 识别潜在关联
- 将检测到的关联写入 JSON 的 `synergies` 字段

### Step 6: 输出关联报告
- 如发现关联 → 描述每条关联的类型、强度、组合后的商业潜力
- 如未发现关联 → 记录"暂无关联，待论文库扩充后重新检测"
- 特别关注："这篇新论文 + 某篇已有论文 = 一条可能的工业路径" 的模式

### Step 7: 交付物
向用户呈现：
1. **Markdown 分析报告**（可直接查看的核心交付物）
2. **待入库 JSON 文件路径**
3. **关联检测结果**（如有）
4. **入库命令**: `python scripts/ingest.py --json paper-data-XXX.json`

---

## 商业路径综合推荐流程

> 当用户要求分析商业路径时：

1. 先运行查询获取论文库全景:
   - `python scripts/query.py --top 15` — 高分论文
   - `python scripts/query.py --export --format csv` — 全量数据
   - `python scripts/report.py --synergy-report` — 关联网络

2. 分析维度:
   - 哪些产品方向有最多的论文支撑？
   - 哪些技术路线的经济性最好？
   - 哪些论文关联形成了完整的"原料→中间体→产品"链条？
   - 哪些高价值产品还没有论文覆盖（空白机会）？

3. 输出:
   - 2-3 条可行的商业路径，每条包含:
     - 产品选择 + 目标市场规模
     - 推荐工艺路线 + 依据的论文
     - 经济性预估 (吨成本/售价/毛利率/回收期)
     - 关键风险与不确定性
     - 下一步验证建议（需要补充什么实验/数据）

---

## 论文搜索流程

> 当用户要求搜索新论文时：

1. 使用 `WebSearch` 搜索，关键词覆盖：
   - 中文: 滑石粉 硅酸镁 酸浸 煅烧 碳化 硫酸镁 氧化镁 碳酸镁 氢氧化镁 技术经济
   - 英文: talc "magnesium silicate" "acid leaching" calcination carbonation "magnesium sulfate" "magnesium oxide" "techno-economic"

2. 筛选标准:
   - ✅ SCI/EI 期刊论文
   - ✅ 有实验数据
   - ✅ 近 15 年 (2010+) 为主
   - ❌ 排除专利文献
   - ❌ 排除纯综述（无新实验数据）
   - 优先: 有经济性数据、TRL 较高、高价值产品

3. 返回格式:
   - 论文标题 | 期刊/年份 | 研究类型 | 技术路线 | 目标产品 | 是否有经济数据
   - 供用户选择哪些需要入库分析

---

## Skills 使用规则

| 场景 | 调用 Skill |
|------|-----------|
| 入库前讨论论文的商业启发 | `brainstorming` |
| 需要对多篇论文做综述梳理 | `ars-lit-review` |
| 需要深度调研某个技术方向 | `deep-research` |
| 复杂跨论文关联分析 (≥5篇) | `synthesis_agent` (Agent) |
| 论文分析体系的设计讨论 | `brainstorming` |

---

## 数据库与脚本位置

| 资源 | 路径 |
|------|------|
| 分析维度树 & DB 设计 | `体系基础架构.md` |
| SQLite 数据库 | `db/thesis.db` |
| 建表 SQL | `db/schema.sql` |
| 入库引擎 | `scripts/ingest.py` |
| 查询引擎 | `scripts/query.py` |
| 报告生成器 | `scripts/report.py` |
| 分析模板 | `templates/paper-analysis-template.md` |
| 论文报告 | `papers/PAPER-XXX-*.md` |
| 论文源文件 | `sources/` |
| 设计规范 | `docs/superpowers/specs/2026-06-26-talc-analysis-system-design.md` |
```

- [ ] **Step 2: 验证配置已生效**

在项目目录下启动新会话，Claude 应自动加载此配置。

- [ ] **Step 3: Commit**

```bash
git add .claude/claude.md
git commit -m "feat: configure Claude workflow for talc paper analysis system"
```

---

## 完成检查清单

- [ ] `db/schema.sql` 可执行建表
- [ ] `scripts/ingest.py` 可正常入库 + 去重 + 关联检测
- [ ] `scripts/query.py` 所有查询参数正常
- [ ] `scripts/report.py` 可生成 Markdown 报告
- [ ] `templates/paper-analysis-template.md` 模板完整
- [ ] `.claude/claude.md` 配置已生效
- [ ] 至少一篇测试论文走通完整入库→查询→报告流程
