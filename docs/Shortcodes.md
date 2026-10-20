# Shortcodes

ZedPaper provides the following twelve shortcodes. Each example includes its source and rendered output. The image examples use `profile.jpg` from this post's page bundle; the audio, video, Bilibili, and YouTube examples require an internet connection to play.

Use the exact shortcode names shown below, including the capital letters in `inTextImg`. These templates use named parameters, except that `ltr` and `rtl` also accept a positional Markdown flag.

## message

Use `message` to show a chat bubble. The content between the shortcodes supports Markdown:

```text
{{</* message name="Zed" avatar="profile.jpg" align="right" nameColor="#884fad" background="#fdd76540" textColor="#333333" */>}}
Hello, I'm **Zed**! And this is an example "message"!
{{</* /message */>}}
```

All parameters are optional. `name` sets the displayed name, `avatar` sets the image URL, and `align="right"` moves the avatar and bubble to the right; the default layout is left-aligned. The color parameters default to `var(--secondary)` for `nameColor`, `var(--entry)` for `background`, and `var(--content)` for `textColor`. The background parameter is named `background`, not `backgroundColor`.

{{< message name="Zed" avatar="profile.jpg" align="right" nameColor="#884fad" background="#fdd76540" textColor="#333333" >}}
Hello, I'm **Zed**! And this is an example "message"!
{{< /message >}}

## collapse

Use `collapse` for expandable content. Supply `summary` for the clickable heading; both the heading and body support Markdown. Set `openByDefault=true` to expand it initially. Use the unquoted boolean `true`, rather than the string `"true"`.

```text
{{</* collapse summary="Click to read **more**" openByDefault=true */>}}
This section is expanded by default.

- Write notes with **Markdown**.
- Click the heading to collapse the section.
{{</* /collapse */>}}
```

{{< collapse summary="Click to read **more**" openByDefault=true >}}
This section is expanded by default.

- Write notes with **Markdown**.
- Click the heading to collapse the section.
  {{< /collapse >}}

You can also nest `message` inside `collapse`, for example to group a conversation. Omit `openByDefault` to keep it collapsed initially:

```text
{{</* collapse summary="Show the conversation" */>}}
{{</* message name="Zed" avatar="profile.jpg" */>}}
Messages inside a collapsed section still support **Markdown**.
{{</* /message */>}}
{{</* /collapse */>}}
```

{{< collapse summary="Show the conversation" >}}
{{< message name="Zed" avatar="profile.jpg" >}}
Messages inside a collapsed section still support **Markdown**.
{{< /message >}}
{{< /collapse >}}

## figure

Use `figure` to display an image with an optional title, caption, credit, and link. Set `src` to the image URL and `alt` to its text alternative. `width` and `height` set the image dimensions; `align="center"` centers the figure, and `class` adds a custom CSS class.

When `width` is set, the image keeps that width while space permits and scales down proportionally in narrower content containers. This also works when `link` wraps the image in a clickable link. Images with a specified width use automatic height to preserve their proportions; height-only sizing remains supported.

```text
{{</* figure src="profile.jpg" alt="Zed's profile picture" width="160" align="center" title="Profile picture" caption="A **figure** with a caption. " attr="Zed Lee" attrlink="https://zdleeeeee.github.io/" link="profile.jpg" target="_blank" rel="noopener noreferrer" */>}}
```

{{< figure src="profile.jpg" alt="Zed's profile picture" width="160" align="center" title="Profile picture" caption="A **figure** with a caption. " attr="Zed Lee" attrlink="https://zdleeeeee.github.io/" link="profile.jpg" target="_blank" rel="noopener noreferrer" >}}

`title` is a visible title below the image, rather than a hover tooltip. `caption` is the image description. `attr` is short for attribution: it credits the image's author or source, and `attrlink` makes that credit a link. Both `caption` and `attr` support Markdown; add a trailing space to `caption` if you want a space before the credit. If `alt` is omitted, the template uses the caption's plain text as the text alternative.

`link` makes the image clickable. Its optional `target` and `rel` parameters control the image link only; they do not apply to `attrlink`.

For a credit linking to another content page, use `attrref` instead of embedding a `relref` shortcode inside an argument:

