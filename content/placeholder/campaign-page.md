---
placeholder: true
# title: Placeholder Campaign Page
# date: 2026-01-01T12:00:00Z
# updated: 2026-01-02T12:00:00Z
# draft: true
# type: page
# slug: placeholder-campaign-page
# url: /placeholder/campaign-page/
# aliases:
#   - /placeholder/old-campaign-page/
# weight: 20
# description: Placeholder description for a campaign.
# summary: Placeholder campaign summary for cards, lists, and search results.
# author: Placeholder Author
# categories:
#   - campaign
# tags:
#   - placeholder
#   - campaign
# series: Placeholder Campaign Series
# image: /uploads/red-abstract.jpg
# fitThumbnail: false # true fits the complete image inside its square search thumbnail; false crops it to fill.
# featured_image: /uploads/red-abstract.jpg
# image_caption: Placeholder campaign image caption.
# show_reading_time: true
# eventDate: "2026-01-03"
# eventTime: "19:00"
# references:
#   - title: Placeholder campaign reference
#     url: https://example.com/campaign-reference
---

# Heading level 1

## Heading level 2

### Heading level 3

#### Heading level 4

##### Heading level 5

###### Heading level 6

Normal campaign text with **bold**, *italic*, ***bold italic***,
~~strikethrough~~, <u>underlined text</u>, `inline code`, and a
[link](/campaign/how-to-play/).

> A wiki-style quotation can contain **formatted text**.
>
> It can also contain multiple paragraphs.

- Unordered item
  - Nested item

1. First ordered item
2. Second ordered item

- [x] Completed objective
- [ ] Incomplete objective

| Session | Status |
| --- | --- |
| Opening | Complete |

```text
Use fenced code blocks for literal text.
```

Inline icon: {{< icon name="book" size="24" >}}

---

## Configurable images

Image attributes support `width`, `align`, `caption`, `mobileMinWidth`, and
`mobileMaxWidth`. A number without a unit is treated as pixels.

![Ordinary campaign image](/uploads/red-abstract.jpg "Ordinary image tooltip")

![Left campaign image](/uploads/barren.jpg "Left image tooltip")
{width="280" align="left" caption="A left-floating campaign image."}

Following text wraps to the right on desktop and returns below on mobile.

![Right campaign image](/uploads/mesa.jpg "Right image tooltip")
{width="35%" align="right" caption="A right-floating campaign image."}

Following text wraps to the left on desktop and returns below on mobile.

![Centered campaign image](/uploads/blue-abstract.jpg "Centered image tooltip")
{width="640" align="center" mobileMinWidth="240" mobileMaxWidth="480" caption="A centered campaign image with mobile width limits."}

---

## Article text-box shortcode

Use `align="left"`, `align="right"`, or `align="center"`. Use
`style="plain"`, `style="dotted"`, or `style="dashes"`. The optional
`icon` parameter accepts an image or SVG path and `iconSize` accepts any CSS
size or a unitless pixel value.

{{< textbox title="Plain full-width box" align="center" style="plain" >}}
This centered box uses normal article text with **bold**, *italics*,
[links](/campaign/how-to-play/), lists, and other Markdown.

> Blockquotes retain the standard article quotation style.
{{< /textbox >}}

{{< textbox title="Dotted left box" align="left" style="dotted" icon="/SVG/info.svg" iconSize="28" >}}
This box floats left at half width on larger screens. Following article text
wraps on its right, while smaller screens display it at full width.
{{< /textbox >}}

This paragraph demonstrates body text wrapping beside a left-aligned text box
on larger displays.

{{< textbox title="Dashed right box" align="right" style="dashes" icon="/SVG/scroll-unfurled.svg" iconSize="32px" >}}
This box floats right at half width on larger screens. Its body supports the
same **Markdown styling** as ordinary article content.
{{< /textbox >}}

This paragraph demonstrates body text wrapping beside a right-aligned text box.

## Responsive content shortcode

Values may contain one to three comma-separated views: `mobile`, `tablet`, and
`desktop`.

{{< responsive show="mobile, tablet" >}}
This **Markdown content** appears on mobile and tablet screens.
{{< /responsive >}}

{{< responsive hide="mobile" >}}
This content appears on tablet and desktop screens, but is hidden on mobile.
{{< /responsive >}}
