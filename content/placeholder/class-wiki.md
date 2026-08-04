---
placeholder: true
# title: Placeholder Class Wiki
# header: The Placeholder Class
# date: 2026-01-01T12:00:00Z
# updated: 2026-01-02T12:00:00Z
# draft: true
# type: wiki
# slug: placeholder-class-wiki
# url: /placeholder/class-wiki/
# aliases:
#   - /placeholder/old-class-wiki/
# weight: 30
# description: Placeholder description for a class wiki page.
# summary: Placeholder class summary for cards, lists, and search results.
# author: Placeholder Author
# categories:
#   - class
# tags:
#   - placeholder
#   - class
# series: Placeholder Wiki Series
# image: /uploads/artificer.jpg
# fitThumbnail: false # true fits the complete image inside its square search thumbnail; false crops it to fill.
# featured_image: /uploads/artificer.jpg
# image_caption: Placeholder class image caption.
# show_date: true
# show_reading_time: true
# iconColor: var(--color-accent)
# badgeOnThumbnail: true
# bookHidden: true
# BookToC: false
# infobox:
#   header: Placeholder Class
#   image: /uploads/artificer.jpg
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
#       item: Class
#     - divider: true
#     - label: Example
#       item: "[Related page](/campaign/how-to-play/)"
# also:
#   - Artificer
#   - How to play
# references:
#   - title: Placeholder class reference
#     url: https://example.com/class-reference
---

# Heading level 1

## Heading level 2

### Heading level 3

#### Heading level 4

##### Heading level 5

###### Heading level 6

Normal class text with **bold**, *italic*, ***bold italic***,
~~strikethrough~~, <u>underlined text</u>, `inline code`, and a
[link](/campaign/how-to-play/).

> A class quotation styled like a wiki quotation.

- Feature
  - Nested feature

1. First step
2. Second step

- [x] Available ability
- [ ] Locked ability

| Level | Feature |
| --- | --- |
| One | Example |

```text
Literal rules or examples can use a fenced code block.
```

Inline icon: {{< icon name="book" size="24" >}}

---

## Configurable images

Image attributes support `width`, `align`, `caption`, `mobileMinWidth`, and
`mobileMaxWidth`. A number without a unit is treated as pixels.

![Ordinary class image](/uploads/artificer.jpg "Ordinary image tooltip")

![Left class image](/uploads/barbarian.jpg "Left image tooltip")
{width="280" align="left" caption="A left-floating class image."}

This text wraps beside the image on desktop.

![Right class image](/uploads/bard.jpg "Right image tooltip")
{width="35%" align="right" caption="A right-floating class image."}

This text wraps beside the image on desktop.

![Centered class image](/uploads/fighter.jpg "Centered image tooltip")
{width="640" align="center" mobileMinWidth="240" mobileMaxWidth="480" caption="A centered class image with mobile width limits."}

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
