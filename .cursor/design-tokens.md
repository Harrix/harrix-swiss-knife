# Shared design tokens (HSK ↔ Harrix-HTML-Template)

**Mirror of** Harrix-HTML-Template `.cursor/design-tokens.md`.  
Source of visual truth for shared chrome: HTML `src/scss/_variables.scss`.  
Desktop implementation: `src/harrix_swiss_knife/apps/common/ui_chrome.py`.

When changing a row below, update **both** repos (SCSS + Python + Cursor rules).

## Brand and selection

| Role | HTML | HSK | Hex |
| --- | --- | --- | --- |
| Brand / primary | `$h-primary` | `SELECTION_BORDER` / `BUTTON_PRIMARY_BG` | `#2e86b7` |
| Soft selected fill | `$h-soft-bg` | `SELECTION_BG` | `#e8f4fc` |
| Soft hover | `$h-soft-hover` | `SELECTION_HOVER` | `#f3f8fb` |
| Brand ink | `$h-brand-ink` | `BRAND_INK` | `#1a5f7a` |
| Text on soft fill | `$h-text` | `SELECTION_TEXT` | `#1a1a1a` |
| Muted text | `$h-muted-text` | `MUTED_TEXT` | `#5c6370` |
| Surface | `$h-surface` | `SURFACE` | `#ffffff` |

## Neutrals and chrome

| Role | HTML | HSK | Hex / value |
| --- | --- | --- | --- |
| Input / default border | `$h-border` | `INPUT_BORDER` | `#dbdbdb` |
| Hairline separator | `$h-hairline` | `HAIRLINE` | `#f0f0f0` |
| Row separator | `$h-separator` | `SEPARATOR` | `#e0e0e0` |
| Control radius | `$h-control-radius` | `INPUT_RADIUS` | `0.375rem` / `6` |
| Panel radius | `$h-panel-radius` | `PANEL_RADIUS` | `0.25rem` / `4` |

## Buttons

Model: **solid primary** (Bulma `.button.is-primary`) — filled brand, no contrasting accent border.

| Role | HTML | HSK | Hex |
| --- | --- | --- | --- |
| Primary fill / border | `$h-primary` | `BUTTON_PRIMARY_BG` / `BUTTON_PRIMARY_BORDER` | `#2e86b7` |
| Primary text | white | `BUTTON_PRIMARY_FG` | `#ffffff` |
| Primary hover/pressed | `$h-brand-ink` | `BUTTON_PRIMARY_HOVER` | `#1a5f7a` |
| Secondary fill | `$h-button-secondary-bg` | `BUTTON_SECONDARY_BG` | `#f5f5f5` |
| Secondary border | `$h-border` | `BUTTON_SECONDARY_BORDER` | `#dbdbdb` |
| Success solid | `$h-success` | `BUTTON_SUCCESS_BG` | `#4caf50` |
| Danger solid | `$h-danger` | `BUTTON_DANGER_BG` | `#cc584c` |
| App CTA cyan (was soft `#e3f2fd`) | — | `BUTTON_CTA_CYAN_BG` | `#79b1d1` |
| App CTA green (was lightgreen / soft green) | — | `BUTTON_CTA_GREEN_BG` | `#4caf50` |
| App CTA mint (was `#C1ECDD`) | — | `BUTTON_CTA_MINT_BG` | `#3aaf9d` |

Solid button QSS always sets `padding: 5px 14px` and `min-height: 28px` so filled buttons match unstyled dialog height. Text/icon on fill: white/`#f4f4f4` when luminance &lt; 0.55, else `#122a3a`; low-chroma gray fills keep semantic Lucide icon colors.

Dialog idle buttons use `button_idle_qss()` (`SURFACE` + `INPUT_BORDER`). Drop zones use `drop_zone_qss()` (white, not `#f9f9f9`). `QCheckBox` / `QRadioButton` get Lucide indicators app-wide via `qt_form_chrome`.

## Do not unify across platforms

- Site navbar height / logo width vs desktop caption 32px + Win11 window buttons
- Site TOC active = text + left border; desktop lists = soft fill + border
- Screenshot selection guide `#00AEFF` (HSK only)
- Domain content accents that are not CTAs (charts, tags) unless explicitly shared

## Sync checklist

1. Change tokens in HTML `_variables.scss`
2. Mirror hex/roles in HSK `ui_chrome.py`
3. Update both `.cursor/design-tokens.md` tables if roles change
4. Update `h-brand-colors.mdc` and `hsk-ui-chrome.mdc`
5. HTML: `npm run check` / `check:css` / `build`
6. HSK: `hsk py ruff-sort-docs` + `hsk py check`
