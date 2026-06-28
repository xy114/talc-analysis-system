# MgO-SiO₂(-C-H₂O) 体系知识图谱 · 项目重建设计规格书

> **状态**: 设计已确认，待实施 | **日期**: 2026-06-28
> **背景**: grill-me 诊断发现三个根本方法论错误，导师要求从材料机理出发重构项目
> **前提**: 用户负责搜索和获取论文，Claude 负责分析框架和脚本

---

## 一、问题诊断（来自 grill-me）

| # | 错误 | 表现 | 后果 |
|---|------|------|------|
| 1 | 搜索边界错误 | 搜「talc / black talc」而非产物名（MgSiO₃, Mg₂SiO₄, MgO, SiC…） | 漏掉物相本身的基础研究论文 |
| 2 | 分析逻辑倒置 | 从已有商业路线反推机理，而非从物相-性质出发推导应用 | 所有路线评分悬空，缺乏机理支撑 |
| 3 | 叙事比例失调 | 把 <1% 的碳提升为二分框架的一半 | 导师一眼看出问题 |

**核心修正**：

```
旧逻辑：黑滑石 → 去碳/用碳 → 找论文支撑 → 商业评分
新逻辑：MgO-SiO₂(-C-H₂O) 体系 → T/P/气氛调控 → 物相组合 → 
        每个相的本征性质 → 可能的产品 → 工艺经济性 → 商业路径选择
```

---

## 二、核心数据结构：system-tree.json

### 2.1 树状拓扑

```
黑滑石原矿 (MgO·SiO₂·H₂O·<1%C)        ← depth=0, type=raw_material
    │
    ├──[process: 800°C空气]──► 顽火辉石 MgSiO₃  ──[property: 低介电]──► 5G微波介质陶瓷
    │                              │
    │                              ├──[property: 耐火>1500°C]──► 耐火材料
    │                              │
    │                              └──[property: 化学稳定]──► 涂料填料
    │
    ├──[process: N₂气氛900°C]──► 顽火辉石-碳复合材料 ──[property: 导电]──► 导电填料
    │
    ├──[process: 酸浸分离]──► 高纯MgO + SiO₂ ──[property: 高纯>99%]──► 镁化学品/白炭黑
    │
    └──[process: +CaO源]──► 钙镁橄榄石 CaMgSiO₄ ──[property: εr~7-8]──► 微波介质谐振器
```

- **节点三类**: raw_material / intermediate_phase / product / byproduct
- **边两类**: process（条件驱动相变，红线）/ property_link（性质连接应用，蓝虚线）
- 碳 <1% 降级为 process 边上的条件参数，不再是叙事主线

### 2.2 JSON Schema

```json
{
  "meta": {
    "name": "黑滑石 MgO-SiO₂(-C-H₂O) 物相-应用体系树",
    "version": "1.0.0",
    "last_updated": "2026-06-28"
  },
  "nodes": {
    "<node_id>": {
      "name": "中文名",
      "name_en": "English Name",
      "formula": "化学式",
      "type": "raw_material | intermediate_phase | product | byproduct",
      "depth": 0,
      "children": ["<child_id>"],
      "parents": ["<parent_id>"],
      "composition": {},
      "properties": [{
        "property": "性质名",
        "value": "数值或范围",
        "condition": "测定条件",
        "source_papers": ["PAPER-XXX"]
      }],
      "market_size": "市场规模（仅 product）",
      "unit_price": "单价（仅 product）",
      "source_papers": ["PAPER-XXX"],
      "notes": ""
    }
  },
  "edges": {
    "<edge_id>": {
      "from": "<node_id>",
      "to": "<node_id>",
      "type": "process | property_link",
      "label_short": "人读标签",
      "conditions": {
        "temperature": {"min": 700, "max": 900, "unit": "°C"},
        "atmosphere": "空气",
        "time": "2h",
        "additives": [],
        "equipment": ""
      },
      "via_property": "（仅 property_link）",
      "result_purity": "",
      "source_papers": ["PAPER-XXX"],
      "trl": 4,
      "notes": ""
    }
  }
}
```

### 2.3 Schema 演化规则

- schema 随研究深入可追加字段
- 向后兼容：新字段使用 optional 语义
- 每次 schema 变更在 `meta.version` 中记录

---

## 三、论文分析框架：四问注册制

替代旧 8 维度填表。每篇论文回答四个问题：

| 问题 | 内容 | 注册到树的什么位置 |
|------|------|-------------------|
| **Q1** 添加了什么节点？ | 新物相 / 已知物相的新性质数据 / 新产品 | `nodes` 新建或追加 `properties` |
| **Q2** 添加了什么边？ | 新工艺路线 / 已有路线的参数优化 / 新性质-应用连接 | `edges` 新建或追加 `source_papers` |
| **Q3** 数据可靠性？ | 实验规模 / 参数完整性 / 期刊等级 | `paper.q3_reliability`（元数据，暂不入树） |
| **Q4** 与其他论文的交叉验证？ | 谁验证了它 / 与谁矛盾 / 与谁互补 | `tree_contributions.papers_cross_validated` |

