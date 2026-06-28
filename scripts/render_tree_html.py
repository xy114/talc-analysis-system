#!/usr/bin/env python3
"""MgO-SiO₂(-C-H₂O) 体系树 — D3.js 交互式 HTML 渲染

用法:
  python scripts/render_tree_html.py                    # 默认输出
  python scripts/render_tree_html.py --output output/my-tree.html

输出:
  自包含 HTML 文件（内嵌 D3.js v7 CDN + CSS + JS）
  - 左侧: 可折叠树（点击节点展开/折叠）
  - 右侧: 节点详情面板（性质表 + 论文来源）
"""

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TREE_PATH = ROOT / "system-tree.json"
OUTPUT_DIR = ROOT / "output"

HTML_TEMPLATE = '''<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>黑滑石 MgO-SiO₂(-C-H₂O) 物相-应用体系树</title>
<script src="https://d3js.org/d3.v7.min.js"></script>
<style>
* { margin: 0; padding: 0; box-sizing: border-box; }
body { font-family: "Microsoft YaHei", "PingFang SC", sans-serif; background: #f8f9fa; display: flex; height: 100vh; }
#tree-panel { flex: 0 0 55%; overflow: auto; border-right: 1px solid #dee2e6; background: white; }
#detail-panel { flex: 1; overflow-y: auto; padding: 24px; background: #f8f9fa; }
#detail-panel h2 { margin-bottom: 12px; color: #2c3e50; font-size: 20px; }
#detail-panel .section { margin-bottom: 20px; }
#detail-panel .section h3 { color: #34495e; font-size: 15px; margin-bottom: 8px; border-bottom: 2px solid #3498db; padding-bottom: 4px; }
#detail-panel table { width: 100%; border-collapse: collapse; font-size: 13px; }
#detail-panel th { background: #34495e; color: white; padding: 6px 10px; text-align: left; font-weight: 500; }
#detail-panel td { padding: 6px 10px; border-bottom: 1px solid #dee2e6; }
#detail-panel tr:hover td { background: #e8f4f8; }
.tag { display: inline-block; padding: 2px 8px; border-radius: 3px; font-size: 11px; margin: 2px; }
.tag-raw { background: #2c3e50; color: white; }
.tag-phase { background: #bdc3c7; color: #2c3e50; }
.tag-product { background: #27ae60; color: white; }
.tag-byproduct { background: #95a5a6; color: white; }
.node circle { fill: #fff; stroke: #34495e; stroke-width: 2px; cursor: pointer; r: 7; }
.node.raw-material circle { fill: #2c3e50; stroke: #1a252f; r: 9; }
.node.intermediate-phase circle { fill: #ecf0f1; stroke: #34495e; }
.node.product circle { fill: #27ae60; stroke: #1e8449; stroke-width: 3px; }
.node.byproduct circle { fill: #95a5a6; stroke: #7f8c8d; }
.node text { font-size: 11px; font-family: "Microsoft YaHei", sans-serif; }
.link { fill: none; stroke: #bdc3c7; stroke-width: 1.5px; }
.link.process { stroke: #e74c3c; }
.link.property_link { stroke: #2980b9; stroke-dasharray: 6 3; }
.edge-label { font-size: 9px; fill: #7f8c8d; }
.empty-state { color: #95a5a6; text-align: center; margin-top: 60px; font-size: 16px; }
.paper-badge { display: inline-block; background: #3498db; color: white; padding: 1px 6px; border-radius: 3px; font-size: 11px; margin: 1px; }
.tree-header { position: absolute; top: 10px; left: 60px; font-size: 14px; color: #7f8c8d; }
</style>
</head>
<body>
<div id="tree-panel">
  <svg width="100%" height="100%"></svg>
</div>
<div id="detail-panel"><div class="empty-state">点击节点查看详情</div></div>
<script>
// ===== DATA =====
const TREE_DATA = __TREE_JSON__;
const EDGES_BY_TARGET = {};

(function() {
  const edges = TREE_DATA.edges || {};
  for (const [eid, edge] of Object.entries(edges)) {
    if (!EDGES_BY_TARGET[edge.to]) EDGES_BY_TARGET[edge.to] = [];
    EDGES_BY_TARGET[edge.to].push(edge);
  }
})();

// ===== BUILD HIERARCHY FROM TREE DATA =====
function buildHierarchy() {
  const nodes = TREE_DATA.nodes || {};
  const edges = TREE_DATA.edges || {};

  // Find root
  let rootId = null;
  for (const [id, node] of Object.entries(nodes)) {
    if (node.type === "raw_material") { rootId = id; break; }
  }
  if (!rootId) {
    for (const [id, node] of Object.entries(nodes)) {
      if (node.depth === 0) { rootId = id; break; }
    }
  }
  if (!rootId && Object.keys(nodes).length > 0) {
    rootId = Object.keys(nodes)[0];
  }

  if (!rootId) return null;

  function buildChildren(parentId) {
    const children = [];
    for (const [eid, edge] of Object.entries(edges)) {
      if (edge.from === parentId && nodes[edge.to]) {
        const child = Object.assign({}, nodes[edge.to]);
        child._incomingEdge = edge;
        child._incomingEdgeId = eid;
        child.children = buildChildren(edge.to);
        children.push(child);
      }
    }
    return children;
  }

  const root = Object.assign({}, nodes[rootId]);
  root._incomingEdge = null;
  root.children = buildChildren(rootId);
  return root;
}

// ===== RENDER TREE =====
const root = buildHierarchy();
if (!root) {
  document.getElementById("tree-panel").innerHTML =
    '<div class="empty-state" style="margin-top:120px;">树为空，请先通过 ingest.py 注册论文</div>';
} else {
  const svg = d3.select("#tree-panel svg");
  const g = svg.append("g").attr("transform", "translate(60, 60)");

  const treeLayout = d3.tree().size([window.innerHeight - 120, 0]);

  const hierarchy = d3.hierarchy(root);
  hierarchy.descendants().forEach(d => {
    // Horizontal spacing
    d._depth = d.depth;
  });

  // Set horizontal positions based on depth
  const maxDepth = d3.max(hierarchy.descendants(), d => d.depth) || 1;
  const panelWidth = () => document.getElementById("tree-panel").clientWidth;

  hierarchy.descendants().forEach(d => {
    d.y = (d.depth / Math.max(maxDepth, 1)) * (panelWidth() - 120);
  });

  const treeData = treeLayout(hierarchy);

  // Draw links
  const link = g.selectAll(".link")
    .data(treeData.links())
    .join("path")
    .attr("class", d => "link " + (d.target.data._incomingEdge ? d.target.data._incomingEdge.type : ""))
    .attr("d", d => {
      return "M" + d.source.y + "," + d.source.x
        + "C" + (d.source.y + d.target.y) / 2 + "," + d.source.x
        + " " + (d.source.y + d.target.y) / 2 + "," + d.target.x
        + " " + d.target.y + "," + d.target.x;
    });

  // Edge labels
  g.selectAll(".edge-label")
    .data(treeData.links())
    .join("text")
    .attr("class", "edge-label")
    .attr("x", d => (d.source.y + d.target.y) / 2)
    .attr("y", d => (d.source.x + d.target.x) / 2 - 8)
    .attr("text-anchor", "middle")
    .text(d => d.target.data._incomingEdge ? d.target.data._incomingEdge.label_short || "" : "");

  // Draw nodes
  const node = g.selectAll(".node")
    .data(treeData.descendants())
    .join("g")
    .attr("class", d => "node " + (d.data.type || ""))
    .attr("transform", d => `translate(${d.y},${d.x})`)
    .on("click", (event, d) => showDetail(d.data));

  node.append("circle");

  node.append("text")
    .attr("dy", "0.31em")
    .attr("x", d => d.children && d.children.length > 0 ? -12 : 12)
    .attr("text-anchor", d => d.children && d.children.length > 0 ? "end" : "start")
    .text(d => d.data.name || d.data.id || "")
    .clone(true).lower()
    .attr("stroke", "white").attr("stroke-width", 3);
}

// ===== DETAIL PANEL =====
function showDetail(nodeData) {
  const panel = document.getElementById("detail-panel");
  let html = "";

  const typeLabels = {
    raw_material: "原料",
    intermediate_phase: "中间物相",
    product: "产品",
    byproduct: "副产品"
  };
  const typeClass = {
    raw_material: "tag-raw",
    intermediate_phase: "tag-phase",
    product: "tag-product",
    byproduct: "tag-byproduct"
  };

  html += '<h2>' + (nodeData.name || nodeData.id) +
    ' <span class="tag ' + (typeClass[nodeData.type] || "tag-phase") + '">' +
    (typeLabels[nodeData.type] || nodeData.type) + '</span></h2>';

  if (nodeData.formula) {
    html += '<p style="color:#7f8c8d;font-size:14px;">' + nodeData.formula + '</p>';
  }
  if (nodeData.name_en) {
    html += '<p style="color:#95a5a6;font-size:12px;">' + nodeData.name_en + '</p>';
  }

  // Properties
  if (nodeData.properties && nodeData.properties.length > 0) {
    html += '<div class="section"><h3>性质数据 (' + nodeData.properties.length + ' 条)</h3>';
    html += '<table><thead><tr><th>性质</th><th>数值</th><th>来源</th></tr></thead><tbody>';
    for (const p of nodeData.properties) {
      const sources = (p.source_papers || []).map(s => '<span class="paper-badge">' + s + '</span>').join(" ");
      html += '<tr><td>' + (p.property || "") +
        (p.condition ? '<br><small style="color:#7f8c8d;">' + p.condition + '</small>' : '') +
        '</td><td><strong>' + (p.value || "") + '</strong></td><td>' + sources + '</td></tr>';
    }
    html += '</tbody></table></div>';
  }

  // Composition
  if (nodeData.composition && Object.keys(nodeData.composition).length > 0) {
    html += '<div class="section"><h3>化学组成</h3><table><thead><tr><th>组分</th><th>含量</th></tr></thead><tbody>';
    for (const [k, v] of Object.entries(nodeData.composition)) {
      html += '<tr><td>' + k + '</td><td>' + v + '</td></tr>';
    }
    html += '</tbody></table></div>';
  }

  // Incoming edges
  const incomingEdges = EDGES_BY_TARGET[nodeData.id] || [];
  if (incomingEdges.length > 0) {
    html += '<div class="section"><h3>入边（如何到达此节点）</h3>';
    for (const e of incomingEdges) {
      const srcName = (TREE_DATA.nodes[e.from] || {}).name || e.from;
      html += '<p style="font-size:13px;margin:4px 0;">' +
        '<strong>' + (e.label_short || "") + '</strong> ' +
        '<span style="color:#7f8c8d;">← ' + srcName + '</span> ' +
        (e.source_papers || []).map(s => '<span class="paper-badge">' + s + '</span>').join(" ") +
        '</p>';
    }
    html += '</div>';
  }

  // Source papers
  if (nodeData.source_papers && nodeData.source_papers.length > 0) {
    html += '<div class="section"><h3>论文来源</h3><p>';
    for (const p of nodeData.source_papers) {
      html += '<span class="paper-badge">' + p + '</span> ';
    }
    html += '</p></div>';
  }

  // Notes
  if (nodeData.notes) {
    html += '<div class="section"><h3>备注</h3><p style="font-size:13px;color:#7f8c8d;">' + nodeData.notes + '</p></div>';
  }

  // Meta
  html += '<div style="margin-top:20px;font-size:11px;color:#bdc3c7;">' +
    '节点ID: ' + (nodeData.id || "?") +
    ' | depth: ' + (nodeData.depth || "?") +
    ' | 论文: ' + (nodeData.source_papers || []).length + ' 篇' +
    ' | 性质: ' + (nodeData.properties || []).length + ' 条' +
    '</div>';

  panel.innerHTML = html;
}

// ===== RESPONSIVE =====
window.addEventListener("resize", () => {
  location.reload();
});
</script>
</body>
</html>'''


