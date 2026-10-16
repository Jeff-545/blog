# 2026-10-16 · 移除 collection-header

## 更新代码

- `themes/clarity/layouts/partials/article-list.html`：移除首页、栏目及分类文章列表顶部的 `collection-header` 区块，右侧直接展示列表。
- `themes/clarity/layouts/_default/terms.html`：同步移除分类、标签索引中的同类区块。
- 两处模板保留不占可视空间的 `<h1 class="sr-only">`，维护屏幕阅读器的标题结构。
- `themes/clarity/assets/css/clarity.css`：删除区块专用样式和手机端留白，新增 `.sr-only` 样式。
- `hugo.toml` 与主题指南：移除不再使用的 `params.intro`；更新 README 的布局说明。
- `scripts/test_theme.py`：新增列表页区块移除回归检查，验证文章列表直接顶齐内容区、无可视标题占位；保留分类计数、分页和移动端测试。

## 模板变更

```go-html-template
<h1 class="sr-only">{{ if $page.IsHome }}全部文章{{ else }}{{ $page.Title }}{{ end }}</h1>
```

仅保留语义标题，原区块中的英文标签、篇数统计、可视大标题及介绍不再渲染。
