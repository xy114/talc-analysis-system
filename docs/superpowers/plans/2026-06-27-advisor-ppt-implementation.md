# 导师汇报 PPT 实施计划

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 从设计规格书构建 44 页 HTML 学术幻灯片，经 frontend-design 多轮打磨至学术会议演讲级别，最终导出为 .pptx 交付导师。

**Architecture:** 单文件 HTML 幻灯片（`presentation/slides.html`），内嵌 CSS 设计系统和 JS 导航逻辑。每页为 `<section class="slide">`，采用 CSS Grid 固定布局骨架。图表占位框使用虚线边框 + 标注信息。打磨完成后用 python-pptx 脚本逐页重建为 .pptx。

**Tech Stack:** HTML5 + CSS Grid/Flexbox + inline SVG + vanilla JS (键盘导航) / Python 3 + python-pptx 库

## Global Constraints

- 44 页, 16:9 比例 (1280×720px 基准)
- 色板: 深蓝 `#1a365d` / 琥珀 `#d97706` / 石墨灰 `#374151` / 浅灰 `#e5e7eb` / 钛白 `#f7f8fa`
- 字体: 标题 思源黑体 Bold 28-32pt / 正文 思源宋体 Regular 16-18pt / 数据 JetBrains Mono 16-20pt
- 无装饰性 emoji。图表占位框统一使用 dashed border + 灰色底色
- 所有论文引用使用 PAPER-XXX 格式
- 内容来源: docs/初步商业方案/tier-1-entry-level.md + spec §3 逐页规格

## File Structure

```
presentation/
├── slides.html          # 主幻灯片文件 (单文件, 内嵌 CSS + JS, ~44 个 <section>)
├── export_to_pptx.py    # python-pptx 迁移脚本
└── README.md            # 使用说明 (如何打开/导航/导出PDF)
```

**设计决策**:
- 单文件 HTML — 双击即开, 方便分享, frontend-design 单文件迭代
- 每页 `<section class="slide">` — CSS scroll-snap 实现翻页, 键盘左右键导航
- 内嵌 SVG 图表 — 无外部依赖, 可精确控制数据图样式
- 图表占位框 `<div class="placeholder">` — 虚线边框 + 标注文字

---

### Task 1: 项目脚手架 + CSS 设计系统

**Files:**
- Create: `presentation/slides.html`

**Interfaces:**
- Consumes: spec §2 (视觉设计系统)
- Produces: CSS 变量体系, 布局骨架 `.slide` 类, 图表占位框 `.placeholder` 类, 所有后续 Task 共用

- [ ] **Step 1: 创建 presentation/ 目录和 slides.html 骨架**

```bash
mkdir -p presentation
```

- [ ] **Step 2: 写入 CSS 设计系统 + HTML 骨架**

写入 `presentation/slides.html`，包含完整 `<style>` 标签（CSS 变量、字体、布局骨架、占位框样式、表格/卡片/图表组件样式）和 `<body>` 框架（含键盘导航 JS 占位）。由于文件较长（CSS 系统 ~200 行 + 44 页内容），此步骤建立完整 CSS 系统和前 5 页幻灯片作为样板。

**CSS 核心变量和布局**:

```css
:root {
  --deep-blue: #1a365d;
  --amber: #d97706;
  --graphite: #374151;
  --light-gray: #e5e7eb;
  --titanium: #f7f8fa;
  --dark-overlay-text: #e2e8f0;
  --slide-width: 1280px;
  --slide-height: 720px;
  --font-title: 'Source Han Sans SC', 'Noto Sans SC', 'Microsoft YaHei', sans-serif;
  --font-body: 'Source Han Serif SC', 'Noto Serif SC', 'SimSun', serif;
  --font-mono: 'JetBrains Mono', 'Cascadia Code', 'Consolas', monospace;
}

* { margin: 0; padding: 0; box-sizing: border-box; }

body {
  font-family: var(--font-body);
  font-size: 16pt;
  color: var(--graphite);
  background: #0f172a; /* 演示时外围暗色 */
  display: flex;
  flex-direction: column;
  align-items: center;
  overflow-x: hidden;
}

/* 幻灯片容器 — scroll-snap 翻页 */
.slide {
  width: var(--slide-width);
  height: var(--slide-height);
  background: var(--titanium);
  position: relative;
  padding: 48px 64px 36px 64px;
  scroll-snap-align: start;
  display: flex;
  flex-direction: column;
  margin-bottom: 4px;
  box-shadow: 0 4px 24px rgba(0,0,0,0.3);
}

/* 章节标签 — 左上角固定 */
.section-tag {
  font-family: var(--font-title);
  font-size: 8pt;
  font-weight: 500;
  color: var(--amber);
  text-transform: uppercase;
  letter-spacing: 0.12em;
  position: absolute;
  top: 28px;
  left: 64px;
}
.section-tag::before { content: "▎"; margin-right: 6px; }

/* 页面标题 */
.slide-title {
  font-family: var(--font-title);
  font-size: 28pt;
  font-weight: 700;
  color: var(--deep-blue);
  margin-bottom: 24px;
  line-height: 1.25;
}

/* 正文内容区 */
.content {
  flex: 1;
  display: flex;
  flex-direction: column;
  justify-content: flex-start;
  gap: 16px;
}

/* 双栏布局 */
.two-col { display: grid; grid-template-columns: 1fr 1fr; gap: 32px; flex: 1; align-items: center; }
.col-left, .col-right { display: flex; flex-direction: column; gap: 12px; }

/* 图表占位框 */
.placeholder {
  border: 2px dashed var(--light-gray);
  background: #f9fafb;
  border-radius: 6px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 24px;
  min-height: 180px;
  gap: 8px;
}
.placeholder-label {
  font-family: var(--font-title);
  font-size: 13pt;
  color: #9ca3af;
}
.placeholder-source {
  font-family: var(--font-body);
  font-size: 9pt;
  color: #b0b7c3;
  line-height: 1.4;
}

/* 数据表格 */
.data-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 14pt;
}
.data-table th {
  font-family: var(--font-title);
  font-size: 12pt;
  color: var(--deep-blue);
  background: var(--light-gray);
  padding: 8px 12px;
  text-align: left;
  border-bottom: 2px solid var(--deep-blue);
}
.data-table td {
  padding: 8px 12px;
  border-bottom: 1px solid var(--light-gray);
  font-size: 14pt;
}

/* 数据高亮 */
.data-highlight {
  font-family: var(--font-mono);
  font-size: 18pt;
  font-weight: 500;
  color: var(--amber);
}

/* 卡片 */
.card-grid { display: grid; gap: 16px; flex: 1; }
.card-grid.cols-2 { grid-template-columns: 1fr 1fr; }
.card-grid.cols-3 { grid-template-columns: 1fr 1fr 1fr; }
.card-grid.cols-4 { grid-template-columns: 1fr 1fr 1fr 1fr; }
.card-grid.cols-5 { grid-template-columns: 1fr 1fr 1fr 1fr 1fr; }

.card {
  background: white;
  border: 1px solid var(--light-gray);
  border-radius: 6px;
  padding: 20px;
  display: flex;
  flex-direction: column;
  gap: 8px;
}
.card-header {
  font-family: var(--font-title);
  font-size: 15pt;
  font-weight: 700;
  color: var(--deep-blue);
}
.card-body {
  font-size: 13pt;
  color: var(--graphite);
  line-height: 1.5;
  flex: 1;
}
.card-tag {
  font-family: var(--font-title);
  font-size: 9pt;
  color: var(--amber);
  text-transform: uppercase;
  letter-spacing: 0.06em;
}

/* 页脚 */
.slide-footer {
  position: absolute;
  bottom: 20px;
  left: 64px;
  right: 64px;
  display: flex;
  justify-content: space-between;
  font-size: 10pt;
  color: #9ca3af;
  border-top: 1px solid var(--light-gray);
  padding-top: 10px;
}

/* 流程步骤 */
.steps { display: flex; align-items: center; gap: 8px; }
.step {
  background: var(--light-gray);
  border-radius: 4px;
  padding: 12px 16px;
  font-family: var(--font-title);
  font-size: 13pt;
  font-weight: 600;
  color: var(--deep-blue);
  text-align: center;
}
.step-arrow { color: var(--amber); font-size: 18pt; font-weight: 700; }

/* D2 路线卡片颜色 */
.route-d1 { border-left: 3px solid #6b7280; }
.route-d2 { border-left: 3px solid #3b82f6; }
.route-d3 { border-left: 3px solid #10b981; }
.route-d4 { border-left: 3px solid #8b5cf6; }
.route-d9 { border-left: 3px solid #f59e0b; }

/* 封面与大图背景页 */
.slide-cover {
  background: linear-gradient(135deg, rgba(26,54,93,0.88) 0%, rgba(26,54,93,0.72) 100%);
  color: var(--dark-overlay-text);
  justify-content: center;
  align-items: center;
  text-align: center;
}
.slide-cover .slide-title { color: white; font-size: 36pt; }
.slide-cover .slide-subtitle { font-size: 18pt; opacity: 0.85; margin-top: 8px; }
.slide-cover .slide-meta { font-size: 14pt; opacity: 0.65; margin-top: 32px; }

/* 暗底覆盖页 */
.slide-dark {
  background: linear-gradient(135deg, rgba(26,54,93,0.92) 0%, rgba(15,23,42,0.92) 100%);
  color: var(--dark-overlay-text);
  justify-content: center;
  align-items: center;
  text-align: center;
}
.slide-dark .slide-title { color: white; }
.slide-dark .data-table th { color: var(--dark-overlay-text); background: rgba(255,255,255,0.08); border-color: rgba(255,255,255,0.2); }
.slide-dark .data-table td { border-color: rgba(255,255,255,0.1); color: var(--dark-overlay-text); }
```

