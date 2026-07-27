---
placeholder: true
# title: Placeholder Lore Page
# date: 2026-01-01T12:00:00Z
# updated: 2026-01-02T12:00:00Z
# draft: true
# type: page
# slug: placeholder-lore-page
# url: /placeholder/lore-page/
# aliases:
#   - /placeholder/old-lore-page/
# weight: 10
# description: Placeholder description for a normal lore page.
# summary: Placeholder summary for cards, lists, and search results.
# author: Placeholder Author
# categories:
#   - lore
# tags:
#   - placeholder
#   - example
# series: Placeholder Series
# image: /uploads/blue-abstract.jpg
# featured_image: /uploads/blue-abstract.jpg
# image_caption: Placeholder featured-image caption.
# show_reading_time: true
# references:
#   - title: Placeholder reference one
#     url: https://example.com/reference-one
#   - title: Placeholder reference two
#     url: https://example.com/reference-two
---

# Heading level 1

## Heading level 2

### Heading level 3

#### Heading level 4

##### Heading level 5

###### Heading level 6

Normal paragraph text with **bold**, *italic*, ***bold italic***,
~~strikethrough~~, <u>underlined text</u>, `inline code`, and a
[link](/campaign/how-to-play/).

> A blockquote can contain **formatting**, links, and multiple paragraphs.
>
> This is its second paragraph.

- Unordered list item
- Another item
  - Nested item

1. Ordered list item
2. Another ordered item

- [x] Completed task
- [ ] Incomplete task

| Column one | Column two |
| --- | --- |
| Cell one | Cell two |

```text
A fenced code block preserves spacing and punctuation.
```

Inline icon: {{< icon name="book" size="24" >}}

---

## Configurable images

Image attributes support `width`, `align`, `caption`, `mobileMinWidth`, and
`mobileMaxWidth`. A number without a unit is treated as pixels.

An ordinary Markdown image has no attribute block:

![Ordinary placeholder landscape](/uploads/blue-abstract.jpg "Ordinary image tooltip")

This image floats left on larger screens:

![Left-aligned placeholder landscape](/uploads/barren.jpg "Left image tooltip")
{width="280" align="left" caption="A left-floating image with wrapped text."}

Text following a floated image wraps beside it on larger screens. On mobile,
the image becomes full width and the text returns above and below it.

This image floats right on larger screens:

![Right-aligned placeholder landscape](/uploads/mesa.jpg "Right image tooltip")
{width="35%" align="right" caption="A right-floating image sized with a percentage."}

More following text demonstrates wrapping on the opposite side of the image.

This centered image breaks the surrounding text flow:

![Centered placeholder landscape](/uploads/red-abstract.jpg "Centered image tooltip")
{width="640" align="center" mobileMinWidth="240" mobileMaxWidth="480" caption="A centered image with optional mobile width limits."}
