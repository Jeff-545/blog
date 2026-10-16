# 使用 Hugo 搭建并部署 GitHub Pages 博客

本文记录本博客从 Hugo 项目初始化、添加主题和文章，到通过 GitHub Actions 发布到 GitHub Pages 的完整过程。适用于个人博客或其他 Hugo 静态站点。

## 1. 准备仓库和工具

1. 在 GitHub 创建一个仓库。本博客使用的仓库为 `Jeff-545/blog`，默认分支为 `main`。
2. 在本地安装 Hugo。可以用 `hugo version` 检查是否安装成功。
3. 初始化本地 Git 仓库，并确保当前分支为 `main`。

GitHub Pages 支持两类站点地址：

- 用户站点：仓库名为 `<username>.github.io`，地址是 `https://<username>.github.io/`。
- 项目站点：普通仓库名（例如 `blog`），地址是 `https://<username>.github.io/<repository>/`。

本博客是项目站点，发布地址为 <https://jeff-545.github.io/blog/>。

## 2. 配置 Hugo

在仓库根目录创建 `hugo.toml`，设置站点 URL、语言、标题和主题：

```toml
baseURL = 'https://jeff-545.github.io/blog'
locale = 'zh-cn'
title = '求真明智'
theme = "ananke"
```

`baseURL` 应对应 GitHub Pages 的最终地址。部署工作流会根据 GitHub Pages 提供的地址覆盖构建时的 `baseURL`，避免项目站点资源路径错误。

## 3. 添加主题和内容

本博客将 Ananke 作为 Git 子模块保存，`.gitmodules` 中记录主题仓库地址。添加或初始化主题时使用：

```bash
git submodule add https://github.com/theNewDynamic/gohugo-theme-ananke.git themes/ananke
```

初始化已有仓库中的子模块：

```bash
git submodule update --init --recursive
```

新建文章：

```bash
hugo new content/posts/first-post.md
```

检查文章 Front Matter 中的 `title`、`date` 和 `draft`。设置为 `draft = true` 的文章默认不会发布；确认可发布后，将其改为 `draft = false`，或删除该字段。

## 4. 本地预览和构建

启动本地预览服务器：

```bash
hugo server -D
```

在浏览器访问终端显示的本地地址。`-D` 会在预览时包含草稿。

执行正式构建：

```bash
hugo --minify
```

Hugo 默认将生成的网站放在 `public/`。它是构建产物，本仓库使用 GitHub Actions 生成并部署，不需要将 `public/` 提交到源码仓库。

## 5. 配置 GitHub Actions 自动部署

仓库中的 `.github/workflows/hugo.yaml` 定义自动部署流程。核心步骤如下：

1. 推送到 `main` 分支或手动触发工作流。
2. 检出源码和 Ananke 子模块（`submodules: recursive`）。
3. 安装 Hugo 并构建站点。
4. 上传 `public/` 构建产物并部署到 GitHub Pages。

工作流必须具有以下权限：

```yaml
permissions:
  contents: read
  pages: write
  id-token: write
```

其中 `pages: write` 和 `id-token: write` 用于 GitHub Pages 的部署。工作流中的 `configure-pages` 会提供站点基础地址；构建命令使用该地址生成正确的静态资源链接：

```yaml
run: hugo --minify --baseURL "${{ steps.pages.outputs.base_url }}/"
```

完整工作流以仓库当前的 `.github/workflows/hugo.yaml` 为准。

## 6. 在 GitHub 仓库启用 Pages

首次部署时，在 GitHub 仓库执行以下设置：

1. 打开 **Settings → Pages**。
2. 在 **Build and deployment → Source** 中选择 **GitHub Actions**。
3. 确认工作流文件已提交到默认分支。

此后每次向 `main` 推送，GitHub Actions 会自动构建并发布。也可以在 **Actions** 页面选择 `Build and deploy Hugo site`，通过 **Run workflow** 手动触发。

## 7. 验证发布结果

1. 打开仓库的 **Actions** 页面，确认 `Build and deploy Hugo site` 的构建和部署作业均成功。
2. 部署成功后访问 <https://jeff-545.github.io/blog/>。
3. 首次发布或更新可能需要短暂等待。后续推送会重新触发部署。

## 常见问题

- **主题目录为空或构建时报主题不存在**：检出仓库时需要初始化子模块；GitHub Actions 中应保留 `submodules: recursive`。
- **页面打开但样式或图片路径错误**：检查 `baseURL` 和工作流传入的 `--baseURL`。项目站点 URL 需要包含仓库路径（本例为 `/blog/`）。
- **文章没有发布**：确认文章不是草稿（`draft = false` 或没有 `draft` 字段）。
- **部署工作流失败**：查看 **Actions** 中失败步骤的日志，并确认 Pages 来源已设为 **GitHub Actions**、工作流具有 `pages: write` 和 `id-token: write` 权限。
- **推送被拒绝**：当前 Git 凭据对应的 GitHub 用户必须对目标仓库具有写入权限。
