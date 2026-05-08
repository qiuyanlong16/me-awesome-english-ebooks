# The Economist Daily Reader

经济学人每日阅读工具 — 自动抓取、词汇注释、每日两页、打印友好。

## 功能

- **自动更新**: GitHub Action 每周六自动抓取最新一期《经济学人》
- **智能过滤**: 自动删除空白页和广告页面
- **词汇注释**: 基于个人词库（4000+ 词），标注音标和中文释义
- **每日阅读**: 自动将每期内容分割为约 2 页的每日阅读量
- **打印友好**: A4 纸张排版优化，一键打印

## 使用方式

### 在线阅读

访问 GitHub Pages 地址即可查看所有期刊的每日阅读页面。

### 本地处理

```bash
# 安装依赖
pip install pymupdf

# 处理本地 PDF 文件
python scripts/process.py
```

### 手动触发更新

在 GitHub 仓库的 Actions 页面中，点击 "Weekly Economist Update" → "Run workflow"。

## 项目结构

```
.
├── .github/workflows/    # GitHub Action（每周自动更新）
├── scripts/
│   ├── process.py        # 主流程（下载 → 提取 → 生成）
│   ├── extract.py        # PDF 文本提取
│   ├── annotate.py       # 词汇注释引擎
│   ├── dictionary.py     # 词库加载器
│   ├── generate.py       # HTML 页面生成
│   ├── build_index.py    # 索引页生成
│   └── user_dictionary.json  # 个人词库
├── template/
│   ├── page.html         # 每日阅读页模板
│   └── index.html        # 首页模板
└── docs/
    ├── index.html        # 生成的索引页（GitHub Pages）
    └── issues/           # 生成的每日阅读页
```

## 词库来源

个人词库来自欧路词典导出的生词本（4000+ 词），包含音标和中文释义。

## License

仅供个人学习使用。
