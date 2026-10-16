# 2026-10-16 · GitHub Pages 与 Hugo 博客搭建文章

## 更新内容

- 新增正式文章 `content/posts/github-pages-hugo-personal-blog.md`，标题为“用 GitHub Pages 和 Hugo 搭建个人博客：从零开始到自动发布”。
- Front Matter 设置 `draft = false`，分类为“技术”“Hugo”，附带描述和标签；同时清理已删除的初始示例草稿 `content/posts/first-post.md`。
- 内容包括：静态博客原理、用户/项目站点、安装、项目目录、现成与自建主题、Front Matter、草稿/未来时间、页面包图片、本地预览、Git 认证与推送、完整 Actions 工作流、上线验证、日常写作、故障排查、自定义域名及官方参考资料。
- 示例基于本项目 Hugo 0.168.0 与现有工作流，使用 `hugo new project`、`hugo new content`、`locale` 等对应版本用法。
- 更新 README 的文章入口和示例草稿状态说明。

## 文章元数据

```toml
+++
title = '用 GitHub Pages 和 Hugo 搭建个人博客：从零开始到自动发布'
date = '2026-10-16T12:05:00+08:00'
draft = false
categories = ['技术', 'Hugo']
tags = ['GitHub Pages', '博客搭建', '自动部署']
+++
```

## 验证

- Hugo 正式构建无警告，文章进入首页、中文分类、Hugo 分类及 RSS。
- 文章中的完整 YAML 工作流与仓库工作流一致；Front Matter 和代码围栏检查通过。
- 8 项主题测试全部通过。
- 文章实际页面在 Chromium 的 320/375/1440 像素视口无全页横向溢出，目录锚点、标题、静态资源及控制台检查通过。
