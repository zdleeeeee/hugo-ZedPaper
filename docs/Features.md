# Theme features

See [Shortcodes](Shortcodes.md) for content components and [Customization](Customization.md) for CSS overrides.

## Authors and links

The `author` field accepts a name, a list of names, an author object, or a mixed list. A page's authors take precedence over `[params].author` in the site configuration.

```toml
author = [
  { name = "Zed Lee", url = "about/team/#zed-lee" },
  { name = "Alice", url = "https://alice.example/" },
  "Bob"
]
```

Use a site-relative path for an internal author link. With `baseURL = 'https://example.org/blog/'`, both `about/team/#zed-lee` and `/about/team/#zed-lee` resolve to `/blog/about/team/#zed-lee`. An already prefixed path such as `/blog/about/team/#zed-lee` is preserved. External URLs are preserved. Include a trailing slash before the fragment when linking to a directory-style page.

The destination page and heading must exist and be published. For example, `content/about/team/index.md` containing `## Zed Lee` provides the `#zed-lee` anchor with Hugo's default heading IDs. Draft destinations require a draft-enabled build.

Visible author links and the author URLs in article structured data use the same normalized paths. Author names also populate the author meta tag. Set `hideAuthor = true` to hide the visible author list without removing the author metadata. An optional `email` on a site-level author supplies the RSS managing editor and author fields.

## Directory layout

Use `directory` on a section's `_index.md` to display its direct children as cards:

```toml
+++
title = 'Lore'
layout = 'directory'
showTags = true
+++
```

Each child section becomes a card with links to its direct articles. Direct articles at the directory root also receive a card. Empty sections retain their section link. Cards display in two columns and switch to one column at viewport widths of 640px or less. All cards are shown together without pagination.

Configure a child section in its own `_index.md`:

```toml
+++
title = 'Basics'
pinned = true
directoryWide = true
[cover]
image = 'basics.png'
alt = 'A map of the setting'
+++
```

- `pinned = true` places the child before unpinned cards. The existing relative order within each group is preserved. This option applies to directory cards, not the default list layout.
- `directoryWide = true` spans all columns. It is independent of pinning and remains one column on narrow screens.
- Cover images use the existing `post-entry` background treatment. Place a bundle image beside the child's `_index.md`, or use an image supported by the theme's cover component. `cover.hiddenInList` and `cover.hidden` retain their normal behavior.

Clicking a card's title or blank space opens that child. Article links open their own destinations. Hover and keyboard focus reveal arrows; touch devices show arrows without hover. Reduced-motion preferences disable movement. Page descriptions, Markdown content, breadcrumbs, RSS links, and the optional tags panel remain available.

## Archives

Create an archive content page; enabling a parameter alone does not create one:

```toml
+++
title = 'Archives'
layout = 'archives'
searchHidden = true
hiddenInHomeList = true
+++
```

Save it as `content/archives/_index.md` or `content/archives.md`. Set `[params].ShowAllPagesInArchive = true` to include regular pages beyond `mainSections`. The archive groups entries by publication year; undated entries are omitted. Drafts remain subject to Hugo's build flags.

Archive author and tag links remain independently clickable above the article link overlay. Their stacking is contained within each archive entry so they cannot cover the fixed navigation.

## Tags panel

Enable `showTags = true` on a list or directory page. The sidebar and dialog share the tags page's title and permalink, including the deployment base path. To customize that title without changing `/tags/`, add `content/tags/_index.md`:

```toml
+++
title = '标签'
+++
```

## Search

The search script reads `[params].fuseOpts`. To allow single-character searches, including single Chinese characters, configure:

```toml
[params.fuseOpts]
minMatchCharLength = 1
```

The default matching threshold is `0` and location is ignored, allowing complete keywords anywhere in indexed text. Results highlight matches and show up to five contextual excerpts per article. The search page requires `layout = 'search'` and JSON in the home output formats.
