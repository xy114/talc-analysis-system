---
name: no-paper-download-access
description: Claude没有期刊/数据库账号，无法自行下载论文，所有论文源文件必须由用户提供
metadata:
  type: feedback
---

Claude Code 没有学术数据库（Web of Science / ScienceDirect / Springer / CNKI 等）的访问权限和账号。用户明确指出"你没有账号，再有链接也下载不了论文，还是需要我去找论文"。所有论文 PDF/TXT 源文件必须由用户下载并放入 sources/ 目录后才能进行分析。

**Why:** 避免 Claude 尝试调用 WebFetch 等工具去抓取付费数据库链接（必然失败），节省时间。

**How to apply:** 当需要分析新论文时，只提供搜索方向建议和关键词，不尝试"帮用户下载"。用户将论文放入 sources/ 后触发入库流程。
