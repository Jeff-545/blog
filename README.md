# 求真明智

基于 Hugo 和 Ananke 主题构建的个人博客，部署在 GitHub Pages：<https://jeff-545.github.io/blog/>。

## GitHub Pages 自动部署

向 `main` 分支推送更改后，GitHub Actions 会递归检出 Ananke 主题子模块、构建 Hugo 站点并部署到 GitHub Pages。也可以在仓库的 **Actions** 页面手动运行 `Build and deploy Hugo site` 工作流。

首次配置时，在仓库 **Settings → Pages → Build and deployment** 中将 **Source** 设为 **GitHub Actions**。