- [ ] **Step 3: 验证 CSS 在浏览器中渲染正确**

用浏览器打开 `presentation/slides.html`，检查:
- 色板全部生效（深蓝标题、琥珀数据、石墨灰正文）
- 占位框虚线边框显示正常
- 16:9 比例无变形

- [ ] **Step 4: Commit**

```bash
git add presentation/slides.html
git commit -m "feat: CSS design system + HTML skeleton for advisor PPT"
```

---

### Task 2: 第 1-5 页 — 开篇章节

**Files:**
- Modify: `presentation/slides.html` (追加 5 个 `<section>` 到 `<body>`)

**Interfaces:**
- Consumes: Task 1 CSS 变量和类
- Produces: 5 个完整 slide, 建立封面/目录/科普/对比/流程图五种页面模板

每页 HTML 结构如下（在 `<body>` 中追加，位于导航 JS 之前）:

**第 1 页 · 封面 (`slide-cover`)**:

```html
<section class="slide slide-cover" id="s1">
  <div style="position:absolute;top:0;left:0;right:0;bottom:0;background:rgba(26,54,93,0.55);z-index:0;"></div>
  <div style="position:relative;z-index:1;">
    <div class="section-tag" style="color:rgba(255,255,255,0.6);">汇报主题</div>
    <h1 class="slide-title" style="font-size:38pt;margin-bottom:12px;">黑滑石高值化商业化<br>初步研究汇报</h1>
    <p class="slide-subtitle">从 10 亿吨低品位资源到 5 条技术路线</p>
    <p class="slide-meta">汇报人：[你的名字] &nbsp;|&nbsp; 导师：[导师姓名] &nbsp;|&nbsp; 2026年7月 &nbsp;|&nbsp; [学校名称]</p>
  </div>
  <div class="placeholder" style="position:absolute;bottom:80px;right:64px;width:200px;height:60px;background:rgba(255,255,255,0.08);border-color:rgba(255,255,255,0.2);">
    <span class="placeholder-label" style="color:rgba(255,255,255,0.5);">背景图占位</span>
    <span class="placeholder-source" style="color:rgba(255,255,255,0.35);">广丰黑滑石矿区全景</span>
  </div>
</section>
```

**第 2 页 · 目录**:

```html
<section class="slide" id="s2">
  <div class="section-tag">汇报提纲</div>
  <h1 class="slide-title">汇报提纲</h1>
  <div class="content" style="gap:18px;margin-top:12px;">
    <div style="display:flex;align-items:flex-start;gap:16px;">
      <span style="font-family:var(--font-mono);font-size:22pt;font-weight:700;color:var(--deep-blue);min-width:40px;">01</span>
      <div><strong>为什么关注黑滑石？</strong><br><span style="font-size:13pt;color:#6b7280;">10亿吨闲置资源 + 核心矛盾 + 五条技术路线全景</span></div>
    </div>
    <div style="display:flex;align-items:flex-start;gap:16px;">
      <span style="font-family:var(--font-mono);font-size:22pt;font-weight:700;color:var(--deep-blue);min-width:40px;">02</span>
      <div><strong>我们有什么知识资产？</strong><br><span style="font-size:13pt;color:#6b7280;">10篇论文 x 5条路线 x 25条关联</span></div>
    </div>
    <div style="display:flex;align-items:flex-start;gap:16px;">
      <span style="font-family:var(--font-mono);font-size:22pt;font-weight:700;color:var(--amber);min-width:40px;">03</span>
      <div><strong style="color:var(--amber);">初阶方案：现在就能做的事</strong><br><span style="font-size:13pt;color:#6b7280;">Phase 0a-0d 完整执行路径 · 预算 ~8,000元 · 产出 3篇论文+1项专利</span></div>
    </div>
    <div style="display:flex;align-items:flex-start;gap:16px;">
      <span style="font-family:var(--font-mono);font-size:22pt;font-weight:700;color:var(--deep-blue);min-width:40px;">04</span>
      <div><strong>中阶展望</strong><br><span style="font-size:13pt;color:#6b7280;">团队 + 中型企业 — D2+D3 双旗舰</span></div>
    </div>
    <div style="display:flex;align-items:flex-start;gap:16px;">
      <span style="font-family:var(--font-mono);font-size:22pt;font-weight:700;color:var(--deep-blue);min-width:40px;">05</span>
      <div><strong>高阶愿景</strong><br><span style="font-size:13pt;color:#6b7280;">产学研联合体 — 五条路线全线部署</span></div>
    </div>
    <div style="display:flex;align-items:flex-start;gap:16px;">
      <span style="font-family:var(--font-mono);font-size:22pt;font-weight:700;color:var(--deep-blue);min-width:40px;">06</span>
      <div><strong>下一步行动 + 讨论</strong></div>
    </div>
  </div>
  <div class="slide-footer"><span>黑滑石高值化商业化 · 初步研究汇报</span><span>2 / 44</span></div>
</section>
```

**第 3 页 · 黑滑石是什么 (`two-col` 布局)**:

```html
<section class="slide" id="s3">
  <div class="section-tag">开篇 · 背景</div>
  <h1 class="slide-title">黑滑石：被低估的 10 亿吨</h1>
  <div class="two-col">
    <div class="col-left">
      <div class="placeholder" style="flex:1;">
        <span class="placeholder-label">黑滑石原矿手标本照片</span>
        <span class="placeholder-source">来源: PAPER-005 Meng 2022 Fig.1<br>位置: PDF 第 2 页, 约 15% 位置<br>备选: 百度搜索"广丰黑滑石原矿"</span>
      </div>
    </div>
    <div class="col-right">
      <div class="card">
        <div class="card-header">矿物学身份</div>
        <div class="card-body">
          <table style="width:100%;font-size:14pt;border-collapse:collapse;">
            <tr><td style="padding:6px 12px;color:#6b7280;">化学式</td><td style="padding:6px 12px;">Mg<sub>3</sub>Si<sub>4</sub>O<sub>10</sub>(OH)<sub>2</sub></td></tr>
            <tr><td style="padding:6px 12px;color:#6b7280;">结构</td><td style="padding:6px 12px;">2:1 T-O-T 层状硅酸盐</td></tr>
            <tr><td style="padding:6px 12px;color:#6b7280;">MgO 含量</td><td style="padding:6px 12px;"><span class="data-highlight">~31%</span></td></tr>
            <tr><td style="padding:6px 12px;color:#6b7280;">SiO<sub>2</sub> 含量</td><td style="padding:6px 12px;"><span class="data-highlight">~63%</span></td></tr>
            <tr><td style="padding:6px 12px;color:#6b7280;">有机碳</td><td style="padding:6px 12px;">1-2% (黑色的来源)</td></tr>
            <tr><td style="padding:6px 12px;color:#6b7280;">储量</td><td style="padding:6px 12px;"><span class="data-highlight">10 亿吨</span> (广丰, 探明)</td></tr>
          </table>
        </div>
      </div>
    </div>
  </div>
  <div class="slide-footer"><span>数据来源: PAPER-005 Meng 2022; PAPER-002 杨华明 2023</span><span>3 / 44</span></div>
</section>
```

**第 4 页 · 核心矛盾**:

