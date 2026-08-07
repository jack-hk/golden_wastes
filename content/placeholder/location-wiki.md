---
placeholder: true
# title: Placeholder Location Wiki
# date: 2026-01-01T12:00:00Z
# updated: 2026-01-02T12:00:00Z
# draft: true
# type: wiki
# slug: placeholder-location-wiki
# url: /placeholder/location-wiki/
# aliases:
#   - /placeholder/old-location-wiki/
# weight: 50
# description: Placeholder description for a location wiki page.
# summary: Placeholder location summary for cards, lists, and search results.
# author: Placeholder Author
# categories:
#   - location
# tags:
#   - placeholder
#   - location
# series: Placeholder Wiki Series
# image: /uploads/cave.jpg
# fitThumbnail: false # true fits the complete image inside its square search thumbnail; false crops it to fill.
# featured_image: /uploads/cave.jpg
# image_caption: Placeholder location image caption.
# show_date: true
# show_reading_time: true
# iconColor: var(--color-accent)
# badgeOnThumbnail: true
# bookHidden: true
# BookToC: false
# infobox:
#   header: Placeholder Location
#   image: /uploads/cave.jpg
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
#       item: Location
#     - label: Danger
#       item: '{{< danger 3 >}}' # Shortcodes in YAML values must be quoted.
#     - divider: true
#     - label: Example
#       item: "[Related page](/location/the-beneath/)"
# also:
#   - The Beneath
#   - Gharob Region
# references:
#   - title: Placeholder location reference
#     url: https://example.com/location-reference
---

# Heading level 1

## Heading level 2

### Heading level 3

#### Heading level 4

##### Heading level 5

###### Heading level 6

Normal location text with **bold**, *italic*, ***bold italic***,
~~strikethrough~~, <u>underlined text</u>, `inline code`, and a
[link](/campaign/how-to-play/).

> A location quotation styled like a wiki quotation.

- Landmark
  - Nested detail

1. First route
2. Second route

- [x] Explored
- [ ] Unexplored

| Place | Detail |
| --- | --- |
| Example | Description |

```text
Literal descriptions can use a fenced code block.
```

Inline icon: {{< icon name="book" size="24" >}}

---

## Configurable images

Image attributes support `width`, `align`, `caption`, `mobileMinWidth`, and
`mobileMaxWidth`. A number without a unit is treated as pixels.

![Ordinary location image](/uploads/cave.jpg "Ordinary image tooltip")

![Left location image](/uploads/barren.jpg "Left image tooltip")
{width="280" align="left" caption="A left-floating location image."}

This text wraps beside the image on desktop.

![Right location image](/uploads/mesa.jpg "Right image tooltip")
{width="35%" align="right" caption="A right-floating location image."}

This text wraps beside the image on desktop.

![Centered location image](/uploads/blue-abstract.jpg "Centered image tooltip")
{width="640" align="center" mobileMinWidth="240" mobileMaxWidth="480" caption="A centered location image with mobile width limits."}

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

## Danger rating shortcode

Use `{{</* danger 3 */>}}` in page content. In an infobox, the entire shortcode
must be quoted, as shown in the front matter example above.

{{< danger 0 >}} · {{< danger 1 >}} · {{< danger 2 >}} · {{< danger 3 >}} · {{< danger 4 >}} · {{< danger 5 >}} · {{< danger 6 >}} · {{< danger 7 >}}

## Responsive content shortcode

{{< responsive show="mobile, tablet, desktop" >}}
- This item demonstrates all three allowed views.
- Inner lists and other **Markdown** are supported.
{{< /responsive >}}

{{< responsive hide="mobile, desktop" >}}
This location note is hidden on mobile and desktop, leaving it visible on tablet.
{{< /responsive >}}