### 旧维度 → 新框架映射

| 旧 8 维度 | 新位置 |
|-----------|--------|
| 论文元信息 | `paper.*` |
| 原料体系 | `nodes[root].composition` |
| 工艺技术 | `edges[process].conditions` |
| 产物体系 | `nodes[product]` |
| 工程放大 | `q3_reliability.scale` + `edges[].trl` |
| 技术经济 | `nodes[product].market_size` |
| 商业化 | `edges[property_link]` |
| 论文间关联 | `q4_cross_validation` |

---

## 四、项目文件结构

```
d:\claude-me\thesis analysis\
├── system-tree.json              ★ 新核心：唯一真相源
├── paper-data/                   ★ 重构：新 schema
│   └── PAPER-XXX.json
├── papers/                       保留：MD 报告（按新模板）
├── scripts/
│   ├── ingest.py                 → 重写：校验 + 注册节点/边到 tree + 写回
│   ├── render_tree.py            ★ 新增：tree → DOT → SVG
│   └── render_tree_html.py       ★ 新增：tree → D3.js 交互式 HTML
├── output/                       ★ 新增：渲染产物
│   ├── system-tree.svg
│   └── system-tree.html
├── docs/
│   ├── 商业方案/                  → 全部重写（从物相推导）
│   └── 综述论文/                  → 重写
├── sources/                      保留
├── memory/                       保留
└── .claude/CLAUDE.md             → 更新
```

---

## 五、脚本体系

### 5.1 ingest.py（重写）

```
输入: paper-data/PAPER-XXX.json
流程:
  1. 校验 Q1-Q4 完整性
  2. 读 system-tree.json
  3. 注册新节点（去重）
  4. 注册新边（去重——检查 from/to/conditions 相似度）
  5. 写回 system-tree.json（version++）
  6. 输出: 注册了 X 新节点 / Y 新边 / Z 新性质
```

### 5.2 render_tree.py（新增 ~150行）

```
读 system-tree.json → 生成 DOT → 调 Graphviz → 写 SVG
DOT 渲染规则: 由 frontend-design 技能设计
  - 简约风，材料学科配色
  - raw_material: 根节点特殊处理
  - process 边: 红色实线
  - property_link 边: 蓝色虚线
```

### 5.3 render_tree_html.py（新增 ~200行）

```
读 system-tree.json → 生成自包含 HTML
  - 左侧: D3.js 可折叠树
  - 右侧: 节点详情面板（性质表 + 边列表 + 论文来源）
```

### 5.4 日常使用流程

```
用户搜到新论文 → 放 sources/ → 
Claude 四问分析 → 生成 paper-data JSON → 
运行 ingest.py → tree.json 更新 →
(可选) render_tree.py → SVG 更新 →
(可选) render_tree_html.py → HTML 更新
```

---

## 六、CLAUDE.md 更新要点

### 需要替换的部分

| 项目 | 旧 | 新 |
|------|----|----|
| 核心目标 | 寻找商业化路径 | 构建 MgO-SiO₂(-C-H₂O) 物相-性质-应用知识图谱 |
| 筛选标准 | 三档制（直接命中/边缘/跳过） | 四问注册制（Q1-Q4） |
| 搜索关键词 | talc AND (acid leaching OR calcination...) | 方向建议：MgSiO₃, Mg₂SiO₄, enstatite, forsterite, MgO from talc, talc decomposition...（用户自己搜） |
| 分析框架 | 8 维度树 | 四问 → 注册到 system-tree.json |
| 入库流程 | 7 步（含 SYNERGY-NETWORK-REPORT） | 6 步（取消独立关联报告，关联内嵌于 tree） |

### 需要删除的内容

- `体系基础架构.md` 引用 → 替换为 `system-tree.json`
- 商业评分字段（`composite_score`, `tech_route_category` 等）
- SYNERGY-NETWORK-REPORT.md 维护流程

### 保留内容

- PAPER-XXX 编号体系
- 单线程执行纪律
- 中文语言规则

---

## 七、实施顺序

| 阶段 | 内容 | 依赖 |
|------|------|:---:|
| **Phase 1** | 更新 CLAUDE.md（方法论文档先行） | 无 |
| **Phase 2** | 新建 `paper-data/` schema + 写一篇论文的 JSON 做范例 | Phase 1 |
| **Phase 3** | 重写 `scripts/ingest.py` | Phase 2 |
| **Phase 4** | 新建 `scripts/render_tree.py`（含 DOT 渲染） | Phase 3 |
| **Phase 5** | 用 frontend-design 设计 DOT 渲染风格（简约材料学配色） | Phase 4 |
| **Phase 6** | 新建 `scripts/render_tree_html.py` | Phase 4 |
| **Phase 7** | 选定 1-2 篇核心论文（如 PAPER-005 Meng）按新框架示范重入库 | Phase 3 |
| **Phase 8** | 建立初始 system-tree.json（基于现有 22 篇论文 + MgO-SiO₂ 相图知识） | Phase 6+7 |

---

*设计确认日期: 2026-06-28 | 用户已逐节确认 §1-§5*
