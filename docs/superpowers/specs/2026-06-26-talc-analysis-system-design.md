# 滑石粉/硫酸镁 论文商业化分析体系 — 系统设计规范

> **版本**: v1.0 | **日期**: 2026-06-26 | **状态**: 待审核

---

## 1. 项目目标

为企业寻找滑石粉（硅酸镁，MgSiO₃）的大规模商业化路径。当前滑石粉用途限于添加剂，消耗远低于产出。通过系统性分析学术论文，评估从滑石粉制备各类高价值镁化合物（硫酸镁、氧化镁、碳酸镁、氢氧化镁等）的技术经济可行性，发现可行的工业转化路径。

**核心交付：**
- 每篇论文的 8 维度结构化分析 + Markdown 报告
- 论文间关联网络，发现跨论文的商业路径组合
- 可查询、可积累的 SQLite 知识库

---

## 2. 系统架构

### 2.1 架构方案：Claude 驱动 + 薄脚本层

```
┌──────────────────────────────────────────────┐
│                   用户                        │
│       提供论文 / 触发入库 / 发起查询            │
└──────────────┬───────────────────────────────┘
               │
               ▼
┌──────────────────────────────────────────────┐
│              Claude (核心分析引擎)              │
│  · 阅读论文 → 提取 8 维度信息                   │
│  · 商业化判断 + 评分                           │
│  · 关联发现与推理                              │
│  · 输出: JSON 数据 + Markdown 报告              │
└──────────────┬───────────────────────────────┘
               │ JSON
               ▼
┌──────────────────────────────────────────────┐
│          scripts/ingest.py (入库引擎)          │
│  · JSON 校验 → 写入 SQLite                     │
│  · 自动关联检测 (规则引擎)                      │
│  · 输出入库报告                                │
└──────────────┬───────────────────────────────┘
               │
               ▼
┌──────────────────────────────────────────────┐
│           SQLite thesis.db                    │
│  papers + process_steps + energy +            │
│  environmental + synergies + attributes       │
└──────────────┬───────────────────────────────┘
               │
               ▼
┌──────────────────────────────────────────────┐
│          scripts/query.py (查询引擎)           │
│  · 按产品/路线/利润率等筛选                     │
│  · 多论文横向对比                              │
│  · 关联网络查询                                │
│  · CSV 导出                                   │
└──────────────────────────────────────────────┘
```

### 2.2 设计原则

- **分析归 Claude，操作归脚本**：推理判断由 Claude 完成，确定性数据操作由 Python 脚本执行
- **宽表 + EAV 混合**：高频字段宽表（查询效率），低频字段 EAV（灵活扩展）
- **一次分析，双重交付**：每篇论文同时产出结构化 JSON（可入库）和 Markdown 报告（可阅读）
- **渐进积累**：每入库一篇即与已有论文比对，关联网络持续生长

---

## 3. 数据库设计

### 3.1 表结构概览

```
papers (1) ────── 1:N ────── process_steps
    │                         energy_breakdown
    │                         environmental
    │                         paper_attributes (EAV)
    │
    └── N:N ── synergies (paper_id_a ↔ paper_id_b)
```

### 3.2 `papers` 主表（宽表，约 40 字段）

| 字段分组 | 字段 | 类型 | 说明 |
|----------|------|------|------|
| **元信息** | title | TEXT | 论文标题 |
| | authors | TEXT | 作者 (分号分隔) |
| | institution | TEXT | 第一机构 |
| | country | TEXT | 国家 |
| | year | INTEGER | 发表年份 |
| | journal | TEXT | 期刊 |
| | doi | TEXT UNIQUE | DOI |
| | research_type | TEXT | 综述/实验/模拟/中试/工业化 |
| | problem_statement | TEXT | 研究问题 |
| | raw_material_source | TEXT | 滑石矿来源 |
| | benchmark_tech | TEXT | 对标现有技术 |
| | has_experiment | INTEGER | 0/1 |
| | has_economic_data | INTEGER | 0/1 |
| | experiment_scale | TEXT | 实验室/小试/中试/工业化 |
| | citation_quality | TEXT | 引用评价 |
| **技术路线** | tech_route_category | TEXT | A-H 八大类 |
| | tech_route_detail | TEXT | 详细描述 |
| | target_product_category | TEXT | 产品类别 |
| | target_product_name | TEXT | 产品名称 |
| | target_product_purity | REAL | 纯度 % |
| | total_yield | REAL | 总产率 % |
| **成熟度** | trl_level | INTEGER | 1-9 |
| | trl_scale | TEXT | 当前规模 |
| **经济** | capex_has_data | TEXT | 有/无/可推算 |
| | capex_equipment | REAL | 设备投资(万元) |
| | capex_total_per_10kt | REAL | 万吨产能投资(万元) |
| | opex_has_data | TEXT | 有/无/可推算 |
| | opex_raw_material_per_ton | REAL | 原料成本(元/吨) |
| | opex_energy_per_ton | REAL | 能耗成本(元/吨) |
| | total_cost_per_ton | REAL | 吨总成本 |
| | product_price_per_ton | REAL | 吨售价 |
| | gross_profit_per_ton | REAL | 吨毛利 |
| | gross_margin | REAL | 毛利率 % |
| | payback_period | REAL | 回收期(年) |
| **评分** | tech_feasibility_score | INTEGER | 0-10 |
| | econ_feasibility_score | INTEGER | 0-10 |
| | market_attractiveness_score | INTEGER | 0-10 |
| | scaleup_feasibility_score | INTEGER | 0-10 |
| | composite_score | REAL | 加权总分 |
| | analysis_date | TEXT | 分析日期 |
| | analyst_notes | TEXT | 备注 |