```text
{{</* figure src="image.jpg" title="Illustration" attr="Zed Lee" attrref="/about/team/#zed-lee" */>}}
```

`attrref` resolves the content reference using Hugo's `Page.RelRef`, including page URL overrides, heading fragments, and a deployment subdirectory such as `/blog/`. The referenced content page must exist; a missing reference produces Hugo's normal reference error. `attrref` takes precedence when both `attrref` and `attrlink` are supplied. Existing `attrlink` values remain literal URLs, suitable for external credits. Do not put `{{</* relref ... */>}}` inside a quoted shortcode argument.

| Parameter          | Meaning                                                      |
| ------------------ | ------------------------------------------------------------ |
| `target="_self"`   | Opens the link in the current tab. This is also the default when `target` is omitted. |
| `target="_blank"`  | Usually opens the link in a new tab, depending on browser settings. |
| `rel="noopener"`   | Prevents the newly opened page from accessing the original window through `window.opener`. |
| `rel="noreferrer"` | Omits the `Referer` header, hiding the referring page from the destination; it also implies `noopener`. |

For `target="_self"`, you can normally omit `rel`: no new window is created, so `noopener` is unnecessary. Use `noreferrer` only if you also want to hide the referring page. For `target="_blank"`, `rel="noopener"` explicitly states the window-isolation behavior; add `noreferrer` if you want to hide the referrer as well.

For example, this image opens the original file in the current tab without needing either `target` or `rel`:

```text
{{</* figure src="profile.jpg" alt="Zed's profile picture" width="160" link="profile.jpg" caption="Click to view the original in this tab." */>}}
```

## inTextImg

Use `inTextImg` to insert a small image within a line of text. The image parameter is `url`, rather than `src`. `height` defaults to `15` pixels; `alt` provides a text alternative.

```text
Here is Zed {{</* inTextImg url="profile.jpg" height="24" alt="Zed's avatar" */>}} in the middle of a sentence.
```

Here is Zed {{< inTextImg url="profile.jpg" height="24" alt="Zed's avatar" >}} in the middle of a sentence.

## audio

Use `audio` with a `src` URL to embed the browser's audio player. The template enables playback controls and starts muted, so unmute it when listening. It does not autoplay.

```text
{{</* audio src="https://interactive-examples.mdn.mozilla.net/media/cc0-audio/t-rex-roar.mp3" */>}}
```

{{< audio src="https://interactive-examples.mdn.mozilla.net/media/cc0-audio/t-rex-roar.mp3" >}}

For a local file, place an audio file such as `sample.mp3` beside this post's `index.md` and use `src="sample.mp3"`. This shortcode only reads `src`; playback attributes are fixed by the template.

## video

Use `video` with a `src` URL to embed the browser's video player. Like `audio`, it includes controls, starts muted, and does not autoplay.

```text
{{</* video src="https://interactive-examples.mdn.mozilla.net/media/cc0-videos/flower.mp4" */>}}
```

{{< video src="https://interactive-examples.mdn.mozilla.net/media/cc0-videos/flower.mp4" >}}

For a local file, place a video such as `sample.mp4` beside this post's `index.md` and use `src="sample.mp4"`. This shortcode only reads `src`; options such as `poster`, `loop`, or `autoplay` would require a template change.

### bilibili

Use `bilibili` to embed a Bilibili video by its BV or AV ID. The player fills the content width at a 16:9 aspect ratio and does not autoplay. These examples use the same video IDs as Stack's shortcode demo.

```text
{{</* bilibili "BV15ddUBvE12" */>}}
```

{{< bilibili "BV15ddUBvE12" >}}

The optional second positional parameter selects a part (分 P), starting from `1`:

```text
{{</* bilibili "av170001" 2 */>}}
```

Named parameters are also supported. `id` is the video ID, `page` defaults to `1`, and `title` provides the iframe's accessible label:

```text
{{</* bilibili id="BV1634y1t7xR" page=1 title="Bilibili demo" */>}}
```

Pass the video ID rather than the full watch-page URL. Invalid IDs or non-positive part numbers produce a Hugo build error with the shortcode's location.

### youtube

