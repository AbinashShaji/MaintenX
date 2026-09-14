---
name: Warm Editorial Maintenance
colors:
  surface: '#fcf9f5'
  surface-dim: '#dcdad6'
  surface-bright: '#fcf9f5'
  surface-container-lowest: '#ffffff'
  surface-container-low: '#f6f3ef'
  surface-container: '#f0edea'
  surface-container-high: '#ebe8e4'
  surface-container-highest: '#e5e2de'
  on-surface: '#1c1c1a'
  on-surface-variant: '#414943'
  inverse-surface: '#31302e'
  inverse-on-surface: '#f3f0ed'
  outline: '#717972'
  outline-variant: '#c1c9c1'
  surface-tint: '#3a674f'
  primary: '#27543c'
  on-primary: '#ffffff'
  primary-container: '#3f6c53'
  on-primary-container: '#baebcc'
  inverse-primary: '#a1d1b3'
  secondary: '#6f5b3c'
  on-secondary: '#ffffff'
  secondary-container: '#fbdeb7'
  on-secondary-container: '#766142'
  tertiary: '#783a1f'
  on-tertiary: '#ffffff'
  tertiary-container: '#955134'
  on-tertiary-container: '#ffd8ca'
  error: '#ba1a1a'
  on-error: '#ffffff'
  error-container: '#ffdad6'
  on-error-container: '#93000a'
  primary-fixed: '#bceece'
  primary-fixed-dim: '#a1d1b3'
  on-primary-fixed: '#002112'
  on-primary-fixed-variant: '#224f38'
  secondary-fixed: '#fbdeb7'
  secondary-fixed-dim: '#ddc39d'
  on-secondary-fixed: '#271902'
  on-secondary-fixed-variant: '#564427'
  tertiary-fixed: '#ffdbce'
  tertiary-fixed-dim: '#ffb598'
  on-tertiary-fixed: '#370e00'
  on-tertiary-fixed-variant: '#72351b'
  background: '#fcf9f5'
  on-background: '#1c1c1a'
  surface-variant: '#e5e2de'
  bg-canvas: '#FAF7F2'
  surface-card: '#FFFFFF'
  ink-primary: '#1E1E1C'
  ink-muted: '#6B6862'
  primary-hover: '#345A44'
  border-subtle: '#E7E2D9'
  accent-blue: '#AFC8D8'
  accent-clay: '#C97B5B'
  accent-tan: '#E4C9A3'
  status-requested: '#8C8C88'
  status-approved: '#AFC8D8'
  status-on-work: '#E4C9A3'
  status-rectified: '#3F6C53'
  status-closed: '#6B6862'
  priority-low: '#AFC8D8'
  priority-medium: '#E4C9A3'
  priority-high: '#C97B5B'
  priority-critical: '#C0392B'
typography:
  display-lg:
    fontFamily: Playfair Display
    fontSize: 48px
    fontWeight: '600'
    lineHeight: 56px
    letterSpacing: -0.02em
  display-lg-mobile:
    fontFamily: Playfair Display
    fontSize: 32px
    fontWeight: '600'
    lineHeight: 40px
    letterSpacing: -0.01em
  headline-lg:
    fontFamily: Playfair Display
    fontSize: 36px
    fontWeight: '600'
    lineHeight: 44px
    letterSpacing: -0.015em
  headline-lg-mobile:
    fontFamily: Playfair Display
    fontSize: 26px
    fontWeight: '600'
    lineHeight: 34px
    letterSpacing: -0.01em
  headline-md:
    fontFamily: Playfair Display
    fontSize: 24px
    fontWeight: '600'
    lineHeight: 32px
    letterSpacing: -0.01em
  title-lg:
    fontFamily: Inter
    fontSize: 18px
    fontWeight: '600'
    lineHeight: 26px
    letterSpacing: -0.01em
  title-md:
    fontFamily: Inter
    fontSize: 16px
    fontWeight: '600'
    lineHeight: 24px
  body-lg:
    fontFamily: Inter
    fontSize: 16px
    fontWeight: '400'
    lineHeight: 26px
  body-md:
    fontFamily: Inter
    fontSize: 14px
    fontWeight: '400'
    lineHeight: 22px
  body-sm:
    fontFamily: Inter
    fontSize: 13px
    fontWeight: '400'
    lineHeight: 18px
  label-md:
    fontFamily: Inter
    fontSize: 12px
    fontWeight: '600'
    lineHeight: 16px
    letterSpacing: 0.04em
  label-sm:
    fontFamily: Inter
    fontSize: 11px
    fontWeight: '500'
    lineHeight: 14px
    letterSpacing: 0.02em
  data-mono:
    fontFamily: Inter
    fontSize: 13px
    fontWeight: '500'
    lineHeight: 18px
    letterSpacing: -0.01em
