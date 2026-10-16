# 2026-10-16 · 补充 YAML Front Matter 写法

## 更新文件

`content/posts/02 Techknowledge/Hugo/用 GitHub Pages 和 Hugo 搭建个人博客.md`

## 更新内容

- 在“Front Matter 是什么”章节增加与原 TOML 示例字段一致的 YAML 文章头。
- 说明 `---` 与 `+++`、冒号与等号、列表、空格缩进及布尔值的区别。
- 明确不同文章可分别使用 TOML 或 YAML，无需修改主题；转换时必须同时调整分隔符和内部语法。
- 保留文章自身的 TOML Front Matter，不修改文章分类或主题实现。

## YAML 示例

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
