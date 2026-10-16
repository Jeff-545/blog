# 2026-10-16 · 新建 Clarity（明简）Hugo 主题

## 更新代码

- 新增 `themes/clarity/`：主题元数据及 MIT 许可、基础布局、首页、分类与标签列表、文章详情、404、页头、分类侧栏、文章列表与分页。
- 新增 `themes/clarity/assets/css/clarity.css`：深蓝灰与浅纸色双模式、左侧分类/右侧文章的响应式排版、Markdown 阅读样式、键盘焦点及减少动画支持。
- 新增 `themes/clarity/assets/js/clarity.js`：系统配色跟随、手动切换与本地偏好持久化，存储不可用时可继续浏览。
- 更新 `hugo.toml`：切换为 `theme = 'clarity'`，保留 `locale = 'zh-cn'`，新增每页文章数与站点文案配置。保留 Ananke 子模块与已有草稿，不自动发布内容。
- 新增 `scripts/test_theme.py`：隔离构建与浏览器回归测试，不写入真实 `content/` 或 `public/`。
- 更新 `README.md`、部署文档并新增 `docs/themes/clarity.md`，说明使用、分类、预览、部署与验证。

## 关键实现

分类使用 Hugo 原生 taxonomy，不依赖前端筛选：

```go-html-template
{{ range site.Taxonomies.categories.Alphabetical }}
  <a href="{{ .Page.RelPermalink }}">
    {{ .Page.LinkTitle }} {{ .Count }}
  </a>
{{ end }}
```

首页收录正式构建可见的文章，并倒序分页：

```go-html-template
{{ partial "article-list.html" . }}
{{ $pages := partial "collection-pages.html" . }}
{{ $paginator := .Paginate $pages }}
```

样式及脚本通过 Hugo 资源管线压缩、指纹化并使用 `RelPermalink`，支持 GitHub Pages `/blog/` 子路径。

独立审查发现 `.Permalink` 在分页页头指向列表首页，已通过统一列表数据源 `collection-pages.html` 初始化分页，并使用 `$paginator.URL | absURL` 生成各页自引用 canonical。修复及回归说明见 `docs/issues/2026-10-16-分页规范链接指向首页.md`。

## 验证

- Hugo 0.168.0 正式构建成功，无警告。
- 7 项测试通过（含 Chromium 浏览器验证）：分类与当前项、多分类、分页、草稿与未来文章排除、静态资源、RSS、文章内容、内部链接、空站点、独立域名，以及 320/375/768/1440 像素下布局。
- 明暗切换、刷新保持、系统模式变化、存储被禁用、键盘跳转正文与禁用 JavaScript 浏览通过。
- 首页与中文分类的后续分页、独立域名分页的自引用 canonical 验证通过。
