#!/usr/bin/env python3
"""用新方法论重写 CLAUDE.md。"""

from pathlib import Path

CLAUDE_PATH = Path(__file__).resolve().parent.parent / ".claude" / "CLAUDE.md"

def update():
    with open(CLAUDE_PATH, "r", encoding="utf-8") as f:
        content = f.read()

    # === 1. 替换头部描述 ===
    old_header = '# 滑石粉 论文商业化分析 · Claude 工作流配置\n\n> 本项目为企业寻找滑石粉（硅酸镁，MgSiO3）的大规模高值化商业化路径。\n> **目标原料**：黑滑石（低品位滑石，含有机碳和石英杂质，储量丰富，价格低廉）。\n> **核心目标**：从黑滑石出发，找到技术可行、经济合理、可规模化的大宗商业应用方向。\n> 产品不限于分离后的镁化学品，也包括陶瓷、耐火材料、功能填料等不分离 Mg/Si 的高附加值产品。\n> 参考文件: 体系基础架构.md（完整分析维度树 + 数据库设计）\n> **研究成果文档**: docs/ 目录（阶段性研究汇总、商业路径分析、缺失论文清单等）'

    new_header = '# 黑滑石 MgO-SiO₂(-C-H₂O) 体系知识图谱 · Claude 工作流配置\n\n> 本项目构建 MgO-SiO₂(-C-H₂O) 体系从原矿到产品的完整物相-性质-应用知识图谱。\n> **核心原料**：黑滑石（天然纳米级 MgO-SiO₂ 混合物，含 <1% 类石墨烯碳层）。\n> **核心逻辑**：以温度/气氛/添加剂为自变量 → 物相演化为因变量 → 每相本征性质 → 推导可能应用 → 工艺经济性倒推商业路径。\n> 碳(<1%)降级为特殊条件下的附注，不再是叙事主线；分离提纯（高纯 MgO/SiO₂）纳入同一物相图框架。\n> **核心数据文件**: system-tree.json（MgO-SiO₂(-C-H₂O) 物相-应用树，单一真相源）\n> **研究成果文档**: docs/ 目录'

    content = content.replace(old_header, new_header)

    # === 2. 替换论文筛选框架 ===
    old_filter = '''## 论文筛选评估框架

### 核心判断

**判断标准不是"是否分离镁"，而是"黑滑石做原料 -> 什么产品 -> 市场多大 -> 利润多高"。**

滑石同时含 MgO (~31%) 和 SiO2 (~63%)，两条并行商业化思路：

| 路线 | 描述 | 典型产品 |
|------|------|----------|
| **分离型** | 化学分解滑石，分离 Mg 和 Si | MgO、MgSO4、MgCO3、白炭黑、硅酸钠 |
| **共烧/复合型** | 不分离 Mg/Si，整体转化为高值材料 | 顽火辉石陶瓷、镁橄榄石耐火材料、堇青石、功能填料、铸造涂料 |

### 筛选三档制

| 档位 | 含义 | 标准 |
|------|------|------|
| 直接命中 | 黑滑石->高值产品，有完整工艺+数据 | 建议收藏，优先入库 |
| 边缘可参考 | 技术相关但不直接 | 可收藏，但不优先分析 |
| 跳过 | 无关 | 菱镁矿/白云石/蛇纹石加工、纯地质矿物学 |

### 搜索关键词

**中文核心**：滑石粉 AND (酸浸 OR 煅烧 OR 碳化 OR 提纯 OR 高值化 OR 综合利用)
**英文核心**：talc AND (acid leaching OR calcination OR carbonation OR valorization)
**排除词**：NOT 菱镁矿 NOT 白云石 NOT 蛇纹石 NOT 水镁石 NOT 橄榄石 NOT magnesite NOT dolomite NOT serpentine NOT brucite NOT olivine'''

    new_filter = '''## 论文分析框架：四问注册制

### 核心逻辑

**不从商业路线出发，从材料机理出发。** 本体系覆盖 MgO-SiO₂(-C-H₂O) 所有物相：

```
黑滑石原矿 → T/P/气氛调控 → 顽火辉石 MgSiO₃ / 镁橄榄石 Mg₂SiO₄ /
                              方镁石 MgO + 方石英 SiO₂ / 堇青石 /
                              钙镁橄榄石 CaMgSiO₄ / 液相 ...
```

每篇论文通过回答四个问题注册到 system-tree.json：

| 问题 | 内容 | 注册位置 |
|------|------|---------|
| **Q1** 添加了什么节点？ | 新物相发现 / 已知物相的新性质数据 / 新产品验证 | `nodes` 新建 或追加 `properties` |
| **Q2** 添加了什么边？ | 新工艺路线 / 已有路线的参数优化 / 新性质-应用连接 | `edges` 新建 或追加 `source_papers` |
| **Q3** 数据可靠性？ | 实验规模(powder/lab/pilot/industrial) / 参数完整性 / 期刊等级 | 元数据记录 |
| **Q4** 交叉验证？ | 谁验证了它 / 与谁矛盾 / 与谁互补 | `papers_cross_validated` |

### 搜索方向建议（用户自行搜索）

论文搜索不再限定「talc/black talc」——应搜索产物名和物相名：

| 方向 | 中文关键词 | 英文关键词 |
|------|-----------|-----------|
| 顽火辉石 | 顽火辉石 微波介质 介电 | enstatite MgSiO₃ microwave dielectric |
| 镁橄榄石 | 镁橄榄石 耐火 烧结 | forsterite Mg₂SiO₄ refractory |
| 滑石热分解 | 滑石 热分解 相变 | talc thermal decomposition dehydroxylation |
| MgO回收 | 滑石 酸浸 镁回收 | MgO recovery from talc leaching |
| 碳热还原 | 滑石 碳热还原 SiC | talc carbothermal reduction |
| 堇青石 | 堇青石 滑石 合成 | cordierite talc synthesis |
| 硅酸镁(通用) | 硅酸镁 陶瓷 复合材料 | magnesium silicate ceramic composite |

禁止搜索词（不属于本体系）：菱镁矿 magnesite / 白云石 dolomite / 蛇纹石 serpentine（除非作为对比参照）'''

    content = content.replace(old_filter, new_filter)

    # === 3. 替换入库流程 ===
    old_ingest = '''## 标准入库流程 (7 步) — 全部步骤必须完成，禁止跳过

**每一步都必须完成并输出可见交付物。禁止以"快速入库""批量处理""节省时间"等任何理由跳过或合并步骤。**
即使同时处理多篇论文，每篇论文也必须独立走完完整的 7 步流程。

### Step 1: 读取论文
- 读取 sources/ 目录下的论文源文件（.txt 或 .pdf）
- 如只有 PDF，优先使用同名的 .txt 版本（已做 OCR/文本提取）
- **交付物**: 已读取的论文全文（在上下文中）

### Step 2: 按维度提取信息
严格按照 体系基础架构.md 树状图的 8 大分支逐项提取：
1. 论文元信息 2. 原料体系 3. 工艺技术 4. 产物体系
5. 工程放大 6. 技术经济 7. 商业化 8. 论文间关联
- **交付物**: 8 维度信息提取完成（至少覆盖所有有数据的维度）

### Step 3: 生成结构化 JSON
按 体系基础架构.md 输入格式组装 JSON，保存为 paper-data-XXX.json。
- **交付物**: JSON 文件已写入磁盘

### Step 4: 生成 Markdown 分析报告（不可跳过）
按 templates/paper-analysis-template.md 模板，逐节填写生成完整的论文分析报告。
保存为 papers/PAPER-XXX-论文简称.md。
- **交付物**: Markdown 报告文件已写入磁盘
- **此步骤不可跳过。即使内容已在 JSON 中，也必须生成独立的 Markdown 报告。**

### Step 5: 自动比对已有论文库
按 7 条关联检测规则匹配已有论文：
1. 对标竞争 2. 副产品利用 3. 工艺互补 4. 上下游衔接
5. 设备共用 6. 联合生产 7. 条件优化借鉴
- **交付物**: 关联检测结果（与哪些已有论文产生哪种关联）

### Step 6: 更新关联网络报告
将新检测到的关联追加到 papers/SYNERGY-NETWORK-REPORT.md。
- **交付物**: 关联网络报告已更新

### Step 7: 入库 + 最终校验
**入库前自检清单（必须逐项确认）**：
- [ ] paper-data-XXX.json 文件存在且内容完整？
- [ ] papers/PAPER-XXX-...md 报告文件存在且覆盖 8 大模块？
- [ ] papers/SYNERGY-NETWORK-REPORT.md 已更新？
- [ ] JSON 中的 synergies 数据与关联报告一致？

以上 4 项全部确认后，执行：
```
python scripts/ingest.py --json paper-data-XXX.json
```
- **交付物**: 数据库已更新 + 入库成功确认

### 禁止行为

| 禁止 | 正确做法 |
|---------|-----------|
| 只生成 JSON 不入库 | JSON + Markdown + 入库 三步缺一不可 |
| 只入库不写 Markdown 报告 | Markdown 报告是必需交付物 |
| 批量快速入库（只跑 ingest.py） | 每篇论文独立走完 7 步 |
| 以"数据已经在 JSON 里"为由跳过 Step 4 | JSON 是机器可读的，Markdown 是人类可读的——两者用途不同 |
| 以"前面已经分析过了"为由跳过步骤 | 入库是独立流程，每次入库都需要完整的可追溯的交付物 |
| **在商业文档中使用旧编号 #N** | **必须使用 PAPER-XXX 格式引用论文** |'''

    new_ingest = '''## 标准入库流程 (5 步) — 全部步骤必须完成，禁止跳过

**每一步都必须完成并输出可见交付物。禁止以任何理由跳过或合并步骤。**

### Step 1: 读取论文
- 读取 sources/ 目录下的论文源文件（.txt 或 .pdf）
- **交付物**: 已读取的论文全文（在上下文中）

### Step 2: 四问分析
对论文逐一回答 Q1-Q4：
- **Q1** 添加了什么节点？（新物相 / 新性质数据 / 新产品）
- **Q2** 添加了什么边？（新工艺路线 / 参数优化 / 性质-应用连接）
- **Q3** 数据可靠性如何？（实验规模 / 参数完整性 / 期刊等级）
- **Q4** 交叉验证关系？（谁验证 / 与谁矛盾 / 与谁互补）
- **交付物**: 四问分析文段

### Step 3: 生成 paper-data JSON
按 paper-data/ 目录下的 schema 组装 JSON，保存为 `paper-data/PAPER-XXX.json`。
- 核心字段: `paper.tree_contributions`（new_nodes / new_edges / properties_added_to / papers_cross_validated）
- **交付物**: JSON 文件已写入 `paper-data/PAPER-XXX.json`

### Step 4: 注册到 system-tree.json
执行 `python scripts/ingest.py --json paper-data/PAPER-XXX.json`
- ingest.py 自动完成：校验四问完整性 → 节点去重注册 → 边去重注册 → 性质数据追加 → 写回 system-tree.json
- **交付物**: system-tree.json 已更新，终端输出注册统计

### Step 5: 生成 Markdown 分析报告
按四问结构填写论文分析报告，保存为 `papers/PAPER-XXX-论文简称.md`。
- **交付物**: Markdown 报告文件已写入磁盘

### 禁止行为

| 禁止 | 正确做法 |
|---------|-----------|
| 只生成 JSON 不注册到树 | JSON + 树注册 + MD 三步缺一不可 |
| 以"商业路线 D1/D2/..."分类论文 | 应以"该论文为 MgO-SiO₂ 物相树贡献了什么节点/边"分类 |
| 以"快速入库"为由跳过四问分析 | 四问是核心——没有四问就无法注册到树 |
| **在商业文档中使用旧编号 #N** | **必须使用 PAPER-XXX 格式引用论文** |'''

    content = content.replace(old_ingest, new_ingest)

    # === 4. 移除 SYNERGY-NETWORK-REPORT 引用 ===
    content = content.replace(
        '- 关联报告 `papers/SYNERGY-NETWORK-REPORT.md` 为完整的论文清单和关联网络',
        '- 论文间关联信息存储在 system-tree.json 的 `papers_cross_validated` 字段和各节点的 `source_papers` 列表中'
    )

    # === 5. 更新触发规则 ===
    old_trigger = '''## 触发规则

| 用户表述 | 执行动作 |
|---------|---------|
| "入库新论文" / "分析这篇论文" / "分析新论文" | 执行 7 步标准入库流程 |
| "分析商业路径" / "有什么机会" / "推荐方向" | 商业路径综合推荐流程 |
| "搜索论文" / "找论文" / "补充论文" | 论文搜索流程 |
| 发送论文摘要/简介请求评估 | 按筛选三档制快速判断 + 给出收藏建议 |
| **放入了/添加了/收集了 论文源文件** | **立即对该论文执行标准入库流程** |

### 论文源文件自动入库规则

当用户说论文X的字版也收集了/论文X放进source里了/放入了论文X等表述时，立即执行：读取源文件→8维度提取→生成JSON→入库→生成Markdown报告→关联检测→更新关联网络报告。'''

    new_trigger = '''## 触发规则

| 用户表述 | 执行动作 |
|---------|---------|
| "入库新论文" / "分析这篇论文" / "分析新论文" | 执行 5 步标准入库流程（四问注册制） |
| "渲染树" / "更新树图" / "导出 SVG" | 运行 `python scripts/render_tree.py` |
| "打开知识图谱" / "浏览体系树" | 运行 `python scripts/render_tree_html.py` 并用浏览器打开 |
| "搜索论文" / "找论文" | 提供搜索方向建议（产物名搜索，用户自行检索） |
| **放入了/添加了/收集了 论文源文件** | **立即对该论文执行 5 步标准入库流程** |

### 论文源文件自动入库规则

当用户添加论文源文件时，立即执行：读取源文件→四问分析→生成 paper-data JSON→注册到 system-tree.json→生成 MD 报告。'''

    content = content.replace(old_trigger, new_trigger)

    # === 6. 更新 Skills 表格 ===
    old_skills = '''| 场景 | 调用 Skill |
|------|-----------|
| 入库前讨论论文的商业启发 | brainstorming |
| 多论文综述对比 | ars-lit-review |
| 深度调研某技术方向 | deep-research |
| 复杂跨论文关联分析 | synthesis_agent (Agent) |'''

    new_skills = '''| 场景 | 调用 Skill |
|------|-----------|
| 入库前讨论论文如何注册到物相树 | brainstorming |
| 设计/修改 system-tree.json schema | brainstorming |
| 多论文综述对比 | ars-lit-review |
| 深度调研某物相/性质方向 | deep-research |
| 复杂跨论文交叉验证分析 | synthesis_agent (Agent) |
| 设计 DOT 渲染风格 | frontend-design |'''

    content = content.replace(old_skills, new_skills)

    # === 7. 更新编号映射表（移除"对应路线"列） ===
    old_mapping_header = '| PAPER编号 | 论文简称 | 年份 | 期刊 | 对应路线 |'
    new_mapping_header = '| PAPER编号 | 论文简称 | 年份 | 期刊 | 对物相树的主要贡献 |'
    content = content.replace(old_mapping_header, new_mapping_header)

    # 改写具体行
    replacements = [
        ('| **PAPER-002** | 杨华明 — 黑滑石矿物学特征及加工应用研究进展 (综述) | 2023 | 材料导报 | 综述框架 |',
         '| **PAPER-002** | 杨华明 — 黑滑石矿物学特征及加工应用研究进展 (综述) | 2023 | 材料导报 | 综述：黑滑石→多物相→多应用全景 |'),
        ('| **PAPER-003** | 裘林莉 — 黑滑石煅烧产物的酸活化及晶格重建 | 2017 | 硅酸盐通报 | D4/D9 |',
         '| **PAPER-003** | 裘林莉 — 黑滑石煅烧产物的酸活化及晶格重建 | 2017 | 硅酸盐通报 | 煅烧→酸活化→Zn²⁺晶格重建→抗菌 |'),
        ('| **PAPER-004** | 刘子峥 — 黑滑石基微波介质陶瓷材料的结构与性能 | 2024 | 电子元件与材料 | D2 |',
         '| **PAPER-004** | 刘子峥 — 黑滑石基微波介质陶瓷材料的结构与性能 | 2024 | 电子元件与材料 | 黑滑石→MgSiO₃ 微波介质陶瓷 εr=5.11 |'),
        ('| **PAPER-005** | Meng — Evolution of Black Talc upon Thermal Treatment | 2022 | Minerals (SCI) | 基础/全路线 |',
         '| **PAPER-005** | Meng — Evolution of Black Talc upon Thermal Treatment | 2022 | Minerals (SCI) | 核心基础：30-1000°C 完整物相演化序列 |'),
        ('| **PAPER-006** | 吴小文 — 黑滑石高温物相行为变化及复合材料性能 | 2017 | 陶瓷学报 | D3 |',
         '| **PAPER-006** | 吴小文 — 黑滑石高温物相行为变化及复合材料性能 | 2017 | 陶瓷学报 | N₂气氛→碳石墨化→导电顽火辉石复合材料 |'),
        ('| **PAPER-007** | Huang — HF+HCl 混合酸浸滑石 (Mg 97.98%) | 2025 | Minerals Eng. (SCI Q1) | D9 |',
         '| **PAPER-007** | Huang — HF+HCl 混合酸浸滑石 (Mg 97.98%) | 2025 | Minerals Eng. (SCI Q1) | 酸浸分离→高纯 MgO + SiO₂ |'),
        ('| **PAPER-008** | Xiao — 滑石基 CaMgSiO4 微波介质陶瓷 (成本降80%) | 2025 | Ceramics Int. (SCI Q1) | D2 |',
         '| **PAPER-008** | Xiao — 滑石基 CaMgSiO₄ 微波介质陶瓷 (成本降80%) | 2025 | Ceramics Int. (SCI Q1) | +CaO→CaMgSiO₄ 微波介质陶瓷 Q×f=59212 |'),
        ('| **PAPER-009** | Bu — 滑石基 Li2MgSiO4 微波介质陶瓷 | 2025 | Ceramics Int. (SCI Q1) | D2 |',
         '| **PAPER-009** | Bu — 滑石基 Li₂MgSiO₄ 微波介质陶瓷 | 2025 | Ceramics Int. (SCI Q1) | +Li₂CO₃→Li₂MgSiO₄ 低温烧结 1075°C |'),
        ('| **PAPER-010** | Fang — Cu2+ 掺杂抑制 MgSiO3 相变 (Qxf=93600) | 2024 | Ceramics Int. (SCI Q1) | D2 |',
         '| **PAPER-010** | Fang — Cu²⁺ 掺杂抑制 MgSiO₃ 相变 (Q×f=93600) | 2024 | Ceramics Int. (SCI Q1) | Cu²⁺掺杂→稳定 MgSiO₃ 相、抑制相变 |'),
        ('| **PAPER-011** | Ullah — Co2+ 掺杂 MgSiO3 陶瓷 (Qxf=145846) | 2019 | J Mater Sci: Mater Electron (SCI) | D2 |',
         '| **PAPER-011** | Ullah — Co²⁺ 掺杂 MgSiO₃ 陶瓷 (Q×f=145846) | 2019 | J Mater Sci: Mater Electron (SCI) | Co²⁺掺杂→最高 Q×f=145846 近零 τf |'),
    ]
    for old, new in replacements:
        content = content.replace(old, new)

    with open(CLAUDE_PATH, "w", encoding="utf-8") as f:
        f.write(content)

    print("[OK] CLAUDE.md 已更新为新方法论")

if __name__ == "__main__":
    update()
