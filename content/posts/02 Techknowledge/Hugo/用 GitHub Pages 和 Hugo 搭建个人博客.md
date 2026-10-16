+++
title = '用 GitHub Pages 和 Hugo 搭建个人博客：从零开始到自动发布'
date = '2026-10-16T12:05:00+08:00'
draft = false
categories = ['hugo']
aliases = ['/posts/github-pages-hugo-personal-blog/']
tags = ['GitHub Pages', '博客搭建', '自动部署']
description = '从理解静态博客开始，逐步完成 Hugo 安装、主题配置、Markdown 写作、GitHub Pages 自动部署，并解决路径、草稿、主题子模块和推送权限等常见问题。'
+++

搭建个人博客，不一定要购买服务器、安装数据库，再维护一套后台系统。如果主要需求是记录技术、整理知识和分享生活，**Hugo + GitHub Pages** 是一种轻量而实用的组合。

Hugo 负责把文章生成网站，GitHub 负责保存源码，GitHub Actions 负责自动构建，GitHub Pages 负责让读者通过网址访问。配置完成后，日常更新通常只剩三件事：**写 Markdown、提交 Git、推送到 GitHub**。

本文按照实际搭建顺序展开。示例使用名为 `blog` 的公开仓库、`main` 分支和 GitHub Actions 部署方式；文中的 `yourname` 需要替换为自己的 GitHub 用户名。

## 一、先弄清楚：这几个工具分别做什么

### GitHub Pages：托管生成好的网站

GitHub Pages 是 GitHub 提供的静态网站托管服务，适合博客、个人主页、项目介绍和文档站点。

所谓“静态”，是指服务器直接返回已经生成好的 HTML、CSS、JavaScript 和图片，而不是每次访问都运行后端程序、查询数据库，再拼出页面。

因此，它不直接运行 PHP、Python 或 Go 后端，也不提供一套现成的登录、评论和数据库系统。这些能力可以通过外部服务补充，但不是搭建博客的必要前提。

对于公开仓库，GitHub Free 可以使用 Pages。私有仓库的适用范围与账号套餐有关，以 GitHub 当前说明为准；**仓库私有也不等于发布的网站自动受到访问保护**。

### Hugo：把内容和主题编译成网站

Hugo 是静态网站生成器。它把以下内容组合起来：

- Markdown 文章：负责内容。
- 主题和模板：负责页面结构。
- CSS 和 JavaScript：负责外观与少量交互。
- 站点配置：负责标题、网址、语言、分页等设置。

然后生成可以直接托管的网站文件，默认输出到 `public/`。

你维护的是文章和配置，而不是一篇篇手工编写完整的 HTML 页面。

### GitHub Actions：连接源码和发布网站

GitHub Pages 不会因为仓库里有 `hugo.toml`，就自动按照 Hugo 的规则构建。我们需要明确告诉 GitHub：安装哪个版本的 Hugo、执行什么命令、部署哪些文件。

GitHub Actions 就是执行这些步骤的自动化工具。整条发布链路可以理解为：

```text
本地写 Markdown
    ↓ git push
GitHub 仓库保存源码
    ↓ 触发工作流
GitHub Actions 运行 Hugo
    ↓ 生成 public/
GitHub Pages 部署静态文件
    ↓
读者通过博客网址访问
```

三个角色不要混淆：**仓库存放源码，Actions 执行构建，Pages 提供网站访问**。

## 二、选对仓库类型和博客地址

GitHub Pages 常见的两种地址形式如下：

| 类型 | 仓库名称示例 | 默认访问地址 |
| --- | --- | --- |
| 用户站点 | `yourname.github.io` | `https://yourname.github.io/` |
| 项目站点 | `blog` | `https://yourname.github.io/blog/` |

如果想让博客直接位于用户名域名的根目录，可以选择用户站点。如果已经有主页，或者希望博客作为一个独立项目存在，可以选择项目站点。

本文使用第二种，因此站点基础地址是：

```text
https://yourname.github.io/blog/
```