def tree_to_html(tree: dict) -> str:
    """将 system-tree.json 嵌入 HTML 模板。"""
    tree_json = json.dumps(tree, ensure_ascii=False)
    return HTML_TEMPLATE.replace("__TREE_JSON__", tree_json)


def render_html(tree_path: Path = None, output_path: Path = None):
    """主渲染流程。"""
    if tree_path is None:
        tree_path = TREE_PATH

    if not tree_path.exists():
        print(f"[ERROR] 树文件不存在: {tree_path}")
        return -1

    with open(tree_path, "r", encoding="utf-8") as f:
        tree = json.load(f)

    if not tree.get("nodes"):
        print("[WARN] 树中无节点——HTML 将显示为空")

    html = tree_to_html(tree)

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    if output_path is None:
        output_path = OUTPUT_DIR / "system-tree.html"

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(html)

    print(f"[OK] 渲染完成: {output_path}")
    print(f"  节点: {len(tree.get('nodes', {}))} | 边: {len(tree.get('edges', {}))}")
    print(f"  用浏览器打开即可交互浏览（点击节点查看详情）")


def main():
    parser = argparse.ArgumentParser(
        description="MgO-SiO₂(-C-H₂O) 体系树 — D3.js 交互式 HTML 渲染")
    parser.add_argument("--tree", default=None, help="system-tree.json 路径")
    parser.add_argument("--output", default=None, help="输出 HTML 路径")
    args = parser.parse_args()

    sys.exit(render_html(
        tree_path=Path(args.tree) if args.tree else None,
        output_path=Path(args.output) if args.output else None
    ))


if __name__ == "__main__":
    main()