```html
<section class="slide" id="s4">
  <div class="section-tag">开篇 · 问题</div>
  <h1 class="slide-title">核心矛盾：为什么 10 亿吨堆在那里？</h1>
  <div class="two-col">
    <div class="col-left">
      <div class="card" style="background:#fef2f2;border-color:#fecaca;">
        <div class="card-header" style="color:#991b1b;">当前用途与困境</div>
        <div class="card-body" style="font-size:14pt;line-height:2.0;">
          陶瓷填料 <span style="color:#6b7280;">80%+</span><br>
          造纸填料 <span style="color:#6b7280;">~10%</span><br>
          涂料/塑料 <span style="color:#6b7280;">&lt;10%</span><br>
          <hr style="border-color:#fecaca;margin:12px 0;">
          煅烧白滑石仅 <span class="data-highlight">500&ndash;800 元/吨</span><br>
          黑色被视为"劣质"→ 价格低 30&ndash;50%
        </div>
      </div>
    </div>
    <div class="col-right">
      <div class="card" style="background:#f0fdf4;border-color:#bbf7d0;">
        <div class="card-header" style="color:#166534;">换个角度：碳不是杂质，是资源</div>
        <div class="card-body" style="font-size:14pt;line-height:2.0;">
          碳可以<span style="color:var(--deep-blue);font-weight:700;">原位石墨烯化</span><br>
          镁可以<span style="color:var(--deep-blue);font-weight:700;">分离做高值化学品</span><br>
          硅可以<span style="color:var(--deep-blue);font-weight:700;">整体转化为特种陶瓷</span><br>
          <hr style="border-color:#bbf7d0;margin:12px 0;">
          导电填料可达 <span class="data-highlight">5,000&ndash;20,000 元/吨</span>
        </div>
      </div>
    </div>
  </div>
  <div class="slide-footer"><span>数据来源: PAPER-005 Meng 2022; PAPER-002 杨华明 2023</span><span>4 / 44</span></div>
</section>
```

**第 5 页 · 五条路线全景图 (inline SVG)**:

```html
<section class="slide" id="s5">
  <div class="section-tag">开篇 · 路线全景</div>
  <h1 class="slide-title">五条技术路线：覆盖从低到高的阶梯</h1>
  <div class="content" style="align-items:center;justify-content:center;">
    <svg viewBox="0 0 1100 380" style="width:100%;max-height:420px;">
      <!-- 中心节点 -->
      <rect x="420" y="150" width="200" height="60" rx="8" fill="var(--deep-blue)"/>
      <text x="520" y="186" text-anchor="middle" fill="white" font-family="var(--font-title)" font-size="16" font-weight="700">黑滑石原矿</text>
      <!-- 五条分支线 -->
      <!-- D1 传统煅烧 -->
      <line x1="620" y1="170" x2="850" y2="40" stroke="#6b7280" stroke-width="2"/>
      <rect x="855" y="15" width="170" height="50" rx="6" fill="white" stroke="#6b7280" stroke-width="1.5"/>
      <text x="940" y="38" text-anchor="middle" fill="#6b7280" font-family="var(--font-title)" font-size="13" font-weight="700">D1 传统煅烧</text>
      <text x="940" y="54" text-anchor="middle" fill="#6b7280" font-size="10">白滑石填料</text>
      <!-- D2 5G陶瓷 -->
      <line x1="620" y1="175" x2="850" y2="100" stroke="#3b82f6" stroke-width="2.5"/>
      <rect x="855" y="75" width="170" height="50" rx="6" fill="white" stroke="#3b82f6" stroke-width="2"/>
      <text x="940" y="98" text-anchor="middle" fill="#3b82f6" font-family="var(--font-title)" font-size="13" font-weight="700">D2 5G微波陶瓷</text>
      <text x="940" y="114" text-anchor="middle" fill="#3b82f6" font-size="10">滤波器/基站</text>
      <!-- D3 N₂碳石墨烯 (高亮 — 初阶旗帜) -->
      <line x1="620" y1="185" x2="850" y2="170" stroke="#10b981" stroke-width="3.5"/>
      <rect x="855" y="145" width="170" height="50" rx="6" fill="#f0fdf4" stroke="#10b981" stroke-width="2.5"/>
      <text x="940" y="168" text-anchor="middle" fill="#10b981" font-family="var(--font-title)" font-size="13" font-weight="700">D3 N₂碳石墨烯 ★</text>
      <text x="940" y="184" text-anchor="middle" fill="#10b981" font-size="10">导电/导热功能填料</text>
      <!-- D4 抗菌 -->
      <line x1="620" y1="190" x2="850" y2="240" stroke="#8b5cf6" stroke-width="2"/>
      <rect x="855" y="215" width="170" height="50" rx="6" fill="white" stroke="#8b5cf6" stroke-width="1.5"/>
      <text x="940" y="238" text-anchor="middle" fill="#8b5cf6" font-family="var(--font-title)" font-size="13" font-weight="700">D4 抗菌岩板</text>
      <text x="940" y="254" text-anchor="middle" fill="#8b5cf6" font-size="10">功能建材</text>
      <!-- D9 酸浸 -->
      <line x1="620" y1="195" x2="850" y2="310" stroke="#f59e0b" stroke-width="2"/>
      <rect x="855" y="285" width="170" height="50" rx="6" fill="white" stroke="#f59e0b" stroke-width="1.5"/>
      <text x="940" y="308" text-anchor="middle" fill="#f59e0b" font-family="var(--font-title)" font-size="13" font-weight="700">D9 酸浸分离</text>
      <text x="940" y="324" text-anchor="middle" fill="#f59e0b" font-size="10">MgO + 白炭黑</text>
      <!-- 图例 -->
      <rect x="30" y="300" width="12" height="12" rx="2" fill="#10b981"/>
      <text x="48" y="310" fill="#10b981" font-size="11" font-weight="600">初阶旗帜</text>
      <rect x="120" y="300" width="12" height="12" rx="2" fill="#3b82f6"/>
      <text x="138" y="310" fill="#3b82f6" font-size="11" font-weight="600">中阶主攻</text>
      <rect x="210" y="300" width="12" height="12" rx="2" fill="#6b7280"/>
      <text x="228" y="310" fill="#6b7280" font-size="11" font-weight="600">高阶全线</text>
    </svg>
  </div>
  <div class="slide-footer"><span>来源: PAPER-002 杨华明综述 §5 应用方向分类</span><span>5 / 44</span></div>
</section>
```

- [ ] **Step 5: 浏览器验证 5 页渲染**

打开 `presentation/slides.html`，逐一确认每页布局、颜色、占位框标注。

- [ ] **Step 6: Commit**

```bash
git add presentation/slides.html
git commit -m "feat: slides 1-5 opening chapter (cover, TOC, background, pain points, roadmap)"
```

---

### Task 3: 第 6-10 页 — 痛点即机会

**Files:**
- Modify: `presentation/slides.html` (追加 5 个 `<section>`)

**Interfaces:**
- Consumes: Task 1 CSS 系统 + Task 2 建立的页面模板模式
- Produces: 5 个 slide (广丰现状/碳翻转/四阶段/N₂对比/机会总结)

**关键页面代码**:

**第 8 页 · 四阶段热演化 (SVG 信息图 + 占位框)**:

```html
<section class="slide" id="s8">
  <div class="section-tag">痛点即机会 · 科学基础</div>
  <h1 class="slide-title">黑滑石热演化：PAPER-005 Meng 的核心发现</h1>
  <div class="two-col">
    <div class="col-left">
      <div class="placeholder" style="flex:1;">
        <span class="placeholder-label">TG-DSC 热分析曲线</span>
        <span class="placeholder-source">来源: PAPER-005 Meng 2022 Fig.2<br>位置: PDF 第 5 页, 约 35% 位置</span>
      </div>
      <div class="placeholder" style="flex:1;">
        <span class="placeholder-label">In-situ XRD 物相演化</span>
        <span class="placeholder-source">来源: PAPER-005 Meng 2022 Fig.6<br>位置: PDF 第 9 页, 约 60% 位置</span>
      </div>
    </div>
    <div class="col-right">
      <svg viewBox="0 0 460 420" style="width:100%;">
        <!-- 温度轴 -->
        <line x1="60" y1="380" x2="440" y2="380" stroke="var(--graphite)" stroke-width="1.5"/>
        <!-- 四个阶段 -->
        <rect x="70" y="340" width="80" height="36" rx="4" fill="#dbeafe"/>
        <text x="110" y="356" text-anchor="middle" font-size="10" fill="#1e40af">Stage I</text>
        <text x="110" y="370" text-anchor="middle" font-size="9" fill="#1e40af">30-165°C</text>
        <rect x="160" y="340" width="90" height="36" rx="4" fill="#fee2e2"/>
        <text x="205" y="356" text-anchor="middle" font-size="10" fill="#991b1b">Stage II</text>
        <text x="205" y="370" text-anchor="middle" font-size="9" fill="#991b1b">165-580°C</text>
        <rect x="260" y="340" width="80" height="36" rx="4" fill="#fef3c7"/>
        <text x="300" y="356" text-anchor="middle" font-size="10" fill="#92400e">Stage III</text>
        <text x="300" y="370" text-anchor="middle" font-size="9" fill="#92400e">800-900°C</text>
        <rect x="350" y="340" width="80" height="36" rx="4" fill="#d1fae5"/>
        <text x="390" y="356" text-anchor="middle" font-size="10" fill="#065f46">Stage IV</text>
        <text x="390" y="370" text-anchor="middle" font-size="9" fill="#065f46">900-1000°C</text>
        <!-- 标注 -->
        <text x="110" y="320" text-anchor="middle" font-size="9" fill="#6b7280">脱水</text>
        <text x="205" y="320" text-anchor="middle" font-size="9" fill="#6b7280">碳氧化→CO₂↑</text>
        <text x="300" y="320" text-anchor="middle" font-size="9" fill="#6b7280">脱羟基</text>
        <text x="390" y="320" text-anchor="middle" font-size="9" fill="#6b7280">相转变</text>
        <!-- 关键标注框 -->
        <rect x="245" y="240" width="200" height="36" rx="4" fill="var(--amber)" opacity="0.12" stroke="var(--amber)" stroke-width="1.5" stroke-dasharray="4,2"/>
        <text x="345" y="254" text-anchor="middle" font-size="10" fill="var(--amber)" font-weight="700">活化窗口 800-900°C</text>
        <text x="345" y="268" text-anchor="middle" font-size="9" fill="var(--amber)">无定形 SiO₂/MgO 峰值</text>
        <rect x="145" y="240" width="200" height="36" rx="4" fill="#3b82f6" opacity="0.08" stroke="#3b82f6" stroke-width="1.5" stroke-dasharray="4,2"/>
        <text x="245" y="254" text-anchor="middle" font-size="10" fill="#3b82f6" font-weight="700">N₂保护窗口 &gt;165°C</text>
        <text x="245" y="268" text-anchor="middle" font-size="9" fill="#3b82f6">阻止碳氧化，保留碳资源</text>
      </svg>
    </div>
  </div>
  <div class="slide-footer"><span>数据来源: PAPER-005 Meng 2022 Fig.2-6</span><span>8 / 44</span></div>
</section>
```