这里的 `/blog/` 很重要。漏掉它，经常会出现“首页能打开，但样式、图片或链接不正常”的问题。

## 三、准备本地环境

需要准备：

1. 一个 GitHub 账号。
2. Git，用来管理和推送源码。
3. Hugo，用来创建、预览和构建网站。
4. 一个文本编辑器，例如 VS Code。

### 安装 Hugo

macOS 已安装 Homebrew 的情况下，可以执行：

```bash
brew install hugo
```

Windows、Linux 或没有 Homebrew 的环境，可以参考 [Hugo 官方安装文档](https://gohugo.io/installation/)选择对应安装方式。

检查工具是否就绪：

```bash
git --version
hugo version
```

本文以 **Hugo 0.168.0** 为例，后面的工作流也固定使用这个版本。日后升级时，建议同时调整本地和 CI 的版本，并重新检查主题兼容性。

如果主题使用需要 Extended 版本的资源处理能力，应确认本地和 CI 安装相应版本。本文的 CI 示例开启了 `extended: true`。

### 设置 Git 提交者信息

首次使用 Git，可以配置：

```bash
git config --global user.name "你的名字"
git config --global user.email "你的邮箱"
```

注意，这两个配置只是**提交记录上的作者信息**，并不能完成 GitHub 登录，也不会授予仓库写入权限。

## 四、创建 Hugo 项目并理解目录结构

在希望保存博客的父目录执行：

```bash
hugo new project blog
cd blog
git init -b main
```

这里使用新版本 Hugo 的 `hugo new project` 命令；旧版教程中常见的项目创建命令是 `hugo new site`。如果本地命令不匹配，先用 `hugo version` 和 `hugo help` 确认版本。

初始项目中，最常用的目录和文件是：

```text
blog/
├── archetypes/       新文章使用的默认模板
├── assets/           需要资源管线处理的样式、脚本等
├── content/          文章和内容页面
├── layouts/          项目级模板或主题覆盖模板
├── static/           原样复制到网站中的静态文件
├── themes/           Hugo 主题
└── hugo.toml         站点配置
```

首次构建后还会出现 `public/`，这是生成的网站，而不是文章源码。

理解这个区别很重要：

- `content/`、主题、配置等应该纳入版本管理。
- `public/` 可以随时由源码重新生成；使用本文的 Actions 部署方式，不需要提交它。

## 五、选择主题并配置站点

### 从现成主题起步

新手可以先用现成主题跑通流程，再逐步调整样式。以 Ananke 为例：

```bash
git submodule add https://github.com/gohugo-ananke/ananke.git themes/ananke
```

这条命令把主题作为 **Git 子模块**加入项目。主仓库记录主题所使用的提交版本，主题源码本身由它的独立仓库管理。

以后在新电脑克隆博客时，使用：

```bash
git clone --recurse-submodules https://github.com/yourname/blog.git
```

如果已经克隆过，但主题目录为空，则在博客根目录执行：

```bash
git submodule update --init --recursive
```

这也是后面工作流中需要设置 `submodules: recursive` 的原因。

### 编辑 hugo.toml

用下面的基础配置替换初始配置，并修改用户名和博客标题：

```toml
baseURL = 'https://yourname.github.io/blog/'
locale = 'zh-cn'
title = '我的个人博客'
theme = 'ananke'

[pagination]
  pagerSize = 10
```

几个字段的含义：

- `baseURL`：网站正式发布地址，项目站点必须包含仓库路径，建议以 `/` 结尾。
- `locale`：本文所用新版本 Hugo 的地区与语言设置。
- `title`：博客名称。
- `theme`：`themes/` 中使用的主题目录名称。
- `pagerSize`：每页显示的文章数量；具体呈现仍由主题模板决定。

旧教程可能使用 `languageCode` 等配置。不要把不同 Hugo 版本的配置机械混在一起，应以所用版本的文档为准。

### 如果使用自建主题

自建主题也遵循相同原则：将完整主题源码保存到 `themes/主题名/`，然后修改 `theme` 配置。

例如本博客后来使用自建的 Clarity 主题：

```toml
theme = 'clarity'
```

Clarity 采用顶部博客标题、左侧分类、右侧文章列表的布局。它的源码随博客仓库保存，不依赖单独下载主题。

需要区分的是：**Hugo 提供分类数据，但分类菜单放在哪里、是否显示数量、如何高亮，取决于主题的具体实现**。换主题并不只是换颜色，也可能改变页面组织方式和可用配置。

## 六、写第一篇文章

在项目根目录执行：

```bash
hugo new content posts/hello-world.md
```

这会创建 `content/posts/hello-world.md`。用编辑器打开，写入类似内容：

```markdown
+++
title = '我的第一篇博客'
date = '2020-01-01T10:00:00+08:00'
draft = false
categories = ['技术', 'Hugo']
tags = ['博客搭建']
description = '记录我搭建个人博客的开始。'
+++

## 为什么开始写博客

我希望把学习过程中的问题、思考和解决方法记录下来。

## 下一步计划

- 持续整理技术笔记
- 分享实践经验
- 慢慢完善博客主题
```

示例日期只是为了展示格式，**发布时请改成自己的实际发布时间**。

### Front Matter 是什么

文件开头的 Front Matter 表示文章元数据。上面的写法使用 TOML 格式，以两组 `+++` 包围；Hugo 也支持 YAML 格式，以两组 `---` 包围。

其中：

- `title`：文章标题。
- `date`：发布时间，可附带时区。
- `draft`：是否为草稿。
- `categories`：分类，可以有多个。
- `tags`：更细的标签。
- `description`：简短介绍；是否在列表中展示由主题决定。

结束分隔符后面才是正文，使用普通 Markdown。

#### 使用 YAML 格式

上面的 TOML 文章头也可以等价地写成 YAML：

```yaml
---
title: "我的第一篇博客"
date: "2020-01-01T10:00:00+08:00"
draft: false
categories:
  - 技术
  - Hugo
tags:
  - 博客搭建
description: "记录我搭建个人博客的开始。"
---
```

第二个 `---` 之后，继续编写相同的 Markdown 正文即可。示例日期同样需要换成实际发布时间。

两种写法的主要区别是：

- **分隔符**：TOML 使用 `+++`，YAML 使用 `---`，文章头必须从文件开头开始。
- **键值对**：TOML 写 `title = '标题'`，YAML 写 `title: "标题"`，冒号后要留空格。
- **列表**：YAML 可像示例一样每行用 `-` 列出分类和标签，也可写成 `categories: [技术, Hugo]`。即使只有一个分类，也建议保留列表形式。
- **缩进与类型**：YAML 使用空格缩进，不要使用 Tab；`draft: false` 中的 `false` 不加引号，日期和含冒号等特殊字符的文本建议加引号。

同一个站点的不同文章可以分别使用 TOML 或 YAML，字段含义不变，不需要修改主题。转换单篇文章时，要同时修改分隔符和内部语法，不能只把 `+++` 替换成 `---`。

### 特别注意草稿和未来日期

新建文章通常默认是 `draft = true`。这有助于避免尚未写完的内容被直接发布。

正式发布前需要确认：

1. `draft = false`，或者删除 `draft` 字段。
2. `date` 不是未来时间。
3. 正文已经保存，并且文章文件已经加入 Git。

仅仅推送一个 Markdown 文件，并不保证它会出现在正式网站上。

## 七、本地预览、图片和正式构建

### 包含草稿的本地预览

```bash
hugo server -D
```

在浏览器打开终端显示的地址，通常是 `http://localhost:1313/`；如果包含子路径，以终端实际输出为准。

编辑文章或样式后，开发服务器通常会自动重建并刷新页面。按 `Ctrl+C` 停止服务器。

`-D` 只表示包含草稿，不会自动包含所有未来文章。确实需要预览未来内容时，可以使用：

```bash
hugo server -D -F
```

不要为了让草稿临时可见，就把正式部署命令改成永久携带 `-D` 或 `-F`。

### 推荐用页面包管理文章图片

文章较长、配图较多时，可以把它组织成页面包：

```text
content/posts/my-note/
├── index.md
└── screenshot.png
```

在 `index.md` 中通过相对路径引用：

```markdown
![配置界面](screenshot.png)
```

图片与文章放在一起更方便迁移，也能减少把域名或 `/blog/` 硬编码进正文的情况。图片最终如何处理，仍应结合主题的 Markdown 渲染规则检查实际页面。

### 检查正式构建

```bash
hugo --minify
```

构建成功后，生成的网站位于 `public/`。正式构建默认排除草稿和未来文章，所以应同时检查首页、分类页和文章是否符合预期。

一个实用习惯是：**先在本地确认内容和构建没有问题，再推送到线上**。

## 八、把源码推送到 GitHub

### 先添加 .gitignore

在根目录创建 `.gitignore`：

```gitignore
/public/
/resources/_gen/
.hugo_build.lock
.DS_Store
```

这里忽略的是生成文件和本地临时文件，不是文章、主题或配置。不要把 `content/`、`themes/`、`.gitmodules` 或 `.github/workflows/` 整体忽略掉。

如果使用 Obsidian 等工具写作，也可以按需忽略本地工作区配置，避免把与读者无关的个人状态推送出去。

### 创建远端仓库

在 GitHub 新建名为 `blog` 的公开仓库。为了让首次推送更简单，可以先不要让 GitHub 自动创建 README、许可证或 `.gitignore`，避免远端先产生一个独立的初始提交。

然后执行：

```bash
git add .
git commit -m "初始化 Hugo 博客"
git remote add origin https://github.com/yourname/blog.git
git push -u origin main
```

把 `yourname` 替换为自己的用户名。已经设置过 `origin` 的仓库，不需要重复执行 `git remote add origin`，可以先用 `git remote -v` 检查。

GitHub 的 HTTPS 认证应使用受支持的凭据方式，例如 GitHub CLI、凭据管理器或个人访问令牌；不能简单地把账号密码当作 Git 推送密码。

如果已经安装 GitHub CLI，可以用它完成认证和 Git 凭据配置：

```bash
gh auth login
gh auth setup-git
```

也可以配置 SSH 并使用 SSH 仓库地址。无论采用哪种方式，登录的账号都必须对目标仓库有写入权限。

## 九、配置 GitHub Pages 自动部署

### 1. 启用 GitHub Actions 发布来源

打开仓库：

**Settings → Pages → Build and deployment → Source → GitHub Actions**

本文采用工作流构建和部署，不要误选成从 `main` 分支根目录直接发布。源码根目录不是生成好的 Hugo 网站。

### 2. 创建工作流文件

在项目根目录新建：

```text
.github/workflows/hugo.yaml
```

内容如下。该示例与本博客目前使用的基本工作流一致，适用于这里展示的主题；它不是所有 Hugo 主题的通用依赖安装清单。

```yaml
name: Build and deploy Hugo site

on:
  push:
    branches: [main]
  workflow_dispatch:

permissions:
  contents: read
  pages: write
  id-token: write

concurrency:
  group: pages
  cancel-in-progress: false

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout
        uses: actions/checkout@v7
        with:
          submodules: recursive

      - name: Configure Pages
        id: pages
        uses: actions/configure-pages@v6

      - name: Install Hugo
        uses: peaceiris/actions-hugo@v3
        with:
          hugo-version: "0.168.0"
          extended: true

      - name: Build
        run: hugo --minify --baseURL "${{ steps.pages.outputs.base_url }}/"

      - name: Upload artifact
        uses: actions/upload-pages-artifact@v5
        with:
          path: ./public

  deploy:
    environment:
      name: github-pages
      url: ${{ steps.deployment.outputs.page_url }}
    runs-on: ubuntu-latest
    needs: build
    steps:
      - name: Deploy
        id: deployment
        uses: actions/deploy-pages@v5
```

YAML 的缩进具有语法意义。`on`、`permissions`、`concurrency` 和 `jobs` 是同一级，不能在复制时给某一整段额外缩进。

### 3. 理解工作流中的关键设置

**触发条件。** 推送到 `main` 后自动执行；`workflow_dispatch` 允许在 Actions 页面手动运行。实际默认分支如果不是 `main`，应同步修改。

**主题检出。** `submodules: recursive` 会初始化主题子模块。缺少它时，本地可以正常显示，但 CI 可能找不到主题。

**构建权限。** `contents: read` 用于读取源码；`pages: write` 用于发布 Pages；`id-token: write` 用于部署所需的身份验证。这是工作流权限，不是要求你把个人访问令牌写进文件。

**站点路径。** `configure-pages` 提供 Pages 的基础地址，构建时传给 `--baseURL`，让生成链接适应项目子路径或已配置的域名。不过，正文和自定义模板里手写的错误绝对路径不会因此自动修复。

**先构建，再部署。** `build` 生成并上传 `public/`；`deploy` 通过 `needs: build` 等待构建成功，然后发布同一份产物。不是把整个 Git 仓库当作网页目录直接上传。

**并发控制。** 同一时刻的部署放在 `pages` 并发组中，减少多个更新交错发布的问题；`cancel-in-progress: false` 不会直接取消正在执行的部署。

**版本管理。** 工作流固定 Hugo 版本，避免安装工具自动升级后，主题突然无法构建。Actions 的主版本也需要定期检查，而不是永远照抄一份旧配置。

如果主题明确要求 Node.js、Dart Sass、Hugo Modules 或其他依赖，应按主题文档补充安装步骤，不要只看到“Hugo”三个字就认为所有主题的工作流完全一样。

### 4. 提交工作流

```bash
git add .github/workflows/hugo.yaml
git commit -m "配置 GitHub Pages 自动部署"
git push
```

推送完成后，打开仓库的 **Actions** 页面，查看 `Build and deploy Hugo site` 的运行情况。

## 十、验证第一次上线

不要只看到“代码推送成功”，就认为网站已经发布成功。至少检查三层结果：

1. **源码层**：GitHub 仓库里能看到最新文章和工作流。
2. **构建层**：Actions 中 `build`、`deploy` 都成功。
3. **访问层**：浏览器能打开首页、文章、分类及静态资源。

部署成功后，访问：

```text
https://yourname.github.io/blog/
```

首次部署和更新可能需要短暂等待。若尚未显示新内容，先检查工作流是否完成，再考虑缓存，而不是立即反复修改配置。

本文所在博客采用的仓库是 `Jeff-545/blog`，对应访问地址是：

<https://jeff-545.github.io/blog/>

## 十一、以后如何持续写作

基础配置完成后，不需要每次重新安装主题或创建工作流。

可以把每次更新固定成以下步骤：

```bash
# 1. 创建文章
hugo new content posts/a-new-note.md

# 2. 编辑正文、分类和发布时间，确认 draft = false

# 3. 本地预览
hugo server -D

# 4. 停止预览后，检查正式构建
hugo --minify

# 5. 提交并推送
# 页面包有图片时，应把该页面包目录一起加入 Git。
git add content/posts/a-new-note.md
git commit -m "发布一篇新文章"
git push
```

这里显式添加文章文件，是为了避免把临时文件、截图或其他无关改动意外一起提交。更一般地，提交前先执行 `git status` 检查本次究竟准备发布什么。

如果只改主题和样式，同样是本地验证、提交对应源码、推送，Actions 会重新生成网站。

## 十二、常见问题与排查顺序

### 网站返回 404

按下面顺序检查：

1. Pages 是否已经启用，Source 是否为 GitHub Actions。
2. Actions 中的部署是否成功。
3. 地址是否与仓库类型一致：项目站点需要 `/blog/`。
4. 文章是否确实生成，而不是被草稿或未来日期过滤掉。

如果是单篇文章 404，还要检查它当前的实际链接。修改文件名、`slug` 或目录结构，可能会改变文章 URL。

### 首页能打开，但是没有样式或图片

先看 `baseURL`，再看浏览器开发者工具中的失败请求。例如项目站点实际位于 `/blog/`，资源却请求 `/css/main.css`，就可能指向错误位置。

模板应通过 Hugo 提供的链接、资源方法构造 URL，避免到处硬编码 `/` 开头的路径。主题和文章中的图片链接，也需要在正式地址下检查，不能只依赖本地预览结果。

### 本地有文章，线上没有

通常优先检查：

- 本地预览是否用了 `-D`，但文章仍是 `draft = true`。
- 日期是否在未来，时区是否设置正确。
- 是否忘记 `git add`、`git commit` 或 `git push`。
- Actions 是否部署了最新提交。

“预览时看得到”与“符合正式发布条件”是两件事。

### Actions 报主题不存在

如果主题是子模块，检查 `.gitmodules` 是否提交，以及 Checkout 是否设置了 `submodules: recursive`。

如果主题是自建源码，检查 `themes/主题名/` 是否完整提交，以及 `hugo.toml` 中的 `theme` 名称是否正确。

### git push 返回 403

这通常是身份或仓库权限问题，不是 Hugo 或 Pages 的配置问题。

检查远端仓库地址与当前登录账号，确认该账号对目标仓库有写入权限。不要以为修改 `git config user.name` 就等于切换了 GitHub 登录身份。

### 推送成功，但 Actions 没运行

检查工作流文件是否位于 `.github/workflows/`，扩展名是否为 `.yml` 或 `.yaml`，推送分支是否匹配 `on.push.branches`，以及仓库是否允许 Actions 运行。

如果工作流已经出现在 Actions 中，可以先手动触发一次，并查看具体报错，而不是只根据网页是否变化来猜测。

### 本地构建成功，CI 构建失败

对比两边的 Hugo 版本、主题版本、依赖和文件大小写。

例如 macOS 本地可能没有暴露文件名大小写问题，但 GitHub 的 Linux Runner 会严格区分 `Photo.png` 和 `photo.png`。还有一些主题在本地已经安装了额外依赖，CI 却没有安装。

## 十三、可选：绑定自己的域名

站点跑通后，可以再考虑自定义域名，不必在第一次搭建时同时解决所有问题。

大致步骤是：

1. 准备一个自己控制的域名。
2. 按 GitHub 文档要求配置对应 DNS 记录。
3. 在 **Settings → Pages → Custom domain** 中绑定域名。
4. 等待验证和证书就绪，再检查 HTTPS 配置。
5. 将 Hugo 的 `baseURL` 更新为实际站点地址，例如 `https://blog.example.com/`，重新部署并验证资源和文章链接。

独立域名不一定继续使用 `/blog/` 子路径，应以最终绑定方式为准。不要只修改 Hugo 配置而忘记 Pages 与 DNS，也不要只修改 DNS 而不检查生成的绝对链接。

具体记录类型和安全建议请参考 [GitHub 自定义域名文档](https://docs.github.com/en/pages/configuring-a-custom-domain-for-your-github-pages-site)。

## 最后：让搭建服务于写作

这套方案的价值，不只是第一次把网站打开，而是把以后每次发布变得简单且可重复：

- Markdown 让内容易于编辑和迁移。
- Git 保存修改历史。
- Hugo 把内容与表现分离。
- Actions 让构建和部署自动发生。
- Pages 承担静态网站托管。

先跑通一个稳定的发布闭环，再慢慢完善主题、分类、图片和域名。**博客最重要的资产，是持续积累下来的内容，而不是一次性配置了多少功能。**

## 参考资料

- [GitHub Pages 是什么](https://docs.github.com/en/pages/getting-started-with-github-pages/what-is-github-pages)
- [Hugo 安装文档](https://gohugo.io/installation/)
- [Hugo 官方快速入门](https://gohugo.io/getting-started/quick-start/)
- [Hugo 部署到 GitHub Pages](https://gohugo.io/host-and-deploy/deploy-to-github-pages/)
- [GitHub Pages 发布来源设置](https://docs.github.com/en/pages/getting-started-with-github-pages/configuring-a-publishing-source-for-your-github-pages-site)