rounded:
  sm: 0.25rem
  DEFAULT: 0.5rem
  md: 0.75rem
  lg: 1rem
  xl: 1.5rem
  full: 9999px
spacing:
  space-xxs: 0.25rem
  space-xs: 0.5rem
  space-sm: 0.75rem
  space-md: 1rem
  space-lg: 1.5rem
  space-xl: 2rem
  space-2xl: 3rem
  space-3xl: 4rem
  gutter-mobile: 1rem
  gutter-tablet: 1.5rem
  gutter-desktop: 2rem
  container-max: 88rem
---

## Brand & Style

This design system establishes an editorial, calm, and dependable environment tailored for high-stakes operational workflows. Rejecting the cold, harsh utilitarianism of traditional industrial enterprise tools, it blends the poise of high-end editorial publishing with rigorous operational clarity.

The aesthetic fuses **Warm Editorial Modernism** with purposeful tactile warmth:
- **Atmospheric Restraint:** A paper-like tactile foundation that alleviates optical fatigue during continuous field and back-office usage.
- **Dignified Craftsmanship:** Sophisticated typography balances expressive literary display serifs with robust, high-legibility geometric sans-serifs for complex technical metadata.
- **Calm Authority:** Status and priority cues rely on muted, natural pigment tones—clay, sage, amber, and slate—delivering instant situational awareness without anxiety-inducing alarms.

## Colors

The palette is rooted in tactile organic pigments reminiscent of archival stationery, architectural blueprints, and weathered workshop materials.

### Application Guidelines
- **Canvas & Surface:** Always use `bg-canvas` (`#FAF7F2`) for screen backgrounds. Floating cards, data sheets, and drawers transition to pure white (`#FFFFFF`) to establish layered, crisp contrast without pure black outlines.
- **Ink & Typography:** Primary headlines and key readings rely strictly on `ink-primary` (`#1E1E1C`). Supporting metadata, secondary labels, and timestamps utilize `ink-muted` (`#6B6862`). Avoid pure black (`#000000`) anywhere in the interface.
- **Semantic Accents:** 
  - `status-rectified` and primary actions share `#3F6C53` (deep sage/forest green), communicating resolution and dependability.
  - Priority levels follow a stepped thermal spectrum: `priority-low` (`#AFC8D8`), `priority-medium` (`#E4C9A3`), `priority-high` (`#C97B5B`), and `priority-critical` (`#C0392B`).
  - Badges and indicators must combine light tinted backgrounds (15% opacity) with solid foreground text or dot indicators to preserve accessibility against paper surfaces.

## Typography

The typographic tension pairs the classical grace of an editorial serif (`Playfair Display`) with the precision of an objective sans-serif (`Inter`).

- **Display & Section Titles (`Playfair Display`):** Reserved exclusively for high-level dashboard summaries, modal intros, page headers, and milestone achievements. It infuses a bespoke, human-led architectural feel into asset tracking.
- **Operational Data & Body (`Inter`):** Deployed for all form inputs, data tables, telemetry readings, and status reports. Tabular figures (`tnum`) should be toggled on for all asset identifiers, timestamps, metrics, and quantitative readings.
- **Labels & Tags:** Uppercase tracking (`+0.04em`) applied to `label-md` lends an archival, stamped indexation look to categorical metadata.

## Layout & Spacing

This design system uses a flexible 12-column grid anchored by disciplined geometric intervals, providing airy breathing room around dense maintenance logs.

- **Rhythm & Padding:** Built upon a 4px/8px incremental base. Internal card padding ranges from `space-lg` (24px) for desktop down to `space-md` (16px) for compact field devices.
- **Responsive Adaptations:**
  - **Mobile (< 768px):** 4-column layout, 16px screen gutters. Cards take 100% width. Pinned bottom navigation bar for quick one-handed field entry.
  - **Tablet (768px – 1024px):** 8-column layout, 24px gutters. Master-detail views switch to a collapsible left panel (320px fixed) with a dynamic viewport for task resolution.
  - **Desktop (> 1024px):** 12-column layout conforming to `container-max` (1408px). Sidebar navigation (260px fixed) flanked by generous whitespace margins, allowing parallel viewing of work orders, machine schematics, and timeline logs.

## Elevation & Depth

Visual hierarchy is articulated through tonal layering and refined low-contrast outlines rather than dramatic dropshadows, ensuring an organic paper-like tactility.

- **Base Layering (Tonal Stack):**
  - **L0 (Ground):** Canvas background `#FAF7F2`.
  - **L1 (Surfaces):** Cards and tables in `#FFFFFF` with a hairline structural border: `1px solid #E7E2D9`.
  - **L2 (Interactive Floating Elements):** Dropdowns, popovers, and task detail side-drawers in `#FFFFFF`, supported by a soft, warm ambient drop shadow: `0 8px 24px -4px rgba(30, 30, 28, 0.06), 0 2px 6px -1px rgba(30, 30, 28, 0.04)`.
  - **L3 (Modals & Overlays):** Deep modal dialogues paired with a translucent backdrop overlay (`rgba(30, 30, 28, 0.35)` with `backdrop-filter: blur(4px)`).
