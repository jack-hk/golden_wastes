---
placeholder: true
# title: Placeholder Card Portal
# date: 2026-01-01T12:00:00Z
# draft: true
# type: page
# slug: placeholder-card-portal
# url: /placeholder/card-portal/
# aliases:
#   - /placeholder/old-card-portal/
# weight: 70
# description: Placeholder containing every card portal option.
# summary: Placeholder card portal summary.
# portal_view: card
# card_count: 3
# min_card_count: 3
# random_cards: false
# cards:
#   - /class/artificer/
#   - /class/barbarian/
#   - /class/bard/
# truncate_limit: 100
# carousel_on_desktop: false
# show_intro_text: true
# intro_text: Choose your path. Each class offers unique abilities and playstyles.
# show_bottom_textbox: true
# bottom_textbox_text: The cards have spoken. Choose your path wisely.
# image: /uploads/tools.jpg
---

# Heading level 1

## Heading level 2

### Heading level 3

#### Heading level 4

##### Heading level 5

###### Heading level 6

Portal text supports **bold**, *italic*, ***bold italic***,
~~strikethrough~~, <u>underlining</u>, `inline code`, [links](/), lists,
tables, fenced code blocks, blockquotes, horizontal rules, and the `icon`
shortcode.

> Portal blockquote example.

- List item
- Another item

| Option | Value |
| --- | --- |
| Layout | Card |

Inline icon: {{< icon name="book" size="24" >}}

---

## Configurable images

Image attributes support `width`, `align`, `caption`, `mobileMinWidth`, and
`mobileMaxWidth`. A number without a unit is treated as pixels.

![Ordinary portal image](/uploads/tools.jpg "Ordinary image tooltip")

![Left portal image](/uploads/barren.jpg "Left image tooltip")
{width="280" align="left" caption="A left-floating portal image."}

Text wraps beside this image on desktop.

![Right portal image](/uploads/mesa.jpg "Right image tooltip")
{width="35%" align="right" caption="A right-floating portal image."}

Text wraps beside this image on desktop.

![Centered portal image](/uploads/blue-abstract.jpg "Centered image tooltip")
{width="640" align="center" mobileMinWidth="240" mobileMaxWidth="480" caption="A centered portal image with mobile width limits."}
