#!/usr/bin/env python3
"""MgO-SiO₂(-C-H₂O) 体系树 — DOT → SVG 渲染器

用法:
  python scripts/render_tree.py                    # 生成 DOT + 尝试 SVG 渲染
  python scripts/render_tree.py --dot-only          # 仅生成 DOT 文本
  python scripts/render_tree.py --output output/my-tree.svg

依赖（可选）:
  - Graphviz (dot CLI) — 安装: winget install graphviz
    未安装时仅生成 DOT 文本文件，可手动用在线工具渲染
    在线渲染: https://dreampuf.github.io/GraphvizOnline/
"""

import argparse
import json
import subprocess
import sys
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TREE_PATH = ROOT / "system-tree.json"
OUTPUT_DIR = ROOT / "output"


def load_tree():
    """加载 system-tree.json。"""
    with open(TREE_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def escape_dot_label(text: str) -> str:
    """转义 DOT label 中的特殊字符。"""
    if not text:
        return ""
    return text.replace('"', '\\"').replace('\n', '\\n')


def tree_to_dot(tree: dict) -> str:
    """将 system-tree.json 转换为 DOT 语言文本。"""
    lines = [
        'digraph MgOSiO2_System {',
        '  rankdir=TB;',
        '  bgcolor="white";',
        '  fontname="Microsoft YaHei";',
        '  fontsize=14;',
        '',
        '  // 全局样式',
        '  node [fontname="Microsoft YaHei", fontsize=11, shape=box, style="rounded,filled", margin="0.15,0.1"];',
        '  edge [fontname="Microsoft YaHei", fontsize=9];',
        '',
        '  // 图标题',
        f'  labelloc="t";',
        f'  label="黑滑石 MgO-SiO₂(-C-H₂O) 物相-应用体系树\\n{tree["meta"]["version"]} | {tree["meta"]["last_updated"]}";',
        f'  fontsize=16;',
        '',
    ]

    # 节点
    for nid, node in tree.get("nodes", {}).items():
        name = escape_dot_label(node.get("name", nid))
        formula = escape_dot_label(node.get("formula", ""))
        full_label = f"{name}\\n{formula}" if formula else name

        t = node.get("type", "intermediate_phase")

        if t == "raw_material":
            lines.append(
                f'  "{nid}" ['
                f'label="{full_label}", '
                f'fillcolor="#2c3e50", fontcolor="white", '
                f'penwidth=2'
                f'];'
            )
        elif t == "intermediate_phase":
            lines.append(
                f'  "{nid}" ['
                f'label="{full_label}", '
                f'fillcolor="#ecf0f1", color="#34495e", fontcolor="#2c3e50"'
                f'];'
            )
        elif t == "product":
            lines.append(
                f'  "{nid}" ['
                f'label="{full_label}", '
                f'fillcolor="#27ae60", fontcolor="white", penwidth=2'
                f'];'
            )
        elif t == "byproduct":
            lines.append(
                f'  "{nid}" ['
                f'label="{full_label}", '
                f'fillcolor="#95a5a6", fontcolor="white", style="dashed,rounded,filled"'
                f'];'
            )
        lines.append('')

    # 边
    for eid, edge in tree.get("edges", {}).items():
        label = escape_dot_label(edge.get("label_short", ""))
        sources = ", ".join(edge.get("source_papers", []))
        full_label = f"{label}\\n[{sources}]" if sources else label
        etype = edge.get("type", "process")

        if etype == "process":
            lines.append(
                f'  "{edge["from"]}" -> "{edge["to"]}" ['
                f'label="{full_label}", '
                f'color="#e74c3c", fontcolor="#c0392b"'
                f'];'
            )
        elif etype == "property_link":
            via = escape_dot_label(edge.get("via_property", ""))
            link_label = f"{via}\\n[{sources}]" if via else full_label
            lines.append(
                f'  "{edge["from"]}" -> "{edge["to"]}" ['
                f'label="{link_label}", '
                f'color="#2980b9", fontcolor="#2c3e50", style=dashed'
                f'];'
            )
        lines.append('')

    lines.append('}')
    return '\n'.join(lines)


def find_dot() -> str | None:
    """查找 Graphviz dot 可执行文件路径。"""
    # 1. 检查 PATH
    found = shutil.which("dot")
    if found:
        return found
    # 2. 检查 Windows 标准安装路径
    windows_paths = [
        "C:/Program Files/Graphviz/bin/dot.exe",
        "C:/Program Files (x86)/Graphviz/bin/dot.exe",
    ]
    for p in windows_paths:
        if Path(p).exists():
            return p
    return None


def has_graphviz() -> bool:
    """检查 Graphviz dot 命令是否可用。"""
    return find_dot() is not None


def render_dot_to_image(dot_text: str, output_path: Path, fmt: str = "svg") -> bool:
    """调用 Graphviz dot 命令渲染。"""
    dot_exe = find_dot()
    if not dot_exe:
        print(f"[WARN] Graphviz (dot) 未安装——无法渲染为 {fmt}")
        print(f"  安装: winget install graphviz")
        print(f"  或在线渲染 DOT 文件: https://dreampuf.github.io/GraphvizOnline/")
        return False

    result = subprocess.run(
        [dot_exe, f"-T{fmt}", "-o", str(output_path)],
        input=dot_text,
        text=True,
        capture_output=True
    )
    if result.returncode != 0:
        print(f"[ERROR] Graphviz 渲染失败:")
        print(result.stderr)
        return False
    return True


def render(tree_path: Path = None, output_path: Path = None, fmt: str = "svg",
           dot_only: bool = False):
    """主渲染流程。"""
    if tree_path is None:
        tree_path = TREE_PATH

    if not tree_path.exists():
        print(f"[ERROR] 树文件不存在: {tree_path}")
        print(f"  提示: 先运行 ingest.py 注册论文")
        return -1

    tree = load_tree()

    if not tree.get("nodes"):
        print("[WARN] 树中无节点——将生成空图")
    if not tree.get("edges"):
        print("[WARN] 树中无边——仅显示节点")

    dot_text = tree_to_dot(tree)

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    # 总是保存 DOT 源文件
    dot_path = OUTPUT_DIR / "system-tree.dot"
    with open(dot_path, "w", encoding="utf-8") as f:
        f.write(dot_text)
    print(f"[OK] DOT 文件已保存: {dot_path}")

    if dot_only:
        return 0

    # 尝试渲染图片
    if output_path is None:
        output_path = OUTPUT_DIR / f"system-tree.{fmt}"

    success = render_dot_to_image(dot_text, output_path, fmt)
    if success:
        print(f"[OK] 渲染完成: {output_path}")
    print(f"  节点: {len(tree.get('nodes', {}))} | 边: {len(tree.get('edges', {}))}")
    print(f"  树版本: {tree['meta']['version']}")
    return 0 if success else -1


def main():
    parser = argparse.ArgumentParser(
        description="MgO-SiO₂(-C-H₂O) 体系树 — 渲染为图片")
    parser.add_argument("--tree", default=None, help="system-tree.json 路径")
    parser.add_argument("--output", default=None, help="输出路径 (默认: output/system-tree.svg)")
    parser.add_argument("--format", default="svg", choices=["svg", "png", "pdf"])
    parser.add_argument("--dot-only", action="store_true", help="仅生成 DOT 文本文件")
    args = parser.parse_args()

    sys.exit(render(
        tree_path=Path(args.tree) if args.tree else None,
        output_path=Path(args.output) if args.output else None,
        fmt=args.format,
        dot_only=args.dot_only
    ))


if __name__ == "__main__":
    main()