**第 9 页 · N₂ vs Air 对比** 和其余页面遵循相同模式：根据 spec §3.2 逐页规格中的内容，使用 `.two-col` / `.card` / `.placeholder` / `.data-table` 组合排版。

- [ ] **Step 7: 写入第 6-10 页 HTML, 浏览器验证**

- [ ] **Step 8: Commit**

```bash
git add presentation/slides.html
git commit -m "feat: slides 6-10 pain point to opportunity chapter"
```

---

### Task 4: 第 11-15 页 — 知识资产

**Files:**
- Modify: `presentation/slides.html` (追加 5 个 `<section>`)

**关键页面**:

**第 11 页 · 10篇论文卡片矩阵 (`.card-grid.cols-5`)**:

```html
<section class="slide" id="s11">
  <div class="section-tag">知识资产 · 论文总览</div>
  <h1 class="slide-title">10 篇论文：五条路线的科学地基</h1>
  <div class="content" style="gap:6px;">
    <div class="card-grid cols-5" style="gap:8px;">
      <!-- 第一行 -->
      <div class="card route-d2"><div class="card-tag">综述框架</div><div class="card-header" style="font-size:11pt;">PAPER-002</div><div class="card-body" style="font-size:10pt;">杨华明 2023<br>材料导报<br>~90篇参考文献</div></div>
      <div class="card route-d3"><div class="card-tag">热演化基础</div><div class="card-header" style="font-size:11pt;">PAPER-005</div><div class="card-body" style="font-size:10pt;">Meng 2022<br>Minerals (SCI)<br>15个温度点</div></div>
      <div class="card route-d3"><div class="card-tag">N₂碳石墨烯</div><div class="card-header" style="font-size:11pt;">PAPER-006</div><div class="card-body" style="font-size:10pt;">吴小文 2017<br>陶瓷学报<br>抗弯+43%</div></div>
      <div class="card route-d2"><div class="card-tag">D2基础陶瓷</div><div class="card-header" style="font-size:11pt;">PAPER-004</div><div class="card-body" style="font-size:10pt;">刘子峥 2024<br>电子元件与材料<br>Q×f=56,782</div></div>
      <div class="card route-d2"><div class="card-tag">成本突破</div><div class="card-header" style="font-size:11pt;">PAPER-008</div><div class="card-body" style="font-size:10pt;">Xiao 2025<br>Ceramics Int. (Q1)<br>成本降80%</div></div>
    </div>
    <div class="card-grid cols-5" style="gap:8px;">
      <!-- 第二行 -->
      <div class="card route-d2"><div class="card-tag">低温烧结</div><div class="card-header" style="font-size:11pt;">PAPER-009</div><div class="card-body" style="font-size:10pt;">Bu 2025<br>Ceramics Int. (Q1)<br>仅1075°C</div></div>
      <div class="card route-d2"><div class="card-tag">Cu掺杂稳相</div><div class="card-header" style="font-size:11pt;">PAPER-010</div><div class="card-body" style="font-size:10pt;">Fang 2024<br>Ceramics Int. (Q1)<br>Q×f=93,600</div></div>
      <div class="card route-d2"><div class="card-tag">Co掺杂高Qf</div><div class="card-header" style="font-size:11pt;">PAPER-011</div><div class="card-body" style="font-size:10pt;">Ullah 2019<br>J Mater Sci (SCI)<br>Q×f=145,846</div></div>
      <div class="card route-d4"><div class="card-tag">Zn晶格重建</div><div class="card-header" style="font-size:11pt;">PAPER-003</div><div class="card-body" style="font-size:10pt;">裘林莉 2017<br>硅酸盐通报<br>Mg²⁺溶出352</div></div>
      <div class="card route-d9"><div class="card-tag">酸浸突破</div><div class="card-header" style="font-size:11pt;">PAPER-007</div><div class="card-body" style="font-size:10pt;">Huang 2025<br>Minerals Eng. (Q1)<br>Mg浸出97.98%</div></div>
    </div>
    <div style="text-align:center;font-size:11pt;color:#6b7280;margin-top:8px;">
      期刊分布: 5篇 SCI Q1 + 1篇 SCI + 4篇中文核心 &nbsp;|&nbsp; 年份跨度: 2017&ndash;2025 &nbsp;|&nbsp; 路线覆盖: D1&ndash;D9 全覆盖
    </div>
  </div>
  <div class="slide-footer"><span>来源: papers/SYNERGY-NETWORK-REPORT.md</span><span>11 / 44</span></div>
</section>
```

**第 13 页 · 关联网络图 (inline SVG)**:

根据 spec §3.3 描述，使用 SVG 绘制节点-连线图：
- 中心：PAPER-002(综述)和 PAPER-005(热演化) → 连接所有实验论文
- D2 簇：PAPER-004→008→009→010↔011 用蓝色框
- D3+D4+D9 簇用另一区域

**第 12、14、15 页**遵循相同的数据表格/流程卡片/金字塔图模式，内容来自 spec。

- [ ] **Step 9: 写入第 11-15 页 HTML, 浏览器验证**

- [ ] **Step 10: Commit**

```bash
git add presentation/slides.html
git commit -m "feat: slides 11-15 knowledge assets chapter"
```

---

### Task 5: 第 16-33 页 — 初阶深讲（核心章节）

**Files:**
- Modify: `presentation/slides.html` (追加 18 个 `<section>`)

**18 页分布**:
- 第 16 页: 初阶总引 (四列卡片)
- 第 17-18 页: Phase 0a 文献综述 (表格 + 检索策略)
- 第 19-21 页: Phase 0b 数据再分析 (相图 + 数据表 + 论文定位)
- 第 22-25 页: Phase 0c 管式炉实验 (实验矩阵 + 增量创新 + 预算饼图 + 预期结果)
- 第 26-27 页: Phase 0d 专利申请 (技术流程 + 专利格局)
- 第 28-29 页: 时间线 (甘特图 + 路线图)
- 第 30-31 页: 企业合作 + 风险矩阵
- 第 32-33 页: 成果检验 + 身份转换

**关键页面代码示例**:

**第 16 页 · 初阶总引 (`.card-grid.cols-4`)**:

```html
<section class="slide" id="s16">
  <div class="section-tag">初阶方案 · 总览</div>
  <h1 class="slide-title">初阶方案：现在就能启动的四个阶段</h1>
  <div class="card-grid cols-4" style="flex:1;">
    <div class="card" style="border-top:3px solid var(--deep-blue);"><div class="card-tag">Phase 0a</div><div class="card-header">文献综述</div><div class="card-body">预算 <span class="data-highlight" style="font-size:16pt;">¥0</span><br>时间 1-2月<br><br>产出: 综述论文初稿<br>目标期刊: 材料导报/硅酸盐通报</div></div>
    <div class="card" style="border-top:3px solid #3b82f6;"><div class="card-tag">Phase 0b</div><div class="card-header">数据二次分析</div><div class="card-body">预算 <span class="data-highlight" style="font-size:16pt;">¥0</span><br>时间 1月<br><br>产出: 温度-气氛-产物相图论文<br>类型: Data Re-analysis</div></div>
    <div class="card" style="border-top:3px solid #10b981;"><div class="card-tag">Phase 0c</div><div class="card-header">管式炉验证实验</div><div class="card-body">预算 <span class="data-highlight" style="font-size:16pt;">¥5,000</span><br>时间 2-3月<br><br>产出: Raman增量实验论文<br>目标期刊: Ceramics Int.</div></div>
    <div class="card" style="border-top:3px solid var(--amber);"><div class="card-tag">Phase 0d</div><div class="card-header">专利申请</div><div class="card-body">预算 <span class="data-highlight" style="font-size:16pt;">¥3,000</span><br>时间 1-2月<br><br>产出: 1项发明专利<br>D3方向无现有专利覆盖</div></div>
  </div>
  <div style="text-align:center;margin-top:16px;font-size:14pt;">
    总预算: <span class="data-highlight" style="font-size:22pt;">~8,000 元</span> &nbsp;|&nbsp;
    时间: <span class="data-highlight">1-2 学期</span> &nbsp;|&nbsp;
    总产出: <span class="data-highlight">3 篇论文 + 1 项发明专利</span>
  </div>
  <div class="slide-footer"><span>核心策略: D3(N₂碳石墨烯)为旗帜 + D1(科学煅烧)为保底</span><span>16 / 44</span></div>
</section>
```