### 3.3 子表

#### `process_steps` — 产率链

| 字段 | 类型 | 说明 |
|------|------|------|
| id | INTEGER PK | |
| paper_id | INTEGER FK | |
| step_order | INTEGER | 步骤序号 |
| step_name | TEXT | |
| conversion_rate | REAL | 转化率 % |
| is_bottleneck | INTEGER | 0/1 |
| notes | TEXT | |

#### `energy_breakdown` — 能耗分项

| 字段 | 类型 | 说明 |
|------|------|------|
| id | INTEGER PK | |
| paper_id | INTEGER FK | |
| step_name | TEXT | |
| heat_energy | REAL | 热耗 (标煤吨/吨产品) |
| electricity | REAL | 电耗 (kWh/吨产品) |
| energy_share_pct | REAL | 占比 % |
| heat_recovery_potential | TEXT | |

#### `environmental` — 环保与副产品

| 字段 | 类型 | 说明 |
|------|------|------|
| id | INTEGER PK | |
| paper_id | INTEGER FK | |
| waste_gas_type/amount/treatment/cost | TEXT/REAL | 废气四维 |
| waste_water_type/amount/treatment/cost | TEXT/REAL | 废水四维 |
| solid_waste_type/amount | TEXT | 废渣 |
| solid_waste_reusable | INTEGER | 0/1 |
| byproduct_name | TEXT | |
| byproduct_value | REAL | (元/吨) |
| byproduct_revenue_share | REAL | 贡献率 % |
| meets_env_policy | TEXT | |

#### `synergies` — 论文关联网络

| 字段 | 类型 | 说明 |
|------|------|------|
| id | INTEGER PK | |
| paper_id_a | INTEGER FK | |
| paper_id_b | INTEGER FK | |
| synergy_type | TEXT | 关联类型 (7种) |
| synergy_strength | TEXT | 强/中/弱 |
| synergy_description | TEXT | |
| combined_potential_score | REAL | |
| created_date | TEXT | |

### 3.4 `paper_attributes` — EAV 扩展表

| 字段 | 类型 | 说明 |
|------|------|------|
| id | INTEGER PK | |
| paper_id | INTEGER FK | |
| category | TEXT | 20 种分类 |
| attr_key | TEXT | 属性名 |
| attr_value | TEXT | 属性值 |
| attr_unit | TEXT | 单位 |
| source_context | TEXT | 数据来源 |

**20 种 category 分类：** raw_material_spec, raw_material_pretreatment, auxiliary_material, raw_material_constraint, process_params, equipment, product_quality, product_market, product_portfolio, scaleup_risk, scaleup_path, scaleup_precedent, sensitivity, competition, value_proposition, barrier, commercial_path, competitive_landscape

### 3.5 自动关联检测规则

| # | 规则 | 匹配逻辑 | 关联类型 |
|---|------|---------|---------|
| 1 | 同产品不同路线 | 同 target_product_category，不同 route_category | 对标竞争 |
| 2 | 副产物-原料匹配 | A 的 byproduct_name 关键词命中 B 的原料 | 副产品利用 |
| 3 | 路线耦合 | A 的 route ∈ {B,C,E}，B 的 route ∈ {H} | 工艺互补 |
| 4 | 参数共享 | attributes 中同 key 的值落在相近区间 | 条件优化借鉴 |
| 5 | 上下游产品 | A 的 target_product 是 B 的 auxiliary_material | 上下游衔接 |
| 6 | 设备共用 | 同 core_reactor_type | 设备共用 |
| 7 | 联产潜力 | A 和 B 的 raw_material 相同但 product 不同 | 联合生产 |

---

## 4. Python 脚本设计

### 4.1 环境要求
- Python 3.8+，仅标准库 (`sqlite3`, `json`, `argparse`, `csv`, `os`, `sys`)

### 4.2 `scripts/ingest.py`

```
用法:
  python ingest.py --json <path>           # 入库
  python ingest.py --json <path> --force   # 覆盖已存在论文
  python ingest.py --json <path> --dry-run # 仅校验不入库

输出:
  · 入库成功/失败状态
  · paper_id
  · 自动检测到的潜在关联列表 (paper_id_b + synergy_type)
```

