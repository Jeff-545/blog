#!/usr/bin/env python3
"""Build isolated Hugo fixtures and verify Clarity; optionally check Chromium layouts."""

import argparse
import functools
import http.server
import json
from pathlib import Path
import shutil
import subprocess
import tempfile
import threading
import unittest
from html.parser import HTMLParser
from urllib.parse import unquote, urlsplit

ROOT = Path(__file__).resolve().parents[1]


class Document(HTMLParser):
    def __init__(self, path):
        super().__init__()
        self.tags = []
        self.feed(path.read_text(encoding="utf-8"))
        self.text = path.read_text(encoding="utf-8")

    def handle_starttag(self, tag, attrs):
        self.tags.append((tag, dict(attrs)))

    def matching(self, tag, **attrs):
        return [a for t, a in self.tags if t == tag and all(a.get(k) == v for k, v in attrs.items())]


class QuietHandler(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *_args):
        pass


class ThemeTests(unittest.TestCase):
    browser = False
    screenshots = None

    @classmethod
    def setUpClass(cls):
        cls.temp = tempfile.TemporaryDirectory(prefix="clarity-test-")
        cls.addClassCleanup(cls.temp.cleanup)
        cls.site = Path(cls.temp.name)
        shutil.copytree(ROOT / "themes/clarity", cls.site / "themes/clarity")
        cls.public = cls.site / "public"
        cls.output = cls.public / "blog"
        (cls.site / "hugo.toml").write_text('''baseURL = 'https://example.org/blog/'
locale = 'zh-cn'
title = '求真明智'
theme = 'clarity'
[pagination]
  pagerSize = 2
''', encoding="utf-8")
        content = cls.site / "content/posts"
        content.mkdir(parents=True)
        for i, categories in enumerate([["技术", "Hugo"], ["生活"], ["技术"], ["技术"], []], 1):
            title = "一段很长的中文文章标题，用来检查窄屏换行与布局" if i == 5 else f"记录 {i}"
            (content / f"note-{i}.md").write_text(
                f'''+++
title = '{title}'
date = '2020-01-0{i}T10:00:00+08:00'
categories = {json.dumps(categories, ensure_ascii=False)}
tags = ['随笔']
draft = false
+++
## 开始记录

这是一篇用于验证主题的文章，包含 **粗体**、[链接](https://example.com) 和 `inline code`。

### 代码与表格

```sh
printf '%s\\n' 'a very long code line that should scroll without stretching the article or the mobile viewport: 012345678901234567890123456789012345678901234567890123456789'
```

| 字段 | 说明 |
| --- | --- |
| 主题 | 简洁、清晰 |

> 让文字回到中心。

- 一条记录
- 一个想法
''', encoding="utf-8")
        (content / "draft.md").write_text("+++\ntitle = '不应公开的草稿'\ndraft = true\n+++\n草稿正文", encoding="utf-8")
        (content / "future.md").write_text("+++\ntitle = '未来文章'\ndate = '2099-01-01'\n+++\n未来正文", encoding="utf-8")
        cls.build(cls.output)

    @classmethod
    def build(cls, destination, *extra):
        result = subprocess.run(
            ["hugo", "--source", str(cls.site), "--destination", str(destination), "--minify", *extra],
            capture_output=True, text=True, check=False,
        )
        log = result.stdout + result.stderr
        if result.returncode or "WARN" in log or "ERROR" in log:
            raise AssertionError(f"Hugo build did not pass cleanly:\n{log}")

    def test_home_and_pagination(self):
        home = Document(self.output / "index.html")
        self.assertEqual(len(home.matching("li", **{"class": "article-row"})), 2)
        self.assertTrue(home.matching("html", lang="zh-cn"))
        self.assertTrue(home.matching("a", href="/blog/page/2/", rel="next"))
        self.assertEqual(len(Document(self.output / "page/3/index.html").matching("li", **{"class": "article-row"})), 1)
        self.assertTrue(Document(self.output / "page/2/index.html").matching("link", rel="canonical", href="https://example.org/blog/page/2/"))
        self.assertNotIn("不应公开的草稿", home.text)
        self.assertFalse((self.output / "posts/future/index.html").exists())
        self.assertFalse((self.output / "posts/draft/index.html").exists())

    def test_categories_and_active_state(self):
        home = Document(self.output / "index.html")
        self.assertTrue(home.matching("a", href="/blog/", **{"aria-current": "page"}))
        category = Document(self.output / "categories/技术/index.html")
        active = category.matching("a", **{"aria-current": "page"})
        self.assertEqual(len(active), 1)
        self.assertEqual(unquote(active[0]["href"]), "/blog/categories/技术/")
        category_page2 = Document(self.output / "categories/技术/page/2/index.html")
        canonical = category_page2.matching("link", rel="canonical")[0]["href"]
        self.assertEqual(unquote(canonical), "https://example.org/blog/categories/技术/page/2/")
        article = Document(self.output / "posts/note-1/index.html")
        self.assertEqual(len(article.matching("a", **{"aria-current": "true"})), 2)
        self.assertIn("文章分类", Document(self.output / "categories/index.html").text)
        self.assertIn("文章标签", Document(self.output / "tags/index.html").text)

    def test_article_markup_and_assets(self):
        doc = Document(self.output / "posts/note-1/index.html")
        self.assertTrue(doc.matching("link", rel="canonical", href="https://example.org/blog/posts/note-1/"))
        self.assertTrue(doc.matching("details", **{"class": "article-toc"}))
        for tag in ["h1", "h2", "h3", "pre", "code", "table", "blockquote"]:
            self.assertTrue(doc.matching(tag), f"Missing article element: {tag}")
        self.assertTrue(doc.matching("link", rel="alternate", href="/blog/index.xml"))
        self.assertTrue(doc.matching("main", id="main"))
        self.assertTrue(doc.matching("a", href="#main", **{"class": "skip-link"}))
        for tag, attr in [("link", "href"), ("script", "src")]:
            for item in doc.matching(tag):
                if item.get("integrity"):
                    self.assertTrue(item[attr].startswith("/blog/"))
                    self.assertTrue((self.public / item[attr].lstrip("/")).is_file())

    def test_internal_links_resolve(self):
        for path in self.output.rglob("*.html"):
            # Hugo's page/1 alias is also checked; external and same-page anchors are ignored.
            for tag, attrs in Document(path).tags:
                if tag != "a" or "href" not in attrs:
                    continue
                url = urlsplit(attrs["href"])
                if url.scheme or url.netloc or not url.path:
                    continue
                self.assertTrue(url.path.startswith("/blog/"), f"Wrong project prefix: {url.path}")
                target = self.public / unquote(url.path).lstrip("/")
                self.assertTrue(target.is_file() or (target / "index.html").is_file(), f"Broken link in {path}: {url.path}")

    def test_empty_site(self):
        empty_content = self.site / "empty-content"
        empty_content.mkdir(exist_ok=True)
        destination = self.site / "empty-output"
        self.build(destination, "--contentDir", str(empty_content))
        doc = Document(destination / "index.html")
        self.assertIn("故事，正在酝酿。", doc.text)
        self.assertIn("分类随文章慢慢生长。", doc.text)
        self.assertFalse(doc.matching("li", **{"class": "article-row"}))
        self.assertIn("这一页", Document(destination / "404.html").text)

    def test_no_collection_header(self):
        for path in ("index.html", "page/2/index.html", "categories/技术/index.html", "categories/index.html", "tags/index.html"):
            doc = Document(self.output / path)
            self.assertFalse(doc.matching("header", **{"class": "collection-header"}), path)
            self.assertTrue(doc.matching("h1", **{"class": "sr-only"}), path)
            self.assertNotIn("THE NOTEBOOK", doc.text)

    def test_custom_domain(self):
        destination = self.site / "root-output"
        self.build(destination, "--baseURL", "https://example.org/")
        doc = Document(destination / "index.html")
        self.assertTrue(doc.matching("a", href="/", **{"aria-current": "page"}))
        self.assertTrue(doc.matching("link", rel="canonical", href="https://example.org/"))
        self.assertTrue(doc.matching("a", href="/page/2/", rel="next"))
        self.assertTrue(Document(destination / "page/2/index.html").matching("link", rel="canonical", href="https://example.org/page/2/"))

    def test_browser_layout_and_theme(self):
        if not self.browser:
            self.skipTest("Use --browser for optional Playwright checks")
        from playwright.sync_api import sync_playwright

        handler = functools.partial(QuietHandler, directory=str(self.public))
        server = http.server.ThreadingHTTPServer(("127.0.0.1", 0), handler)
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        url = f"http://127.0.0.1:{server.server_port}/blog/"
        try:
            with sync_playwright() as p:
                browser = p.chromium.launch()
                try:
                    page = browser.new_page(color_scheme="dark", viewport={"width": 1440, "height": 1000})
                    errors = []
                    page.on("pageerror", lambda error: errors.append(str(error)))
                    page.on("response", lambda response: errors.append(f"HTTP {response.status}: {response.url}") if response.status >= 400 else None)
                    page.goto(url)
                    self.assertEqual(page.locator("html").get_attribute("data-theme"), "dark")
                    sidebar = page.locator(".sidebar").bounding_box()
                    main = page.locator("main").bounding_box()
                    self.assertLess(sidebar["x"] + sidebar["width"], main["x"])
                    self.assertLess(page.locator(".site-header").bounding_box()["y"], main["y"])
                    self.assertEqual(page.locator(".collection-header").count(), 0)
                    self.assertAlmostEqual(page.locator(".list-heading").bounding_box()["y"], main["y"], delta=1)
                    self.assertEqual(page.locator("h1.sr-only").bounding_box()["width"], 1)
                    self.assertEqual(page.locator(".category-link.is-active .category-count").inner_text(), "5")
                    if self.screenshots:
                        Path(self.screenshots).mkdir(parents=True, exist_ok=True)
                        page.screenshot(path=str(Path(self.screenshots) / "desktop-dark.png"), full_page=True)
                    page.get_by_role("button", name="切换到浅色模式").click()
                    page.reload()
                    self.assertEqual(page.locator("html").get_attribute("data-theme"), "light")
                    if self.screenshots:
                        page.screenshot(path=str(Path(self.screenshots) / "desktop-light.png"), full_page=True)
                    for width in (320, 375, 768, 1440):
                        page.set_viewport_size({"width": width, "height": 900})
                        for path in ("", "posts/note-1/", "categories/技术/"):
                            page.goto(url + path)
                            self.assertFalse(page.evaluate("document.documentElement.scrollWidth > window.innerWidth"), f"Overflow at {width}px on {path}")
                    page.set_viewport_size({"width": 375, "height": 900})
                    page.goto(url)
                    mobile_nav = page.locator(".sidebar").bounding_box()
                    self.assertLess(mobile_nav["y"] + mobile_nav["height"], page.locator("main").bounding_box()["y"])
                    if self.screenshots:
                        page.screenshot(path=str(Path(self.screenshots) / "mobile-light.png"), full_page=True)
                    page.locator(".category-link").filter(has_text="技术").click()
                    self.assertEqual(page.locator("h1.sr-only").text_content(), "技术")
                    self.assertEqual(page.locator(".category-link.is-active .category-count").inner_text(), "3")
                    page.locator(".article-link").first.click()
                    self.assertTrue(page.locator(".prose").is_visible())
                    page.goto(url)
                    page.keyboard.press("Tab")
                    self.assertEqual(page.evaluate("document.activeElement.getAttribute('href')"), "#main")
                    page.keyboard.press("Enter")
                    self.assertEqual(page.evaluate("document.activeElement.id"), "main")
                    self.assertFalse(errors, "\n".join(errors))
                    blocked = browser.new_context(color_scheme="dark")
                    blocked.add_init_script("Object.defineProperty(window, 'localStorage', {get() { throw new DOMException('Blocked', 'SecurityError'); }});")
                    blocked_page = blocked.new_page()
                    blocked_page.on("pageerror", lambda error: errors.append(str(error)))
                    blocked_page.goto(url)
                    self.assertEqual(blocked_page.locator("html").get_attribute("data-theme"), "dark")
                    blocked_page.emulate_media(color_scheme="light")
                    blocked_page.wait_for_function("document.documentElement.dataset.theme === 'light'")
                    blocked_page.get_by_role("button", name="切换到深色模式").click()
                    self.assertEqual(blocked_page.locator("html").get_attribute("data-theme"), "dark")
                    self.assertFalse(errors, "\n".join(errors))
                    blocked.close()
                    no_js = browser.new_context(java_script_enabled=False, color_scheme="light")
                    fallback = no_js.new_page()
                    fallback.goto(url)
                    self.assertTrue(fallback.locator(".article-link").first.is_visible())
                    self.assertTrue(fallback.locator(".theme-toggle").is_hidden())
                    self.assertEqual(fallback.evaluate("getComputedStyle(document.documentElement).colorScheme"), "light")
                    no_js.close()
                finally:
                    browser.close()
        finally:
            server.shutdown()
            server.server_close()
            thread.join(timeout=5)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--browser", action="store_true")
    parser.add_argument("--screenshots", help="Optional screenshot output directory (outside the repository recommended)")
    args, remaining = parser.parse_known_args()
    ThemeTests.browser = args.browser
    ThemeTests.screenshots = args.screenshots
    unittest.main(argv=[__file__, *remaining], verbosity=2)
