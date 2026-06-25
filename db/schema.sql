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
    trl_level INTEGER CHECK (trl_level BETWEEN 1 AND 9),  -- 1-9
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
    tech_feasibility_score INTEGER DEFAULT 0 CHECK (tech_feasibility_score BETWEEN 0 AND 10),
    econ_feasibility_score INTEGER DEFAULT 0 CHECK (econ_feasibility_score BETWEEN 0 AND 10),
    market_attractiveness_score INTEGER DEFAULT 0 CHECK (market_attractiveness_score BETWEEN 0 AND 10),
    scaleup_feasibility_score INTEGER DEFAULT 0 CHECK (scaleup_feasibility_score BETWEEN 0 AND 10),
    composite_score REAL DEFAULT 0.0 CHECK (composite_score BETWEEN 0 AND 100),
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
    FOREIGN KEY (paper_id) REFERENCES papers(id) ON DELETE CASCADE,
    UNIQUE(paper_id, step_order)
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
    synergy_type TEXT NOT NULL CHECK (synergy_type IN ('对标竞争','副产品利用','工艺互补','条件优化借鉴','上下游衔接','设备共用','联合生产')),
    synergy_strength TEXT CHECK (synergy_strength IN ('强','中','弱')),
    synergy_description TEXT,
    combined_potential_score REAL,
    created_date TEXT DEFAULT (date('now')),
    FOREIGN KEY (paper_id_a) REFERENCES papers(id) ON DELETE CASCADE,
    FOREIGN KEY (paper_id_b) REFERENCES papers(id) ON DELETE CASCADE,
    UNIQUE(paper_id_a, paper_id_b),
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
    FOREIGN KEY (paper_id) REFERENCES papers(id) ON DELETE CASCADE,
    UNIQUE(paper_id, category, attr_key)
);

-- 索引
CREATE INDEX IF NOT EXISTS idx_papers_year ON papers(year);
CREATE INDEX IF NOT EXISTS idx_papers_route ON papers(tech_route_category);
CREATE INDEX IF NOT EXISTS idx_papers_product ON papers(target_product_category);
CREATE INDEX IF NOT EXISTS idx_papers_composite ON papers(composite_score);
CREATE INDEX IF NOT EXISTS idx_process_steps_paper ON process_steps(paper_id);
CREATE INDEX IF NOT EXISTS idx_energy_paper ON energy_breakdown(paper_id);
CREATE INDEX IF NOT EXISTS idx_attributes_category ON paper_attributes(paper_id, category);
CREATE INDEX IF NOT EXISTS idx_synergies_pair ON synergies(paper_id_a, paper_id_b);
CREATE INDEX IF NOT EXISTS idx_synergies_b ON synergies(paper_id_b);