**JSON 输入结构：**
```json
{
  "paper": { /* papers 表字段 */ },
  "process_steps": [ { "step_order": 1, "step_name": "...", ... } ],
  "energy": [ { "step_name": "...", "heat_energy": ..., ... } ],
  "environmental": { /* environmental 表字段 */ },
  "attributes": [ { "category": "...", "attr_key": "...", "attr_value": "..." } ],
  "synergies": [ { "paper_id_b": ..., "synergy_type": "..." } ]
}
```

### 4.3 `scripts/query.py`

```
用法:
  python query.py --list-all                    # 全论文摘要列表
  python query.py --paper-id N                  # 单论文详情
  python query.py --product "氧化镁"             # 按产品筛选
  python query.py --route C                     # 按技术路线筛选
  python query.py --min-margin 30               # 毛利率 >= 30%
  python query.py --compare 3,5,7               # 多论文横向对比
  python query.py --synergies-for N             # 论文N的关联
  python query.py --unlinked                    # 孤立论文
  python query.py --top 10                      # 综合评分 Top N
  python query.py --export --format csv         # CSV 导出
```

### 4.4 `scripts/report.py`

```
用法:
  python report.py --paper-id N                 # 单篇报告
  python report.py --all                        # 批量全量
  python report.py --synergy-report             # 全局关联网络报告
```

---

## 5. 文件结构

```
d:\claude-me\thesis analysis\
├── .claude\
│   └── claude.md                    # Claude 工作流配置
├── 体系基础架构.md                    # 分析维度树 + 数据库设计（已创建）
├── 注意事项.md                       # 原始需求（已存在）
├── docs\
│   └── superpowers\
│       └── specs\
│           └── 2026-06-26-talc-analysis-system-design.md  # 本规范（已创建）
├── db\
│   ├── schema.sql                   # 建表 DDL
│   └── thesis.db                    # SQLite 数据库 (gitignore)
├── scripts\
│   ├── ingest.py                    # 入库引擎
│   ├── query.py                     # 查询引擎
│   └── report.py                    # 报告生成器
├── papers\                          # Markdown 分析报告
│   └── PAPER-XXX-[简称].md
├── sources\                         # 原始论文文件 (gitignore)
└── templates\
    └── paper-analysis-template.md   # 标准化分析模板
```

---

## 6. Claude 工作流定义

### 6.1 触发规则

| 用户表述 | Claude 行为 |
|---------|------------|
| "入库新论文" / "分析这篇论文" / "分析新论文" | 执行 7 步标准入库流程 |
| "分析商业路径" / "有什么机会" / "推荐方向" | 查询高分论文 + 关联网络 → 提出商业路径建议 |
| "搜索论文" / "找论文" / "补充论文" | WebSearch 搜索 → 返回候选列表 |
| 提供论文文件 / DOI / 链接 | 自动识别并入库 |

### 6.2 标准入库流程 (7 步)

```
Step 1: 读取论文源文件
Step 2: 按 8 维度树状图逐项提取信息
Step 3: 生成结构化 JSON
Step 4: 生成 Markdown 分析报告 → papers/
Step 5: 自动比对已有论文库 (如库已存在)
Step 6: 输出关联报告 (如有)
Step 7: 交付 JSON + 报告 + 入库命令
```

### 6.3 Skills 使用规则

| 场景 | Skill |
|------|-------|
| 论文入库前讨论启发 | brainstorming |
| 多论文综述对比 | ars-lit-review |
| 深度调研某技术方向 | deep-research |
| 复杂关联分析 | synthesis_agent (Agent) |

---

## 7. 论文搜索策略

### 7.1 关键词组合

**中文：** 滑石粉, 硅酸镁, 酸浸, 煅烧, 碳化, 提纯, 硫酸镁, 氧化镁, 碳酸镁, 氢氧化镁, 白炭黑, 技术经济, 成本分析

**英文：** talc, talcum, magnesium silicate, acid leaching, calcination, carbonation, purification, magnesium sulfate, magnesium oxide, magnesium carbonate, Mg(OH)₂, precipitated silica, techno-economic, cost analysis, scale-up

### 7.2 质量标准
- SCI/EI 期刊论文，有实验数据支撑
- 排除专利文献
- 近 10-15 年为主；经典论文不限年份
- 优先：含经济性数据、TRL 较高、目标产品市场规模大

### 7.3 产品方向优先级
- **第一优先级**: 滑石粉 → 硫酸镁及其他镁化合物
- **第二优先级**: 高价值产品（高纯氧化镁、纳米氢氧化镁、轻质碳酸镁等）

---

## 8. 成功标准

1. 论文库达到 20+ 篇时，能自动发现至少 5 组有价值的跨论文关联
2. 能够对任意产品方向（如"硫酸镁"），查询出所有相关论文并按经济性排序
3. 能够基于论文库综合数据，提出 2-3 条完整的"滑石粉 → 终端产品"工业路径建议
4. 每篇新论文入库时间（从提供到报告完成）控制在单次对话内

---

*本规范由 Claude 与用户通过 grill-me → brainstorming 协作完成。*
