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