**第 24 页 · 预算饼图 (SVG pie chart)**:

```html
<section class="slide" id="s24">
  <div class="section-tag">初阶方案 · Phase 0c</div>
  <h1 class="slide-title">Phase 0c：预算 ¥5,000 怎么分配</h1>
  <div class="two-col">
    <div class="col-left" style="align-items:center;">
      <svg viewBox="0 0 300 300" style="width:280px;">
        <!-- 饼图扇区: 管式炉40%→144°, Raman24%→86.4°, N₂16%→57.6°, 原料10%→36°, XRD10%→36° -->
        <circle cx="150" cy="150" r="120" fill="none" stroke="#1a365d" stroke-width="60"
          stroke-dasharray="301.6 452.4" stroke-dashoffset="0" transform="rotate(-90 150 150)"/>
        <circle cx="150" cy="150" r="120" fill="none" stroke="#3b82f6" stroke-width="60"
          stroke-dasharray="181.0 573.0" stroke-dashoffset="-301.6" transform="rotate(-90 150 150)"/>
        <circle cx="150" cy="150" r="120" fill="none" stroke="#10b981" stroke-width="60"
          stroke-dasharray="120.6 633.4" stroke-dashoffset="-482.6" transform="rotate(-90 150 150)"/>
        <circle cx="150" cy="150" r="120" fill="none" stroke="#f59e0b" stroke-width="60"
          stroke-dasharray="75.4 678.6" stroke-dashoffset="-603.2" transform="rotate(-90 150 150)"/>
        <circle cx="150" cy="150" r="120" fill="none" stroke="#8b5cf6" stroke-width="60"
          stroke-dasharray="75.4 678.6" stroke-dashoffset="-678.6" transform="rotate(-90 150 150)"/>
        <text x="150" y="145" text-anchor="middle" font-family="var(--font-mono)" font-size="18" font-weight="700" fill="var(--deep-blue)">¥5,000</text>
        <text x="150" y="165" text-anchor="middle" font-size="11" fill="#6b7280">总计</text>
      </svg>
    </div>
    <div class="col-right">
      <table class="data-table">
        <tr><th>项目</th><th>金额</th><th>占比</th><th>说明</th></tr>
        <tr><td>管式炉使用费</td><td class="data-highlight">¥2,000</td><td>40%</td><td>若学校有则仅电费; 按外协机时计</td></tr>
        <tr><td>Raman 测试 ×8</td><td class="data-highlight">¥1,200</td><td>24%</td><td>校外 ~¥150/样</td></tr>
        <tr><td>N₂ 气瓶 ×2</td><td class="data-highlight">¥800</td><td>16%</td><td>高纯 99.999%, 40L</td></tr>
        <tr><td>黑滑石原料</td><td class="data-highlight">¥500</td><td>10%</td><td>网购/矿区寄送 5kg</td></tr>
        <tr><td>XRD 测试</td><td class="data-highlight">¥500</td><td>10%</td><td>若学校有则免费</td></tr>
      </table>
    </div>
  </div>
  <div class="slide-footer"><span>数据来源: tier-1-entry-level.md §3.3</span><span>24 / 44</span></div>
</section>
```

**第 28 页 · 甘特图 (CSS bar chart)**:

```html
<section class="slide" id="s28">
  <div class="section-tag">初阶方案 · 时间线</div>
  <h1 class="slide-title">Phase 0 总览：8 个月 · 4 项产出</h1>
  <div class="content" style="justify-content:center;">
    <svg viewBox="0 0 1050 360" style="width:100%;max-height:340px;">
      <!-- 月份标题 -->
      <text x="200" y="24" font-size="11" fill="#6b7280" text-anchor="middle">1月</text>
      <text x="300" y="24" font-size="11" fill="#6b7280" text-anchor="middle">2月</text>
      <text x="400" y="24" font-size="11" fill="#6b7280" text-anchor="middle">3月</text>
      <text x="500" y="24" font-size="11" fill="#6b7280" text-anchor="middle">4月</text>
      <text x="600" y="24" font-size="11" fill="#6b7280" text-anchor="middle">5月</text>
      <text x="700" y="24" font-size="11" fill="#6b7280" text-anchor="middle">6月</text>
      <text x="800" y="24" font-size="11" fill="#6b7280" text-anchor="middle">7月</text>
      <text x="900" y="24" font-size="11" fill="#6b7280" text-anchor="middle">8月</text>
      <!-- Phase 0a -->
      <text x="160" y="60" font-size="12" fill="var(--deep-blue)" font-weight="600" text-anchor="end">Phase 0a</text>
      <rect x="180" y="48" width="180" height="24" rx="4" fill="var(--deep-blue)" opacity="0.8"/>
      <text x="270" y="64" font-size="10" fill="white" text-anchor="middle">文献综述</text>
      <!-- Phase 0b -->
      <text x="160" y="110" font-size="12" fill="#3b82f6" font-weight="600" text-anchor="end">Phase 0b</text>
      <rect x="280" y="98" width="120" height="24" rx="4" fill="#3b82f6" opacity="0.8"/>
      <text x="340" y="114" font-size="10" fill="white" text-anchor="middle">数据再分析</text>
      <!-- Phase 0c -->
      <text x="160" y="160" font-size="12" fill="#10b981" font-weight="600" text-anchor="end">Phase 0c</text>
      <rect x="330" y="148" width="330" height="24" rx="4" fill="#10b981" opacity="0.8"/>
      <text x="495" y="164" font-size="10" fill="white" text-anchor="middle">管式炉验证实验</text>
      <!-- Phase 0d -->
      <text x="160" y="210" font-size="12" fill="var(--amber)" font-weight="600" text-anchor="end">Phase 0d</text>
      <rect x="530" y="198" width="220" height="24" rx="4" fill="var(--amber)" opacity="0.8"/>
      <text x="640" y="214" font-size="10" fill="white" text-anchor="middle">专利申请</text>
      <!-- 产出标注 -->
      <text x="270" y="270" font-size="10" fill="var(--deep-blue)" text-anchor="middle">综述初稿</text>
      <text x="340" y="290" font-size="10" fill="#3b82f6" text-anchor="middle">相图论文</text>
      <text x="495" y="270" font-size="10" fill="#10b981" text-anchor="middle">Raman实验论文</text>
      <text x="640" y="290" font-size="10" fill="var(--amber)" text-anchor="middle">发明专利 ×1</text>
    </svg>
  </div>
  <div class="slide-footer"><span>来源: tier-1-entry-level.md §3.5</span><span>28 / 44</span></div>
</section>
```

**其余 14 页**遵循已建立的模式：表格页用 `.data-table`，卡片页用 `.card-grid`，对比页用 `.two-col`，信息图用 inline SVG，内容严格来自 spec §3.4。

- [ ] **Step 11: 写入第 16-33 页 HTML, 浏览器验证**

- [ ] **Step 12: Commit**

```bash
git add presentation/slides.html
git commit -m "feat: slides 16-33 entry-level deep dive chapter (18 slides)"
```

---

### Task 6: 第 34-44 页 — 中阶简览 + 高阶简览 + 收尾

**Files:**
- Modify: `presentation/slides.html` (追加 11 个 `<section>`)

**11 页分布**:
- 第 34-38 页: 中阶简览 (总引/掺杂对比/双旗舰/财务/触发条件)
- 第 39-41 页: 高阶简览 (愿景/原料分级/路线协同)
- 第 42-44 页: 收尾 (行动清单/讨论问题/致谢)

**关键页面**: 第 35 页掺杂对比表, 第 40 页原料分级树状图, 第 44 页致谢 (`slide-dark`)。

- [ ] **Step 13: 写入第 34-44 页 HTML, 浏览器验证**

- [ ] **Step 14: Commit**

```bash
git add presentation/slides.html
git commit -m "feat: slides 34-44 mid/high tier overview + closing chapter"
```

---

### Task 7: 导航系统 + 进度条

**Files:**
- Modify: `presentation/slides.html` (追加 JS 键盘导航)

