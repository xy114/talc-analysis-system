# System-Tree Schema v2 设计规格书

> **目的**：将产品节点按工艺路线拆分，边 = 工艺路线，属性 = 该路线的性质
> **日期**：2026-07-01
> **状态**：待实施

---

## 问题陈述

当前 schema（v0.1.x）将不同工艺路线制造的同名产物的性质混在一个节点中。

**典型案例** — `forsterite_mw_ceramic` 节点包含：
- PAPER-018 纯试剂+造孔+LPD-TiO₂ 路线：Q×f=270,000
- PAPER-020 黑滑石+B₂O₃ 路线：Q×f=151,137
- 13 条性质混在一起，无法区分来源

**同样** — `black_talc_mw_ceramic` 节点包含：
- PAPER-004 原矿 1325°C 直接烧结：Q×f=56,782
- PAPER-010 Cu²⁺ 掺杂：Q×f=93,600
- PAPER-011 Co²⁺ 掺杂：Q×f=145,846

**根因**：性质数据扁平挂在节点下，边承载了多套工艺信息但无法区分。

---

## 新 Schema 核心原则

1. **产品节点按工艺路线命名和拆分**——不同添加剂/温度/气氛 → 不同产品节点
2. **边 = 工艺路线**——每条边指向唯一产品节点，描述唯一工艺条件
3. **性质属于工艺路线**——每个性质挂在对应路线的产品节点下
4. **中间相不拆**——中间相是热力学必经状态，性质不因工艺显著变化
5. **交叉验证绑定到边**——因为验证的是"这条工艺路线是否靠谱"，不是"这个物相是否存在"

---

## Section 1: 节点分类与命名

### 节点类型（不变）

```
raw_material       — 原料（仅 raw_black_talc）
intermediate_phase — 中间相（热力学必经状态，不拆分）
product            — 最终产品，按工艺路线命名
```

### 产品节点命名规则

格式：`{产品名}({关键工艺区分})`

关键工艺区分取自：添加剂、掺杂离子、烧结温度窗口、气氛、喷涂方法等。

### 拆分对照表

| 旧节点 ID | 旧名称 | 新节点 ID | 新名称 | 来源 |
|------|------|------|------|------|
| `black_talc_mw_ceramic` | 黑滑石微波介质陶瓷 | `black_talc_mw_direct` | 黑滑石微波介质陶瓷(原矿1325°C) | PAPER-004 |
| | | `black_talc_mw_cu` | 黑滑石微波介质陶瓷(Cu²⁺掺杂) | PAPER-010 |
| | | `black_talc_mw_co` | 黑滑石微波介质陶瓷(Co²⁺掺杂) | PAPER-011 |
| `forsterite_mw_ceramic` | 镁橄榄石微波介质陶瓷 | `forsterite_mw_pure` | 镁橄榄石微波介质陶瓷(纯试剂+LPD-TiO₂) | PAPER-018 |
| | | `forsterite_mw_talc` | 镁橄榄石微波介质陶瓷(黑滑石+B₂O₃) | PAPER-020 |
| `camgsio4_ceramic` | 钙镁橄榄石微波介质陶瓷 | `camgsio4_ceramic` | 钙镁橄榄石微波介质陶瓷(CaO固相反应) | PAPER-008 |
| `li2mgsio4_ceramic` | Li₂MgSiO₄微波介质陶瓷 | `li2mgsio4_ceramic` | 硅酸镁锂微波介质陶瓷(Li₂CO₃低温烧结) | PAPER-009 |
| `cordierite_ceramic` | 堇青石陶瓷 | `cordierite_ceramic` | 堇青石陶瓷(煤矸石+铝矾土) | PAPER-002 |
| `forsterite_tbc` | 镁橄榄石热障涂层 | `forsterite_tbc` | 镁橄榄石热障涂层(APS喷涂) | PAPER-019 |
| `refractory_brick` | 镁橄榄石耐火砖 | `refractory_brick` | 镁橄榄石耐火砖(高温烧结) | PAPER-002 |
| `talc_photocatalyst` | 黑滑石光催化剂 | `talc_photocatalyst` | 黑滑石光催化剂(TiO₂限域) | PAPER-002 |
| `talc_antibacterial` | 黑滑石抗菌材料 | `talc_antibacterial` | 黑滑石抗菌材料(离子交换) | PAPER-002 |
| `zn_enstatite_antibacterial` | Zn-顽火辉石抗菌材料 | `zn_enstatite_antibacterial` | Zn-顽火辉石抗菌材料(ZnSO₄晶格重建) | PAPER-003 |

### 中间相节点（保持不变）

```
raw_black_talc
enstatite_from_talc
forsterite_from_talc
separated_mgo
separated_sio2
graphitized_carbon
dehydrated_talc
decarbonized_talc
dehydroxylated_talc
acid_activated_enstatite
```

---

## Section 2: 边模型

### 规则

