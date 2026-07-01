# PAPER-018 多孔 Mg₂SiO₄ + LPD-TiO₂ 微波介电性能

> **论文编号**: PAPER-018
> **作者**: Sugihara J, Kakimoto K, Kagomiya I, Ohsato H
> **年份**: 2006 (发表 2007)
> **期刊**: Journal of the European Ceramic Society 27, 3105–3108 (SCI Q1)
> **DOI**: 10.1016/j.jeurceramsoc.2006.11.032
> **类型**: 实验研究 (Experiment)
> **机构**: Nagoya Institute of Technology, Japan

---

## 核心贡献：Mg₂SiO₄ 全体系最高 Q×f = 270,000 GHz + TiO₂-LPD τf 补偿

**本论文首次定量报告了 Mg₂SiO₄（镁橄榄石）的微波介电性能，Q×f = 270,000 GHz 为 MgO-SiO₂ 体系最高纪录。** 同时提出了一种避免杂相的 τf 补偿策略：多孔骨架 + LPD 溶液沉积 TiO₂，将 τf 从 −73 改善至 −46 ppm/°C。

| 指标 | 纯 Mg₂SiO₄ | TiO₂-LPD 复合 (5次) |
|------|:--:|:--:|
| Q×f | **270,000 GHz** | ~10,000 GHz（劣化，未解决） |
| εr | **6.8** | — |
| τf | −73 ppm/°C | **−46 ppm/°C** |

> **体系对比**：Q×f=270,000 远超 Co²⁺-MgSiO₃（PAPER-011, 145,846），确立 forsterite 为 MgO-SiO₂ 体系中介电损耗最低的物相。

**关键创新**：LPD 法（(NH₄)₂TiF₆ + H₃BO₃）在 Mg₂SiO₄ 孔壁沉积 TiO₂，避免了传统固相混合时 Mg₂SiO₄ + TiO₂ → MgTi₂O₅ + MgSiO₃ 的有害杂相反应。

## Q1: 新增节点 (1 个)

| 节点ID | 名称 | 类型 | 深度 | 关键数据 |
|--------|------|------|:--:|---------|
| `forsterite_mw_ceramic` | 镁橄榄石微波介质陶瓷 | product | 2 | Q×f=270,000, εr=6.8, τf=−73(纯)/−46(TiO₂) |

### 向已有节点追加性质

- `forsterite_from_talc` ← Q×f=270,000 GHz, εr=6.8, τf=−73 ppm/°C（3 条）

## Q2: 新增边 (1 条)

- e0021: `forsterite_from_talc` → `forsterite_mw_ceramic`（造孔+LPD-TiO₂→τf 补偿, TRL 3）

> ⚠ 注：论文用高纯 Mg(OH)₂ + SiO₂ 固相合成 Mg₂SiO₄（1150°C/2h 预烧 → 1400°C/2h 烧结），非滑石路线。但介电性质为本征性质，适用于黑滑石 >1100°C 煅烧所得 Mg₂SiO₄。τf 补偿策略通用于任何来源的 Mg₂SiO₄ 骨架。

## Q3: 数据可靠性 ★★★★★

| 维度 | 评估 |
|------|------|
| **实验规模** | powder（实验室） |
| **参数完整性** | PMMA 含量/粒径/CIP 三重变量控制孔隙率 + LPD 次数变量 + εr/τf/Q×f 四响应 |
| **期刊等级** | SCI Q1（J. Eur. Ceram. Soc.，陶瓷领域顶刊） |
| **方法** | Hakki-Coleman 谐振法（TE₀₁₁ 模）+ SEM 微观结构 |
| **资金** | 日本文部科学省科学研究费补助金（基盘研究 B） |
| **局限** | Q×f 在 TiO₂ 填充后从 270,000 骤降至 ~10,000 GHz（孔填充不完全 + 可能的界面反应），τf 仍距零较远（−46 ppm/°C） |

## Q4: 交叉验证

| 关系 | 论文 | 说明 |
|------|------|------|
| **互补** | PAPER-004 刘子峥 2024 | MgSiO₃ 微波介电（Q×f=56,782），forsterite Q×f 高出 4.7× |
| **互补** | PAPER-010 Fang 2024 | Cu²⁺-MgSiO₃（Q×f=93,600），仍低于纯 Mg₂SiO₄ |
| **互补** | PAPER-011 Ullah 2019 | Co²⁺-MgSiO₃（Q×f=145,846，此前最高），被 forsterite 超越 |

**本文定位**: Mg₂SiO₄ 微波介电方向的奠基准论文——提供本征介电参数基准值。τf 补偿策略有待后续研究优化（目标：近零 τf 同时保持 Q×f）。

---

## MgO-SiO₂ 体系微波介电性能排名（更新后）

| 排名 | 材料 | Q×f (GHz) | εr | τf (ppm/°C) | 来源 |
|:--:|------|:--:|:--:|:--:|------|
| 1 | **Mg₂SiO₄（纯）** | **270,000** | 6.8 | −73 | PAPER-018 |
| 2 | Co²⁺-MgSiO₃ | 145,846 | — | 近零 | PAPER-011 |
| 3 | Cu²⁺-MgSiO₃ | 93,600 | — | — | PAPER-010 |
| 4 | CaMgSiO₄ | 59,212 | — | — | PAPER-008 |
| 5 | MgSiO₃（未掺杂） | 56,782 | 5.11 | −18 | PAPER-004 |

---

*入库日期: 2026-07-01 | 树版本: v0.1.17*