- [ ] **Step 15: 添加键盘导航和进度条**

在 `</body>` 前追加:

```html
<script>
(function() {
  const slides = document.querySelectorAll('.slide');
  let current = 0;
  const total = slides.length;

  // 进度条
  const bar = document.createElement('div');
  bar.style.cssText = 'position:fixed;top:0;left:0;height:3px;background:var(--amber);z-index:9999;transition:width 0.25s ease;';
  document.body.appendChild(bar);

  function goTo(idx) {
    if (idx < 0 || idx >= total) return;
    current = idx;
    slides[current].scrollIntoView({ behavior: 'smooth' });
    bar.style.width = ((current + 1) / total * 100) + '%';
    // 更新 URL hash
    history.replaceState(null, null, '#' + (current + 1));
  }

  // 键盘导航
  document.addEventListener('keydown', function(e) {
    if (e.key === 'ArrowRight' || e.key === 'ArrowDown' || e.key === ' ') {
      e.preventDefault();
      goTo(current + 1);
    } else if (e.key === 'ArrowLeft' || e.key === 'ArrowUp') {
      e.preventDefault();
      goTo(current - 1);
    } else if (e.key === 'Home') {
      e.preventDefault();
      goTo(0);
    } else if (e.key === 'End') {
      e.preventDefault();
      goTo(total - 1);
    }
  });

  // 点击左右区域翻页
  document.addEventListener('click', function(e) {
    const x = e.clientX;
    const w = window.innerWidth;
    if (x < w * 0.25) goTo(current - 1);
    else if (x > w * 0.75) goTo(current + 1);
  });

  // 触摸滑动
  let touchStartX = 0;
  document.addEventListener('touchstart', function(e) { touchStartX = e.touches[0].clientX; });
  document.addEventListener('touchend', function(e) {
    const dx = e.changedTouches[0].clientX - touchStartX;
    if (dx > 60) goTo(current - 1);
    else if (dx < -60) goTo(current + 1);
  });

  // 渲染当前页码
  function updatePageNumbers() {
    slides.forEach(function(s, i) {
      s.setAttribute('data-page', (i + 1) + ' / ' + total);
    });
  }
  updatePageNumbers();
  goTo(0);
})();
</script>
```

- [ ] **Step 16: 测试键盘导航, Click翻页, 触摸滑动, 进度条更新**

- [ ] **Step 17: Commit**

```bash
git add presentation/slides.html
git commit -m "feat: keyboard navigation + progress bar + touch support"
```

---

### Task 8: 打磨轮次 1 — 字体层级与留白节奏

**Files:**
- Modify: `presentation/slides.html` (CSS 调整)

**检查点**:
1. 所有 44 页的标题字号是否在 28-32pt 范围内一致
2. 正文 16pt 可读性 — 在 1280×720 视口下是否够大
3. 卡片/表格内部 padding 是否统一（12-16px）
4. 留白间距 — 页面内容区上下边距是否呼吸感足够
5. 思源字体 fallback — 如果用户电脑无思源字体，Microsoft YaHei / SimSun 的表现

- [ ] **Step 18: 逐页检查字体层级一致性**

使用浏览器 DevTools 逐页查看 computed font-size，统一所有 `.slide-title` 为 28pt，所有 `.card-header` 为 15pt。

- [ ] **Step 19: 调整全局留白**

将 `.slide` 的 padding 从 `48px 64px 36px 64px` 调整为 `52px 72px 40px 72px` (增大留白让页面更舒展)。

- [ ] **Step 20: 添加字体 fallback 测试**

在 CSS `:root` 的 `--font-title` 和 `--font-body` 中确认 fallback 链完整。

- [ ] **Step 21: Commit**

```bash
git add presentation/slides.html
git commit -m "polish: typography consistency + whitespace rhythm round 1"
```

---

### Task 9: 学术会议 PPT 参考研究

**无需修改代码，研究成果指导后续打磨**

- [ ] **Step 22: 搜索学术会议 PPT 排版参考**

用 WebSearch 搜索以下关键词，收集 2-3 份高质量学术 PPT 的排版特征：

```
"MRS fall meeting presentation template" 
"Materials Research Society slides example"
"全国高技术陶瓷学术年会 PPT 模板"
" academic conference presentation slide design materials science"
```

- [ ] **Step 23: 提炼排版规则**

从收集到的参考中提炼 10 条可直接应用的排版规则，记录到 `presentation/DESIGN-NOTES.md`。重点关注：
- 数据图的标注字体大小和颜色
- 表格的线宽和灰阶
- 标题与正文的字号比例
- 学术 PPT 中色彩的克制使用

- [ ] **Step 24: 对比当前幻灯片与参考标准的差距**

列出具体的不符合项清单（如 "表格线太粗"、"数据标签太小"）。

- [ ] **Step 25: Commit**

```bash
git add presentation/DESIGN-NOTES.md
git commit -m "docs: academic PPT design reference notes"
```

---

### Task 10: 打磨轮次 2 — 色板微调与图表精致化

**Files:**
- Modify: `presentation/slides.html`

**基于 Task 9 的研究结果进行调整**:

- [ ] **Step 26: 色板微调**

根据学术 PPT 参考标准，将色板做如下检查和调整：
- 深蓝 `#1a365d` 是否过深 → 可能调整到 `#1e3a5f` (稍微柔和)
- 强调色琥珀 `#d97706` 在投影仪上的可见性 — 可能需要略微提亮
- 表格奇偶行底色交替（白/浅灰）增加可读性

- [ ] **Step 27: SVG 图表精致化**

检查所有 inline SVG 图表:
- 线宽统一 (主要线 1.5px, 辅助线 0.75px)
- 文字大小统一 (图表标签 10pt, 数据标注 11pt)
- 颜色与 CSS 变量一致
- 饼图扇区顺序从大到小排列

- [ ] **Step 28: 占位框美化**

调整 `.placeholder` 样式:
- 添加居中的相机图标 (CSS 绘制)
- 虚线间距调整为 6px
- 增加 hover 时的微弱高亮 (演示时鼠标悬停提示)

- [ ] **Step 29: Commit**

```bash
git add presentation/slides.html
git commit -m "polish: color refinement + SVG chart polish + placeholder enhancement round 2"
```

---

### Task 11: 最终打磨 + 导出 PDF 测试

**Files:**
- Modify: `presentation/slides.html` (最终微调)

- [ ] **Step 30: 逐页自检清单**

对全部 44 页执行逐页检查:
1. 标题无错别字
2. PAPER-XXX 编号正确
3. 占位框标注完整（来源 + PDF位置%）
4. 页脚页码连续
5. 章节标签正确
6. 无装饰性 emoji

- [ ] **Step 31: 打印导出 PDF 测试**

```bash
# 在浏览器中打开, 使用 Cmd/Ctrl+P → 另存为 PDF
# 检查: 每页是否完整显示, 图表是否截断, 颜色是否正确
```

如 PDF 输出有问题，添加 `@media print` 样式:

```css
@media print {
  @page { size: 1280px 720px; margin: 0; }
  .slide { page-break-after: always; box-shadow: none; margin-bottom: 0; }
  body { background: white; }
}
```

- [ ] **Step 32: Commit**

```bash
git add presentation/slides.html
git commit -m "polish: final page-by-page audit + print styles"
```

---

### Task 12: python-pptx 迁移脚本

**Files:**
- Create: `presentation/export_to_pptx.py`

**Interfaces:**
- Consumes: `presentation/slides.html` 中确定的设计参数（色板、字号、布局）
- Produces: `presentation/advisor-presentation.pptx`

- [ ] **Step 33: 安装 python-pptx**

```bash
pip install python-pptx
```

- [ ] **Step 34: 编写迁移脚本**