- 每条边 = 一条且仅一条工艺路线
- 每条边 source_papers 为单一论文（或同路线多篇验证论文）
- 每条边指向唯一产品节点
- type 保留 `process`（中间相→产品工艺边）和 `property_link`（交叉引用边）

### 多路线拆边示例

**旧** — e0021 承载两条路线：
```
e0021: forsterite_from_talc → forsterite_mw_ceramic
       source_papers: [PAPER-018, PAPER-020]
```

**新** — 拆为两条边：
```
e0021a: forsterite_from_talc → 镁橄榄石微波介质陶瓷(纯试剂+LPD-TiO₂)
        conditions: {预烧1150°C, 烧结1400°C, PMMA造孔, LPD TiO₂, 退火700°C}
        source_papers: [PAPER-018]

e0021b: forsterite_from_talc → 镁橄榄石微波介质陶瓷(黑滑石+B₂O₃)
        conditions: {预烧1100°C, 烧结1350°C, B₂O₃ 0.2wt%, MgO补Mg}
        source_papers: [PAPER-020]
```

### 中间相边（保持不变）

```
e0001: raw_black_talc → enstatite_from_talc  (850-1000°C 煅烧)
e0002: raw_black_talc → forsterite_from_talc  (>1100°C 高温煅烧)
e0003: raw_black_talc → separated_mgo  (酸浸分离)
...
```

---

## Section 3: Schema 字段变更

### 节点 schema（不变）

```json
{
  "id": "string",
  "name": "string",
  "name_en": "string",
  "formula": "string",
  "type": "raw_material | intermediate_phase | product",
  "depth": "int",
  "children": ["id", ...],
  "parents": ["id", ...],
  "properties": [{"property": "string", "value": "string", "condition": "string?", "source_papers": ["id"]}],
  "source_papers": ["id"],
  "notes": "string",
  "papers_cross_validated": ["id", ...]
}
```

### 属性对象新增字段

```json
{
  "property": "Q×f",
  "value": "151,137 GHz",
  "condition": "1350°C 烧结",
  "source_papers": ["PAPER-020"],
  "process_route": "黑滑石+B₂O₃助烧"
}
```

`process_route` 字段用于追溯——当后续有新工艺路线时，可以通过此字段确认该性质来自哪条路线。

### 边 schema（不变）

```json
{
  "from": "id",
  "to": "id",
  "type": "process | property_link",
  "label_short": "string",
  "conditions": {
    "temperature": {"min": 0, "max": 0, "unit": "°C"},
    "atmosphere": "string",
    "additives": ["string"],
    "equipment": "string?"
  },
  "source_papers": ["id"],
  "trl": "int",
  "notes": "string",
  "papers_cross_validated": ["id", ...]
}
```

### `papers_cross_validated` 迁移

- 产品节点：移除 `papers_cross_validated`（迁移到边）
- 中间相节点：保留 `papers_cross_validated`（中间相不拆）
- 边：新增 `papers_cross_validated` 字段

---

## Section 4: 迁移计划

### Step 1: 归档旧树
- 复制 `system-tree.json` → `system-tree-v0.1.19-legacy.json`
- 新树从空 v2 骨架开始

### Step 2: 迁移脚本 `scripts/migrate_to_v2.py`
- 读取旧树
- 遍历所有 product 节点 → 按 `source_papers` 拆分属性
- 生成新 product 节点（ID 按命名规则生成）
- 遍历所有边 → product 相关边按 `source_papers` 拆分
- 中间相节点原样复制
- 交叉验证数据迁移到边级别
- 输出新 `system-tree.json`

### Step 3: 人工复核
- 检查自动拆分的节点命名是否合理
- 检查是否有遗漏的工艺路线
- 确认 children/parents 双向引用正确

### Step 4: 更新 ingest.py
- 适配新 schema 的 product 节点创建逻辑
- 新增 product ID 生成函数（基于命名规则）
- 边去重逻辑适配（新 key: from + to + source_paper 主论文）

### Step 5: 更新 render_tree_html.py
- 适配节点数增加（~10→~13+）
- 更长的节点名称显示处理
- nodeSize / fontSize 可能需要微调

### Step 6: 更新 paper-data JSON
- 更新已有 PAPER-XXX.json 的 `tree_contributions.new_nodes` 以匹配新节点 ID
- 仅影响有产品节点的论文（PAPER-003/004/008/009/010/011/018/019/020）

---

## Section 5: 设计决策记录

| 决策 | 选项 | 理由 |
|------|------|------|
| 中间相是否拆分 | 不拆 | 中间相是热力学必经状态，性质不由工艺显著决定 |
| 产品节点命名 | 中文描述式 `产品名(工艺)` | 直观可读，适合以中文为主的论文体系 |
| 单路线产品是否也改名 | 统一改 | 保持结构一致，后续有新路线时无需重新命名 |
| 交叉验证归属 | 绑定到边 | 验证的是工艺路线是否靠谱，不是物相是否存在 |
| 迁移方式 | 自动脚本+人工复核 | 数据量大，手工会出错；自动拆分可能命名不精确 |
