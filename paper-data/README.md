# paper-data/ — 论文四问分析 JSON

## 文件命名

`PAPER-XXX.json`（XXX 为三位数字编号，与 papers/ 目录一致）

## JSON Schema

```json
{
  "paper": {
    "id": "PAPER-XXX",
    "title": "",
    "authors": "",
    "year": 2022,
    "journal": "",
    "doi": "",
    "research_type": "experiment | review | theory | policy",
    
    "tree_contributions": {
      "new_nodes": [],
      "new_edges": [],
      "properties_added_to": {},
      "papers_cross_validated": []
    },
    
    "q3_reliability": {
      "scale": "powder | lab_sample | pilot | industrial",
      "full_params": true,
      "replicates": false,
      "journal_tier": "SCI_Q1 | SCI | chinese_core | conference | thesis | report"
    },
    
    "q4_cross_validation": {
      "verified_by": [],
      "contradicts": [],
      "complements": []
    }
  }
}
```

## 字段说明

| 字段 | 类型 | 必填 | 说明 |
|------|------|:---:|------|
| `paper.id` | string | ✅ | PAPER 编号 |
| `paper.title` | string | ✅ | 论文标题 |
| `paper.authors` | string | ✅ | 作者 |
| `paper.year` | number | ✅ | 发表年份 |
| `tree_contributions.new_nodes` | array | — | Q1: 新节点定义（格式同 system-tree.json nodes schema） |
| `tree_contributions.new_edges` | array | — | Q2: 新边定义（格式同 system-tree.json edges schema） |
| `tree_contributions.properties_added_to` | object | — | Q1 补充: 追加性质到已有节点 `{"node_id": [{property...}]}` |
| `tree_contributions.papers_cross_validated` | array | — | Q4: 交叉验证的论文 ID 列表 |
| `q3_reliability.scale` | enum | ✅ | 实验规模 |
| `q3_reliability.full_params` | boolean | ✅ | 参数是否完整可复现 |
| `q3_reliability.journal_tier` | enum | ✅ | 期刊等级 |
| `q4_cross_validation` | object | — | 与其他论文的交叉验证关系 |
