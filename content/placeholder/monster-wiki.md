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
