# Customizing styles

## Extend individual rules

Put site-specific CSS under the site's `assets/css/extended/` directory, using a filename that does not collide with a theme asset. For example:

```text
assets/
  css/
    extended/
      blockquote.css
```

```css
.md-content blockquote {
    margin: 1rem 0;
    color: var(--secondary);
    border: 0;
    background: var(--code-bg);
    border-radius: 0;
    padding: var(--radius) var(--content-gap);
}
```

ZedPaper automatically bundles `css/extended/*.css` after its core styles. This overrides the matching properties while retaining the theme's headings, links, tables, lists, code blocks, and other Markdown styles. No template changes or `@import` are needed. Normal CSS specificity still applies; match the original selector or use a narrowly scoped, more specific selector when necessary.

The `.md-content` scope covers rendered Markdown containers, including article content and other theme components that use the same class. For changes limited to full article bodies, use `.post-content.md-content blockquote` instead.

## Replace an entire theme asset

Hugo gives project assets priority over theme assets at the same relative path. Creating a project file at:

```text
assets/css/common/md-content.css
```

replaces the theme's entire file at that path. Hugo does not merge the two files. A project file containing only a blockquote rule therefore removes all the other Markdown rules supplied by the theme's file.

Use same-path replacement only when you intend to maintain the complete asset yourself. For a partial customization, move the file to a unique name under `assets/css/extended/` and remove the original same-path override. The same asset precedence applies within `extended`, so avoid reusing a theme filename there as well.

## Keep link layers local

Archive entries include an article-wide link and independently clickable author and tag links. These metadata links need a positive `z-index` to sit above the article overlay. `.archive-entry` uses `isolation: isolate` to keep those layers inside the entry and below the fixed header.

When adding similar overlays to new components, establish a local stacking context rather than increasing global navigation or metadata `z-index` values. Preserve independent keyboard focus and click targets for nested content links; do not nest anchors inside an enclosing card anchor.