```python
"""将 HTML 幻灯片的设计参数迁移到 PPTX 文件。

此脚本不解析 HTML，而是直接使用 HTML 中确定的设计参数。
用户需要手动将论文截图插入到对应占位框中。
所有占位框在 PPTX 中以文本框标注来源 + PDF 位置百分比。
"""

from pptx import Presentation
from pptx.util import Inches, Pt, Emu
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN
import os

# ---- 设计参数（与 slides.html CSS 变量一致）----
DEEP_BLUE = RGBColor(0x1A, 0x36, 0x5D)
AMBER = RGBColor(0xD9, 0x77, 0x06)
GRAPHITE = RGBColor(0x37, 0x41, 0x51)
LIGHT_GRAY = RGBColor(0xE5, 0xE7, 0xEB)
TITANIUM = RGBColor(0xF7, 0xF8, 0xFA)

SLIDE_W = Inches(13.333)  # 16:9
SLIDE_H = Inches(7.5)

FONT_TITLE = 'Source Han Sans SC'
FONT_BODY = 'Source Han Serif SC'
FONT_MONO = 'JetBrains Mono'

TITLE_SIZE = Pt(28)
BODY_SIZE = Pt(16)
SMALL_SIZE = Pt(10)
TAG_SIZE = Pt(8)

# ---- 幻灯片结构定义 ----
# 每页: (章节标签, 页面标题, 类型, 内容描述, 占位框列表)
# 类型: 'title' | 'two-col' | 'cards' | 'table' | 'svg-chart' | 'cover' | 'dark' | 'timeline' | 'list'

SLIDES = [
    # === 开篇 (1-5) ===
    (1, "汇报主题", "黑滑石高值化商业化初步研究汇报", "cover",
     "从10亿吨低品位资源到5条技术路线",
     [("背景图", "广丰黑滑石矿区全景", "")]),

    (2, "汇报提纲", "汇报提纲", "list",
     "01-06 六个章节目录",
     []),

    (3, "开篇 · 背景", "黑滑石：被低估的 10 亿吨", "two-col",
     "左：原矿照片占位 | 右：矿物学身份卡片",
     [("黑滑石原矿手标本", "PAPER-005 Meng 2022 Fig.1", "PDF 约 15% 位置")]),

    (4, "开篇 · 问题", "核心矛盾：为什么10亿吨堆在那里？", "two-col",
     "左：当前困境 | 右：新视角——碳不是杂质",
     []),

    (5, "开篇 · 路线全景", "五条技术路线：覆盖从低到高的阶梯", "svg-chart",
     "SVG 流程图：黑滑石→D1/D2/D3/D4/D9",
     []),

    # === 痛点即机会 (6-10) ===
    (6, "痛点即机会 · 现状", "广丰黑滑石：储量 vs 价值的巨大落差", "two-col",
     "左：矿区地图占位 | 右：数据卡片(储量/品位/售价)",
     [("广丰矿区地理位置", "Google Earth截图", ""),
      ("XRF成分表", "PAPER-005 Meng 2022 Table 1", "PDF 约 20% 位置")]),

    (7, "痛点即机会 · 认知", "碳：从杂质到资源的认知翻转", "svg-chart",
     "分叉对比图：空气煅烧 vs N₂气氛",
     []),

    (8, "痛点即机会 · 科学基础", "黑滑石热演化：PAPER-005 Meng 的核心发现", "two-col",
     "左：TG-DSC+In-situ XRD占位 | 右：四阶段SVG示意图",
     [("TG-DSC曲线", "PAPER-005 Meng 2022 Fig.2", "PDF 约 35% 位置"),
      ("In-situ XRD", "PAPER-005 Meng 2022 Fig.6", "PDF 约 60% 位置")]),

    (9, "痛点即机会 · 验证", "N₂ vs Air：同一块矿石的两种命运", "two-col",
     "左：性能对比柱状图SVG | 右：机理说明+TEM占位",
     [("N₂ vs Air 性能对比数据", "PAPER-006 吴小文 2017 Fig.3-5", "PDF 约 45-55% 位置"),
      ("TEM石墨烯高分辨像", "PAPER-006 吴小文 2017", "PDF 约 70% 位置")]),

    (10, "痛点即机会 · 总结", "三个科学事实指向一个商业机会", "svg-chart",
     "三圆汇聚图：储量 × 热演化 × N₂石墨烯化 → 功能填料产业化",
     []),

    # === 知识资产 (11-15) ===
    (11, "知识资产 · 论文总览", "10篇论文：五条路线的科学地基", "cards",
     "2行×5列 论文卡片矩阵",
     []),

    (12, "知识资产 · 数据快照", "从论文中提取的核心数据", "table",
     "按路线分组的数据表格",
     []),

    (13, "知识资产 · 关联网络", "25条论文间关联：知识不是孤岛", "svg-chart",
     "SVG 节点-连线图",
     []),

    (14, "知识资产 · D2深度", "D2 路线：五篇论文构成完整技术链", "svg-chart",
     "流程卡片：基础→成本→低温→掺杂→共掺杂",
     []),

    (15, "知识资产 · 金字塔", "知识资产的三个层次", "svg-chart",
     "三层金字塔：科学地基→综述框架→应用验证",
     []),

    # === 初阶深讲 (16-33) ===
    (16, "初阶方案 · 总览", "初阶方案：现在就能启动的四个阶段", "cards",
     "四列卡片：Phase 0a/0b/0c/0d",
     []),

    (17, "初阶方案 · Phase 0a", "Phase 0a：文献综述 · 站在10篇论文的肩膀上", "table",
     "5篇可直接引用的核心论文 + 综述章节 + 关键引用数据",
     []),

    (18, "初阶方案 · Phase 0a", "Phase 0a：系统检索策略", "list",
     "中英文检索式 + 目标期刊 + 预期产出",
     []),

    (19, "初阶方案 · Phase 0b", "Phase 0b：温度-气氛-产物 三位一体相图", "two-col",
     "左：论文截图占位 | 右：空气vs N₂对比相图",
     [("TG-DSC曲线", "PAPER-005 Meng 2022 Fig.2", "PDF 约 35% 位置"),
      ("In-situ XRD", "PAPER-005 Meng 2022 Fig.6", "PDF 约 60% 位置"),
      ("性能对比数据", "PAPER-006 吴小文 2017", "PDF 约 50% 位置")]),

    (20, "初阶方案 · Phase 0b", "Phase 0b：从已有论文提取的10组定量数据", "table",
     "数据点 / 来源 / 用于相图哪个部分",
     []),

    (21, "初阶方案 · Phase 0b", "Phase 0b：这篇论文的创新点在哪？", "two-col",
     "左：已有论文做了什么 | 右：我们的论文贡献什么",
     []),

    (22, "初阶方案 · Phase 0c", "Phase 0c：管式炉验证实验", "two-col",
     "左：实验矩阵(4温度×3N₂流量)SVG | 右：参数表",
     [("管式炉设备照片", "学校实验室实拍", ""),
      ("黑滑石200目粉体照片", "自拍", "")]),

    (23, "初阶方案 · Phase 0c", "Phase 0c：三个增量创新 — PAPER-006 没做过的", "cards",
     "三列卡片：Raman ID/IG定量 / N₂流量梯度 / 碳含量关联",
     []),

    (24, "初阶方案 · Phase 0c", "Phase 0c：预算 ¥5,000 怎么分配", "two-col",
     "左：饼图SVG | 右：分类说明表格",
     []),

    (25, "初阶方案 · Phase 0c", "Phase 0c：预期结果与论文规划", "two-col",
     "左：预期结果列表 | 右：论文结构 + 目标期刊",
     [("ID/IG vs Temperature 预期趋势", "文献参考", "碳材料Raman典型S曲线"),
      ("电阻率 vs Temperature 预期趋势", "文献参考", "percolation曲线")]),

    (26, "初阶方案 · Phase 0d", "Phase 0d：发明专利申请", "two-col",
     "左：技术方案流程图 | 右：三个创新点",
     []),

    (27, "初阶方案 · Phase 0d", "Phase 0d：现有专利格局 — 我们的位置", "table",
     "已有专利列表 + D3方向空白高亮",
     []),

    (28, "初阶方案 · 时间线", "Phase 0 总览：8个月 · 4项产出", "svg-chart",
     "甘特图",
     []),

    (29, "初阶方案 · 路线图", "初阶路线图：从文献到企业验证的完整路径", "svg-chart",
     "四学期时间线",
     []),

    (30, "初阶方案 · 企业合作", "如何找到第一个合作企业", "list",
     "企业画像 + 接触渠道 + Phase 1 企业投入",
     [("广丰煅烧厂照片", "百度街景/实地拍摄", ""),
      ("广丰区标注地图", "百度地图截图", "")]),

    (31, "初阶方案 · 风险", "初阶风险矩阵：每件事的 Plan B", "table",
     "5项风险 × (概率/影响/应对)",
     []),

    (32, "初阶方案 · 检验", "初阶完成标准：什么时候可以进入中阶？", "svg-chart",
     "四道门递进图",
     []),

    (33, "初阶方案 · 身份", "初阶完成后的身份转换", "two-col",
     "左：现在的身份 | 右：初阶完成后的身份",
     []),

    # === 中阶简览 (34-38) ===
    (34, "中阶方案 · 总引", "中阶方案：从课题组到产学研合作", "two-col",
     "定位过渡：初阶→中阶升级",
     []),

    (35, "中阶方案 · 掺杂", "中阶核心决策：D2 路线选哪种掺杂？", "table",
     "5种掺杂方案对比表 + 推荐Cu+Co共掺杂",
     [("Q×f vs τf 散点图", "PAPER-010 Fig.7 + PAPER-011 Fig.8", "PDF 后半部分")]),

    (36, "中阶方案 · 双旗舰", "中阶双旗舰：D3 先盈利，D2 建壁垒", "svg-chart",
     "双通道时间线 D3(24月) + D2(30月)",
     []),

    (37, "中阶方案 · 财务", "中阶经济模型概要", "table",
     "D3 vs D2: CAPEX/产能/单价/营收/毛利率",
     []),

    (38, "中阶方案 · 触发", "中阶关键风险与进入条件", "list",
     "四条触发信号 + 关键风险",
     []),

    # === 高阶简览 (39-41) ===
    (39, "高阶方案 · 愿景", "高阶方案：产学研联合体的全产业链整合", "list",
     "五线全线启动 · CAPEX ~5.5亿 · 年营收 ~15亿",
     []),

    (40, "高阶方案 · 分级", "原料分级：同一座矿，五种产品", "svg-chart",
     "树状分配图：矿料→5%/20%/10%/50%/15%→5条路线",
     [("XRF对比表", "PAPER-005 Table 1 + PAPER-007 Table 1", "PDF 前 15% 位置")]),

    (41, "高阶方案 · 协同", "五条路线的协同效应", "svg-chart",
     "流程图：废弃物互消化 · 综合成本降35-40%",
     []),

    # === 收尾 (42-44) ===
    (42, "收尾 · 行动", "下一步行动：本周就能开始的四件事", "list",
     "立即/短期/中期 三层级行动清单",
     []),

    (43, "收尾 · 讨论", "希望得到导师指导的四个问题", "list",
     "设备/企业/路线/研究生参与",
     []),

    (44, "收尾 · 致谢", "感谢导师的宝贵时间", "dark",
     "致谢页 · 矿区远景照片 · 底部文字",
     [("矿区远景", "广丰矿区或江西丘陵地貌风景照", "")]),
]


def create_presentation():
    prs = Presentation()
    prs.slide_width = SLIDE_W
    prs.slide_height = SLIDE_H

    # 使用空白版式
    blank_layout = prs.slide_layouts[6]  # blank

    for page_num, section_tag, title, slide_type, desc, placeholders in SLIDES:
        slide = prs.slides.add_slide(blank_layout)

        # 设置背景色
        bg = slide.background
        fill = bg.fill
        fill.solid()
        if slide_type in ('cover', 'dark'):
            fill.fore_color.rgb = DEEP_BLUE
        else:
            fill.fore_color.rgb = TITANIUM

        # 章节标签 (左上)
        tag_box = slide.shapes.add_textbox(Inches(0.8), Inches(0.3), Inches(4), Inches(0.3))
        tf = tag_box.text_frame
        tf.text = f"▎{section_tag}"
        p = tf.paragraphs[0]
        p.font.size = TAG_SIZE
        p.font.color.rgb = AMBER
        p.font.name = FONT_TITLE

        # 页面标题
        title_box = slide.shapes.add_textbox(Inches(0.8), Inches(0.65), Inches(11.5), Inches(0.7))
        tf = title_box.text_frame
        tf.text = title
        tf.word_wrap = True
        p = tf.paragraphs[0]
        p.font.size = TITLE_SIZE
        p.font.bold = True
        p.font.name = FONT_TITLE
        if slide_type in ('cover', 'dark'):
            p.font.color.rgb = RGBColor(0xFF, 0xFF, 0xFF)
        else:
            p.font.color.rgb = DEEP_BLUE

        # 内容区占位 (简化处理: 用文本框标注内容和占位图)
        content_top = Inches(1.6)
        content_box = slide.shapes.add_textbox(Inches(0.8), content_top, Inches(11.5), Inches(5.0))
        tf = content_box.text_frame
        tf.word_wrap = True

        # 类型标识
        type_names = {
            'cover': '[封面页]', 'dark': '[暗底页]', 'two-col': '[双栏布局]',
            'cards': '[卡片矩阵]', 'table': '[数据表格]', 'svg-chart': '[SVG 图表]',
            'list': '[清单列表]', 'timeline': '[时间线]'
        }
        p = tf.paragraphs[0]
        p.text = f"{type_names.get(slide_type, '')} {desc}"
        p.font.size = BODY_SIZE
        p.font.name = FONT_BODY
        if slide_type in ('cover', 'dark'):
            p.font.color.rgb = RGBColor(0xE2, 0xE8, 0xF0)
        else:
            p.font.color.rgb = GRAPHITE

        # 占位框
        if placeholders:
            placeholder_top = Inches(2.8)
            for i, (ph_label, ph_source, ph_pos) in enumerate(placeholders):
                ph_box = slide.shapes.add_shape(
                    1,  # MSO_SHAPE.RECTANGLE
                    Inches(0.8), placeholder_top + Inches(i * 1.2),
                    Inches(5.5), Inches(1.0)
                )
                ph_box.fill.solid()
                ph_box.fill.fore_color.rgb = RGBColor(0xF9, 0xFA, 0xFB)
                ph_box.line.color.rgb = LIGHT_GRAY
                ph_box.line.width = Pt(1.5)
                ph_box.line.dash_style = 2  # dash

                tf = ph_box.text_frame
                tf.word_wrap = True
                p = tf.paragraphs[0]
                p.text = f"[图表占位] {ph_label}"
                p.font.size = Pt(13)
                p.font.name = FONT_TITLE
                p.font.color.rgb = RGBColor(0x9C, 0xA3, 0xAF)

                p2 = tf.add_paragraph()
                p2.text = f"来源: {ph_source}"
                p2.font.size = Pt(9)
                p2.font.name = FONT_BODY
                p2.font.color.rgb = RGBColor(0xB0, 0xB7, 0xC3)

                if ph_pos:
                    p3 = tf.add_paragraph()
                    p3.text = f"位置: {ph_pos}"
                    p3.font.size = Pt(9)
                    p3.font.name = FONT_BODY
                    p3.font.color.rgb = RGBColor(0xB0, 0xB7, 0xC3)

        # 页脚
        footer_top = Inches(7.0)
        footer_box = slide.shapes.add_textbox(Inches(0.8), footer_top, Inches(11.5), Inches(0.3))
        tf = footer_box.text_frame
        p = tf.paragraphs[0]
        p.text = f"{page_num} / 44"
        p.font.size = SMALL_SIZE
        p.font.name = FONT_BODY
        p.font.color.rgb = RGBColor(0x9C, 0xA3, 0xAF)
        p.alignment = PP_ALIGN.RIGHT

        # 页脚来源
        src_box = slide.shapes.add_textbox(Inches(0.8), footer_top, Inches(8), Inches(0.3))
        tf = src_box.text_frame
        p = tf.paragraphs[0]
        p.text = f"数据来源: tier-1-entry-level.md + 对应论文分析报告"
        p.font.size = SMALL_SIZE
        p.font.name = FONT_BODY
        p.font.color.rgb = RGBColor(0x9C, 0xA3, 0xAF)

    # 保存
    output_path = os.path.join(os.path.dirname(__file__), 'advisor-presentation.pptx')
    prs.save(output_path)
    print(f"PPTX saved to: {output_path}")
    print(f"Total slides: {len(prs.slides)}")
    return output_path


if __name__ == '__main__':
    create_presentation()
```