- **Outlines & Dividers:** Subtle inner borders (`1px solid #E7E2D9`) cleanly delineate complex operational tables without visual friction. Heavy dropshadows are strictly avoided to retain clarity in bright outdoor maintenance conditions.

## Shapes

The design system employs a soft, humanized geometry that contrasts rectangular data density with pill-shaped interactive anchors:

- **Interactive Controls (Pill Form):** Primary buttons, status filters, action chips, and segment switchers use full pill radii (`rounded-full` / `9999px`).
- **Cards & Containers:** Work orders, machine logs, and asset modules utilize an expressive radius of `16px` (`rounded-lg`) to `20px` (`rounded-xl`), creating a modern, approachable feel.
- **Inputs & Dropdowns:** Text inputs and selectors sit comfortably at `10px` to `12px` rounding, retaining structure while matching surrounding curves.
- **Empty States & Organic Motifs:** Empty states and onboarding vignettes leverage soft, pebble-like organic shapes rendered in warm washes of tan (`#E4C9A3`) and soft blue (`#AFC8D8`).

## Components

### Buttons
- **Primary:** Full pill (`rounded-full`), background `#3F6C53`, text `#FFFFFF`, vertical padding `10px`, horizontal padding `24px`. Hover transitions to `#345A44`. Active state subtly scales to `0.98`.
- **Secondary:** Full pill, background `transparent`, border `1.5px solid #3F6C53`, text `#3F6C53`. Hover brings a soft wash of `rgba(63, 108, 83, 0.08)`.
- **Ghost/Tertiary:** Full pill, text `#6B6862`. Hover state: background `rgba(231, 226, 217, 0.5)`, text `#1E1E1C`.
- **Icon Buttons:** Circular (`rounded-full`), `40x40px` touch targets with 1.5px stroke icons.

### Status & Priority Badges (Chips)
- **Status Indicator:** Pill shape (`rounded-full`), `padding: 4px 12px`, font size `12px`, `font-weight: 600`.
  - *Requested:* Background `rgba(140, 140, 136, 0.15)`, text `#4A4A46`.
  - *Approved:* Background `rgba(175, 200, 216, 0.25)`, text `#2B4A5D`.
  - *On Work:* Background `rgba(228, 201, 163, 0.3)`, text `#5C441E`.
  - *Rectified:* Background `rgba(63, 108, 83, 0.15)`, text `#234231`.
  - *Closed:* Background `rgba(107, 104, 98, 0.15)`, text `#3A3834`.
- **Priority Indicator:** Miniature pill containing a 6px solid circular dot accompanied by the priority label in `12px` bold sans-serif.

### Cards & Work Order Containers
- Background `#FFFFFF`, border `1px solid #E7E2D9`, border-radius `16px`.
- Padding `20px` to `24px`.
- Includes an explicit header zone featuring the asset ID in `data-mono` alongside an editorial card title (`Playfair Display`, `headline-md`). Subtle horizontal line (`#E7E2D9`) partitions task steps and assignees.

### Form Inputs & Selectors
- Background `#FFFFFF`, border `1.5px solid #E7E2D9`, border-radius `12px`, height `44px`, padding `0 14px`.
- Text style: `Inter`, `14px`, text `#1E1E1C`. Placeholder text `#8C8C88`.
- Focus state: border-color `#3F6C53`, soft outer glow `0 0 0 3px rgba(63, 108, 83, 0.15)`.
- Error state: border-color `#C0392B`, outer glow `0 0 0 3px rgba(192, 57, 43, 0.15)`.

### Checkboxes & Radio Controls
- **Checkbox:** `20x20px`, border-radius `6px`, border `1.5px solid #6B6862`. Checked state: solid `#3F6C53` fill with white checkmark icon (1.5px stroke).
- **Radio Button:** `20x20px`, circular, border `1.5px solid #6B6862`. Checked state: inner dot of `#3F6C53` with `4px` breathing clearance.

### Data Tables & Lists
- Table headers use uppercase `label-md` in `#6B6862`, with `padding: 12px 16px`, bordered on the bottom with `1px solid #E7E2D9`.
- Row height is standard `52px` to accommodate touch selection. Hover state across rows: `#FAF7F2`.
- Numeric outputs and timestamps format with `data-mono` for horizontal tabular alignment.

### Timeline & Progress Rail
- Vertical line (`2px solid #E7E2D9`) linking sequential status steps. Active step manifests as a `#3F6C53` ring encircling a warm white center; completed steps fill solid `#3F6C53`.