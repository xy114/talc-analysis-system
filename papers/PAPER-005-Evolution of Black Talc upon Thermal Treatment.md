# PAPER-005 Evolution of Black Talc upon Thermal Treatment

> **论文编号**: PAPER-005
> **作者**: Meng Y, Xie W, Wu H, Tariq S M, Yang H (通讯)
> **年份**: 2022
> **期刊**: Minerals (MDPI, SCI)
> **DOI**: 10.3390/min12020155
> **类型**: 实验研究 (Experiment)
> **机构**: 中南大学 + 中国地质大学(武汉)

---

## 核心贡献：四阶段热演化模型

**这是 MgO-SiO₂(-C-H₂O) 知识图谱最核心的实验论文。** 通过 in-situ XRD + in-situ FTIR + TG-DSC/TG-MS + BET + SEM + TEM + SAED + ICP 多技术正交验证，建立了黑滑石 30-1000°C 完整物相演化序列：

| 阶段 | 温度 | 过程 | 关键数据 |
|:---:|------|------|---------|
| I | 30-165°C | 脱水 | 质量损失0.32%, d(006)不变 |
| II | 165-580°C | 有机碳氧化 | CO₂ m/z=44峰值600°C, 层间距膨胀 |
| III | 800-900°C | 脱羟基活化 | CI 75.8%→51.0%, 活化窗口 |
| IV | 900-1000°C | 相转变→顽火辉石 | DSC 920.7°C, T1000完全转变 |

## Q1: 新增节点 (3个)

- `dehydrated_talc` (脱水滑石) — depth 1
- `decarbonized_talc` (脱碳滑石) — depth 1
- `dehydroxylated_talc` (脱羟基滑石/非晶化) — depth 1, **活化窗口**

## Q2: 新增边 (3条)

- e0015: 原矿→脱水滑石 (30-165°C)
- e0016: 原矿→脱碳滑石 (165-580°C)
- e0017: 原矿→脱羟基滑石 (800-900°C)

追加 e0001: 原矿→顽火辉石 (900-1000°C, 此前由PAPER-002/004注册但参数不完整)

## Q3: 数据可靠性 ★★★★★

- **技术栈**: in-situ XRD + in-situ FTIR + ex-situ TG-DSC/TG-MS/BET/SEM/TEM/SAED/ICP/Zeta
- **温度点**: 15个 (100-1000°C)
- **期刊**: SCI (Minerals)
- **资金**: 国家杰出青年科学基金 + 国家自然科学基金

**评价**: 本体系最权威的单篇实验论文。方法论极其完善。

## Q4: 交叉验证

- **被综述引用**: PAPER-002
- **互补**: PAPER-006 (N₂气氛对比), PAPER-003 (酸活化利用活化窗口), PAPER-004 (顽火辉石微波介电)

---

*入库日期: 2026-06-28 | 树版本: v0.1.4*
