# PAPER-010 Cu²⁺ 掺杂抑制 MgSiO₃ 相变——Q×f 提升至 93,600 GHz

> **论文编号**: PAPER-010
> **作者**: Fang et al.
> **年份**: 2024
> **期刊**: Ceramics International (SCI Q1)
> **类型**: 实验研究 (Experiment)

---

## 核心贡献：Cu²⁺ 掺杂稳定 MgSiO₃ 原顽火辉石相

**本论文解决了 MgSiO₃ 微波介质陶瓷的关键瓶颈——高温相变（proto-enstatite → ortho-enstatite）导致性能劣化。** 通过 Cu²⁺ 掺杂进入 MgSiO₃ 晶格，有效抑制相变，将 Q×f 从 56,782 GHz 提升至 **93,600 GHz**。

| 指标 | 未掺杂 (PAPER-004) | Cu²⁺ 掺杂 (本论文) | 提升 |
|------|:--:|:--:|:--:|
| Q×f | 56,782 GHz | **93,600 GHz** | +65% |
| 相稳定性 | proto↔ortho 相变 | Cu²⁺ 稳定 proto 相 | — |

**机理**: Cu²⁺ 离子半径与 Mg²⁺ 接近，进入晶格后改变局部配位环境，抑制高温下 proto→ortho 的结构弛豫。

## Q1: 新增节点

**无。** 本论文向已有节点追加掺杂性能数据：

- `black_talc_mw_ceramic` ← Q×f (Cu²⁺ 掺杂) = 93,600 GHz
- `enstatite_from_talc` ← Cu²⁺ 相变抑制机理

## Q2: 新增边 (1 条)

- `enstatite_from_talc` → `black_talc_mw_ceramic`（Cu²⁺ 掺杂, TRL 3）

## Q3: 数据可靠性 ★★★★★

| 维度 | 评估 |
|------|------|
| **实验规模** | powder（实验室） |
| **期刊等级** | SCI Q1（Ceramics International） |
| **评价** | 掺杂策略有明确机理支撑。需验证不同 Cu²⁺ 浓度的最优窗口。 |

## Q4: 交叉验证

| 关系 | 论文 | 说明 |
|------|------|------|
| **互补** | PAPER-004 刘子峥 2024 | PAPER-004 提供未掺杂基线（Q×f=56,782），本论文在其上优化 |
| **互补** | PAPER-011 Ullah 2019 | Co²⁺ 掺杂为平行策略，Q×f 更高（145,846） |

**本文定位**: 掺杂工程路线——证明过渡金属离子掺杂是提升 MgSiO₃ 微波介电性能的有效策略。与 PAPER-011（Co²⁺）构成掺杂元素对比。

---

*入库日期: 2026-06-28 | 树版本: v0.1.9*