- [ ] **Step 35: 运行脚本并验证输出**

```bash
cd presentation
python export_to_pptx.py
# 验证: 44 页, 每页有章节标签/标题/内容描述/占位框/页脚
```

- [ ] **Step 36: Commit**

```bash
git add presentation/export_to_pptx.py presentation/advisor-presentation.pptx
git commit -m "feat: python-pptx migration script + initial .pptx output"
```

---

### Task 13: Code Review + 修复

**Files:**
- Review: `presentation/slides.html`
- Review: `presentation/export_to_pptx.py`

**Review 检查清单**:

- [ ] **Step 37: HTML/CSS 代码质量**

1. HTML 结构: 所有标签闭合正确, 语义化 section 使用
2. CSS: 是否有多余/重复的样式定义, CSS 变量是否全部被使用
3. Inline SVG: viewBox 是否正确, 文字是否可读
4. 无障碍: 标题层级是否合理 (每个 slide 有 h1 标题)
5. 响应式: 在小屏幕上 slide 是否 scale 正确 (或至少有 min-width 保护)
6. 性能: 44 个 SVG 是否影响滚动流畅度

- [ ] **Step 38: Python 代码质量**

1. python-pptx 脚本: 所有 slide_type 是否都有处理
2. 颜色映射: RGBColor 值是否与 CSS 变量一致
3. 占位框: 12 个论文占位框是否都正确标注
4. 异常处理: 文件保存路径是否存在/可写

- [ ] **Step 39: 修复发现的问题**

逐项修复后运行验证。

- [ ] **Step 40: 最终 Commit**

```bash
git add presentation/slides.html presentation/export_to_pptx.py
git commit -m "fix: code review fixes for slides.html + export_to_pptx.py"
```

---

## 完工标准

- [x] 44 页 HTML 幻灯片全部可渲染
- [x] 键盘/鼠标/触摸导航正常工作
- [x] 所有 12 项论文截图占位框标注完整（来源 + PDF位置%）
- [x] 学术会议标准排版（字体/色板/留白经过 2 轮打磨）
- [x] PDF 导出可用
- [x] python-pptx 迁移脚本可生成 44 页 .pptx
- [x] Code review 通过无遗留问题