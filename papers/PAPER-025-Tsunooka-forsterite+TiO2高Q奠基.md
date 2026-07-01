# PAPER-025 纯试剂 forsterite + TiO₂ 高 Q 微波介质——奠基之作

> **论文编号**: PAPER-025
> **作者**: T. Tsunooka, M. Androu, Y. Higashida, H. Sugiura, H. Ohsato
> **年份**: 2003
> **期刊**: Journal of the European Ceramic Society 23, 2573–2578（SCI Q1 顶刊）
> **DOI**: 10.1016/S0955-2219(03)00177-8
> **类型**: 实验研究
> **机构**: 日本精细陶瓷中心 (JFCC) + 名古屋工业大学 + Aishin Seiki

---

## 核心贡献：forsterite 微波介电的奠基论文 + TiO₂ 双功能机理 + τf 补偿失败的根本原因

本论文建立了 forsterite (Mg₂SiO₄) 作为毫米波介质陶瓷的**性能基准**（Q×f=240,000 GHz——2003 年世界纪录），系统研究了 TiO₂ 添加的烧结助熔和 τf 补偿双重效应，并**首次揭示 TiO₂ 无法有效补偿 forsterite τf 的化学根源**——这一发现直接影响了后续所有 forsterite 微波介质研究（包括 PAPER-020 改用 B₂O₃）。

### 关键数据

| 性能 | 纯 forsterite (0% TiO₂) | 最优 TiO₂ (1 wt%) | TiO₂ 过量 (30 wt%) |
|------|:---:|:---:|:---:|
| Q×f (GHz) | **240,000** | 230,000 | 急剧下降 |
| εr | 6.8 | 7.0 | 线性增加 |
| τf (ppm/°C) | -60~-70 | **-65** | ≈-63 |
| 烧结温度 | ~1400°C | **~1300°C** (降 ~100°C) | >1350°C |
| 物相 | 纯 forsterite | 纯 forsterite | forsterite + MgTi₂O₅ |

### TiO₂ 双功能机理

| 功能 | 效果 | 机理 |
|------|:---:|------|
| **烧结助熔** | ✅ 降 100°C | TiO₂ 促进晶界扩散→加速致密化 |
| **τf 补偿** | ❌ 完全无效 | TiO₂ 与 MgO-SiO₂ 反应生成 MgTi₂O₅→被消耗 |

---

## 为什么 τf 补偿失败？（核心机理发现）

按 Lichtenecker 混合法则，13.3 wt% TiO₂（τf=+450 ppm/°C）应可将 forsterite τf 从 -67 调至 0。但实验发现 τf **几乎不随 TiO₂ 添加量变化**（始终在 -63~-70 ppm/°C）。

**原因**：TiO₂ 在 forsterite 体系中不是惰性第二相——它与 MgO-SiO₂ 发生化学反应：
- 0-10 wt% TiO₂ → TiO₂ 完全固溶/反应进入 forsterite 结构
- >10 wt% TiO₂ → MgTi₂O₅ 第二相析出，Q 值急剧下降
- rutil 相在**所有组成**中消失（XRD 未检测到）

**对黑滑石路线 forsterite 的启示**：PAPER-020 (Wang 2026) 选择 B₂O₃ 而非 TiO₂ 作为黑滑石基 forsterite 的烧结助剂——正是因为本论文已证明 TiO₂ 的 τf 补偿功能被化学反应抵消，而 B₂O₃ 形成液相促进烧结但不与 MgO 发生等价反应。

---

## Q1-Q4 摘要

- **Q1**: 新建 `forsterite_mw_dense_tio2` 节点（10 条性质），向 `forsterite_from_talc` 追加 2 条性质数据
- **Q2**: 无新边（纯试剂路线，独立于黑滑石路线）
- **Q3**: JECS (SCI Q1)，日本顶尖陶瓷研究机构，全因子实验，Hakki-Coleman 法
- **Q4**: 强互补 PAPER-018（多孔 forsterite+LPD）、PAPER-020（黑滑石+B₂O₃）

---

## 第一性原理分析

### TiO₂ 与 MgO 反应的化学驱动力

从 Pauling 电负性角度：Ti⁴⁺(电负性 1.54) vs Mg²⁺(1.31) vs Si⁴⁺(1.90)。Ti⁴⁺ 的电负性和离子半径（0.605 Å）介于 Mg²⁺(0.72 Å) 和 Si⁴⁺(0.26 Å) 之间 → 在 forsterite 晶格中 Ti⁴⁺ 可部分替代 Mg²⁺ 或 Si⁴⁺ 位 → 低浓度 TiO₂ 固溶消失。当 TiO₂ > 溶解度极限 → 独立成核 MgTi₂O₅（MgO·TiO₂ 中间化合物在热力学上比 TiO₂ 更稳定）。

τf 补偿需要 TiO₂ 以**独立金红石相**存在（+450 ppm/°C 来自 Ti-O 八面体的正 τf），但 MgTi₂O₅ 的 τf 并非高正值→TiO₂ 一旦反应就失去了补偿能力。这解释了 TiO₂ 在几乎所有硅酸镁体系中都未能有效补偿 τf 的普适规律。

---

*入库日期: 2026-07-01 | 树版本: v0.2.5 | 类型: 纯试剂基准对照 + 机理关键*
