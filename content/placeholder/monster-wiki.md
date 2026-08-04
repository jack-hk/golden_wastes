---
placeholder: true
# title: Placeholder Monster Wiki
# date: 2026-01-01T12:00:00Z
# updated: 2026-01-02T12:00:00Z
# draft: true
# type: wiki
# slug: placeholder-monster-wiki
# url: /placeholder/monster-wiki/
# aliases:
#   - /placeholder/old-monster-wiki/
# weight: 40
# description: Placeholder description for a monster wiki page.
# summary: Placeholder monster summary for cards, lists, and search results.
# author: Placeholder Author
# categories:
#   - monster
# tags:
#   - placeholder
#   - monster
# series: Placeholder Wiki Series
# image: /uploads/monster.jpg
# fitThumbnail: false # true fits the complete image inside its square search thumbnail; false crops it to fill.
# featured_image: /uploads/monster.jpg
# image_caption: Placeholder monster image caption.
# show_date: true
# show_reading_time: true
# iconColor: var(--color-accent)
# badgeOnThumbnail: true
# bookHidden: true
# BookToC: false
# infobox:
#   header: Placeholder Monster
#   image: /uploads/monster.jpg
#   icon: /SVG/village.svg
#   imageSize: 180
#   iconSize: 180
#   imageMargin: 10px auto
#   iconMargin: 10px auto
#   iconColor: var(--color-accent)
#   badgePath: /SVG/village.svg
#   badge: /SVG/village.svg
#   badgeIcon: /SVG/village.svg
#   badgeSvg: /SVG/village.svg
#   badgeEnabled: true
#   badgeOnThumbnail: true
#   badgeBackgroundColor: var(--color-accent)
#   badgeColor: var(--color-accent)
#   badgeForegroundColor: var(--color-background-light)
#   badgeSize: 32
#   labels:
#     - label: Type
#       item: Monster
#     - divider: true
#     - label: Example
#       item: "[Related page](/monster/beak-thing/)"
# also:
#   - Beak Thing
#   - Bonestalker
# references:
#   - title: Placeholder monster reference
#     url: https://example.com/monster-reference
---

# Heading level 1

## Heading level 2

### Heading level 3

#### Heading level 4

##### Heading level 5

###### Heading level 6

Normal monster text with **bold**, *italic*, ***bold italic***,
~~strikethrough~~, <u>underlined text</u>, `inline code`, and a
[link](/campaign/how-to-play/).

> A monster quotation styled like a wiki quotation.

- Trait
  - Nested trait

1. First behaviour
2. Second behaviour

- [x] Observed
- [ ] Unconfirmed

| Trait | Value |
| --- | --- |
| Example | Description |

```text
Literal stat or rules text can use a fenced code block.
```

Inline icon: {{< icon name="book" size="24" >}}

---

## Configurable images

Image attributes support `width`, `align`, `caption`, `mobileMinWidth`, and
`mobileMaxWidth`. A number without a unit is treated as pixels.

![Ordinary monster image](/uploads/monster.jpg "Ordinary image tooltip")

![Left monster image](/uploads/card1.jpg "Left image tooltip")
{width="280" align="left" caption="A left-floating monster image."}

This text wraps beside the image on desktop.

![Right monster image](/uploads/card10.jpg "Right image tooltip")
{width="35%" align="right" caption="A right-floating monster image."}

This text wraps beside the image on desktop.

![Centered monster image](/uploads/monster.jpg "Centered image tooltip")
{width="640" align="center" mobileMinWidth="240" mobileMaxWidth="480" caption="A centered monster image with mobile width limits."}

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
