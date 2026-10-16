# Clarity（明简）主题使用指南

Clarity 是本仓库自建的 Hugo 主题。参考 pi.dev 的深蓝灰配色、细线结构、等宽注释和留白，重新设计为适合中文博客的阅读布局。未使用参考网站的字体、图片或源码。

## 布局与功能

- 顶部显示博客标题，右侧提供 RSS 和明暗切换。
- 桌面端左侧为分类导航，显示数量并高亮当前分类；右侧直接显示按日期倒序排列的文章标题，支持分页，不再显示集合标题、统计或介绍区块。列表页仅保留屏幕阅读器可读的一级标题，不占可视空间。
- 手机端分类转为可横向滚动的导航，正文占满可用宽度。
- 文章页包含日期、预计阅读时间、分类链接和可折叠目录；支持 Markdown、代码、表格和引用。
- 未发布文章时显示空状态，不自动创建或发布示例内容。
- 主题默认跟随系统明暗偏好；手动切换后保存在浏览器本地。禁用 JavaScript 时仍可浏览，颜色继续跟随系统。
- 无第三方字体、前端框架或 CDN 依赖。

## 启用与配置

要求 Hugo **0.158.0 或以上**。本项目本地与 GitHub Actions 当前使用 0.168.0。

在根目录 `hugo.toml` 设置：

```toml
baseURL = 'https://jeff-545.github.io/blog'
locale = 'zh-cn'
title = '求真明智'
theme = 'clarity'

[pagination]
  pagerSize = 12

[params]
  tagline = '记录 · 思考 · 分享'
  description = '把想法写下来，让思考有迹可循。'
```

- `title`：顶部博客名称及浏览器标题。
- `tagline`：桌面端页头短句。
- `description`：侧栏说明及默认网页描述。
- `pagerSize`：每页文章数。

原 Ananke 子模块保留不动。如需切回旧主题，只需设置 `theme = 'ananke'` 并确认其子模块已经初始化。

## 添加文章与分类

```bash
hugo new content/posts/my-note.md
```

文章使用 TOML Front Matter，例如：

```toml
+++
title = '我的第一篇记录'
date = '2020-01-01T10:00:00+08:00'
draft = false
categories = ['技术', 'Hugo']
description = '可选的一句话介绍，会显示在文章列表与正文标题下。'
+++
```

以上日期仅为示例，请改为真实发布时间。未来日期的文章默认不会发布。

在 Front Matter 后编写 Markdown 正文即可。`categories` 中的分类自动显示在左侧，不需要手工维护菜单。支持中文及一篇文章属于多个分类；未分类文章仍出现在“全部文章”。分类按 Hugo 的名称顺序排列，文章按日期倒序排列，计数只包含当前构建实际收录的内容。

使用 `hugo server -D` 可以预览草稿；正式发布前请补充内容、分类并设置 `draft = false`。

注意：`docs/` 是仓库说明文档，不属于 Hugo 文章。希望在博客展示的文档，应由作者整理到 `content/posts/` 并设置 Front Matter 后发布。

## 本地预览与发布

```bash
hugo server -D
```

使用终端显示的地址访问预览。正式构建使用 `hugo --minify`，仍通过现有 GitHub Pages 工作流部署，不需要提交 `public/`。CSS、脚本、文章和分类链接均支持 `/blog/` 这类子路径，也支持以后切换到独立域名。

## 文件结构

```text
themes/clarity/
├── theme.toml
├── LICENSE
├── assets/
│   ├── css/clarity.css
│   └── js/clarity.js
└── layouts/
    ├── index.html
    ├── 404.html
    ├── _default/
    │   ├── baseof.html
    │   ├── list.html
    │   ├── single.html
    │   └── terms.html
    └── partials/
        ├── header.html
        ├── sidebar.html
        ├── article-list.html
        ├── collection-pages.html
        └── pagination.html
```

颜色集中在 `clarity.css` 顶部 CSS 变量中。主题脚本只负责明暗偏好；分类跳转、分页和文章浏览均由 Hugo 生成的静态页面完成。

## 验证主题

测试脚本会在临时目录中构造中文分类、多分类、未分类、草稿及未来文章，不修改真实文章和 `public/`。

```bash
~/Documents/DEV/python_venvs/.venv/bin/python3 scripts/test_theme.py
~/Documents/DEV/python_venvs/.venv/bin/python3 scripts/test_theme.py --browser --screenshots /tmp/clarity-preview
```

基础测试只使用 Python 标准库和 Hugo；`--browser` 额外需要 Playwright 与 Chromium。浏览器测试覆盖 320、375、768、1440 像素视口、分类和文章跳转、键盘跳转正文、模式切换及刷新保持、系统模式变化、存储被禁用与无 JavaScript 浏览，以及无全页横向溢出。基础构建测试还验证分页各页的 canonical 规范链接，避免后续页错误指向第一页。截图输出到指定临时目录，不作为博客文章或构建产物提交。
