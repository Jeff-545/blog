# 求真明智

基于 Hugo 和自建 **Clarity（明简）** 主题构建的个人博客，部署在 GitHub Pages：<https://jeff-545.github.io/blog/>。

## Clarity 主题

参考 [pi.dev](https://pi.dev/) 的克制排版：顶部博客标题、左侧分类导航、右侧按时间倒序排列的文章标题，使用细分隔线和大面积留白。

- 右侧直接展示文章列表，不显示额外的集合标题、统计或介绍区块。
- 自动读取文章 `categories`，显示分类数量与当前分类高亮。
- 深浅双色随系统切换，也可手动选择并记住偏好。
- 支持分页、文章目录、代码块、表格、RSS 和 404 页面。
- 手机端分类变为横向导航；无外部字体、前端框架或 CDN 依赖。

主题源码位于 [`themes/clarity/`](themes/clarity/)，配置和写作说明见[主题使用指南](docs/themes/clarity.md)。

```bash
hugo server -D  # 本地预览，包含草稿
hugo --minify  # 正式构建，不发布草稿或未来文章
```

当前已有文章仍是草稿，正式首页会显示空状态；发布文章后，列表和分类会自动生成。

## GitHub Pages 自动部署

向 `main` 分支推送更改后，GitHub Actions 会构建 Hugo 站点并部署到 GitHub Pages。Clarity 源码随仓库保存；原 Ananke 子模块保留为备用主题。也可以在仓库的 **Actions** 页面手动运行 `Build and deploy Hugo site` 工作流。

首次配置时，在仓库 **Settings → Pages → Build and deployment** 中将 **Source** 设为 **GitHub Actions**。

完整过程见 [GitHub Pages 博客搭建文档](docs/deployment/github-pages-setup.md)。

## 主题测试

需要 Hugo 0.158.0 或以上版本及 Python 3；测试生成临时内容，不修改真实文章或 `public/`。

```bash
~/Documents/DEV/python_venvs/.venv/bin/python3 scripts/test_theme.py
# 可选：需要在此 Python 环境安装 Playwright 及 Chromium
~/Documents/DEV/python_venvs/.venv/bin/python3 scripts/test_theme.py --browser
```