Use `youtube` to embed a YouTube video by its 11-character ID. It shares the responsive 16:9 layout with `bilibili` and does not autoplay by default.

```text
{{</* youtube "ZJthWmvUzzc" */>}}
```

{{< youtube "ZJthWmvUzzc" >}}

For named parameters, use `id` and an optional accessible `title`. Set `autoplay=true` to request automatic playback; whether it starts depends on the browser's autoplay policy.

```text
{{</* youtube id="ZJthWmvUzzc" title="YouTube demo" autoplay=true */>}}
```

The shortcode respects Hugo's YouTube privacy settings in `hugo.toml`:

```toml
[privacy.youtube]
  privacyEnhanced = true # Use www.youtube-nocookie.com.
  disable = false       # Set true to omit YouTube players entirely.
```

## ltr

Use `ltr` to give a block a left-to-right text direction. Set `md=true` to render the body as Markdown. The positional form `{{</* ltr true */>}}` also enables Markdown.

```text
{{</* ltr md=true */>}}
This paragraph flows **from left to right**.

1. First item
2. Second item
{{</* /ltr */>}}
```

{{< ltr md=true >}}
This paragraph flows **from left to right**.

1. First item
2. Second item
   {{< /ltr >}}

Use `md=false` to emit the body without Markdown conversion. The same option is available on `rtl`; explicit unquoted booleans make the intended behavior clear.

## rtl

Use `rtl` for a block of right-to-left text, such as Arabic or Hebrew. Its `md` parameter works the same way as `ltr`.

```text
{{</* rtl md=true */>}}
هذه فقرة باللغة **العربية**.

- العنصر الأول
- العنصر الثاني
{{</* /rtl */>}}
```

{{< rtl md=true >}}
هذه فقرة باللغة **العربية**.

- العنصر الأول
- العنصر الثاني
  {{< /rtl >}}

## quote

Use `quote` for a quotation with an optional source. The body and the `source` parameter both support Markdown, so you can write the author, title, and source link together without separate parameters. The source appears below the body in smaller, right-aligned text. Write the body directly; no Markdown `>` prefix is needed.

```text
{{</* quote source="— Zed Lee, [About ZedPaper](/posts/20260901about-zedpaper/)" */>}}
Keep the quotation **simple**.

A quotation can contain more than one paragraph.
{{</* /quote */>}}
```

{{< quote source="— Zed Lee, [About ZedPaper](/posts/20260901about-zedpaper/)" >}}
Keep the quotation **simple**.

A quotation can contain more than one paragraph.
{{< /quote >}}

Omit `source` if no attribution is needed. Punctuation such as the dash is written explicitly in `source`, rather than added automatically.

For an internal content reference, use `sourceref`. It resolves the target with Hugo's `Page.RelRef`, including deployment base paths, custom page URLs, and heading fragments:

```text
{{</* quote source="— Zed Lee, About ZedPaper" sourceref="/posts/20260901about-zedpaper/" */>}}
Keep the quotation **simple**.
{{</* /quote */>}}
```

With `sourceref`, the entire `source` becomes the link text. Use text or Markdown emphasis in `source`, rather than a Markdown link, to avoid nested links. If `source` is omitted, the resolved URL is displayed. Without `sourceref`, existing Markdown links in `source` remain unchanged. A referenced page must exist; missing references produce Hugo's normal reference error. Do not embed a `relref` shortcode inside a quoted parameter.

```text
{{</* quote */>}}
A quotation without a source.
{{</* /quote */>}}
```

{{< quote >}}
A quotation without a source.
{{< /quote >}}

## rawhtml

Use `rawhtml` to insert HTML directly. It takes no parameters and emits its body without Markdown conversion. This also works when Goldmark's `unsafe` HTML rendering is disabled, as in this site's current configuration.

```text
{{</* rawhtml */>}}
<p>A native HTML progress indicator: <progress value="70" max="100">70%</progress> <strong>70%</strong></p>
{{</* /rawhtml */>}}
```

{{< rawhtml >}}

<p>A native HTML progress indicator: <progress value="70" max="100">70%</progress> <strong>70%</strong></p>
{{< /rawhtml >}}
