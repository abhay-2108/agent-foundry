---
name: frontend-design
description: >-
  Use this skill when designing, building, or refining web and mobile user interfaces.
  Enforces modern aesthetic excellence, responsive layouts, cohesive design systems,
  micro-animations, accessible typography, and distinctive visual polish.
---

# Frontend Design & UI/UX Craftsmanship

## Overview

Crafts modern, aesthetically exceptional user interfaces and design systems. Enforces curated HSL color palettes, accessible contrast ratios, fluid typography, dark mode architectures, micro-animations, and responsive layouts.

## When to Use

- When creating web applications, landing pages, dashboards, or mobile interfaces.
- When styling UI components, establishing CSS design tokens, or overhauling visual aesthetics.
- When transitioning rough wireframes or functional prototypes into polished, production-ready interfaces.
- Trigger phrases: `"build frontend"`, `"design UI"`, `"style this component"`, `"make it look modern"`, `"improve UI/UX"`.
- **When NOT to use**: Backend database optimization (use `backend-architecture`) or low-level LLM token streaming repair (use `agentic-ui-patterns`).

## Core Process & UI/UX Design System Craftsmanship

## Core Design Principles

### 1. Distinctive Visual Excellence (No Generic "AI Looks")
- **Curated Color Palettes**: Never use default saturated reds, blues, or greens. Use harmonious HSL/OKLCH color palettes (e.g., slate/charcoal backgrounds with vibrant electric violet, emerald, or warm amber accents).
- **Modern Typography**: Pair distinctive typefaces (e.g., *Inter*, *Plus Jakarta Sans*, *Outfit*, or *JetBrains Mono* for code) instead of generic system defaults. Establish clear scale ratios (12px, 14px, 16px, 20px, 24px, 32px, 48px).
- **Depth & Dimension**: Use layered glassmorphism (`backdrop-filter: blur(12px)`), subtle gradient borders (`linear-gradient(135deg, rgba(255,255,255,0.1), transparent)`), and multi-layered soft shadows (`box-shadow: 0 4px 20px -2px rgba(0,0,0,0.2)`).

### 2. Micro-Interactions & Fluid Motion
- **Interactive Feedback**: Every clickable element must have distinct hover, focus-visible, and active states (`transition: all 0.2s cubic-bezier(0.16, 1, 0.3, 1)`).
- **Delightful Micro-animations**: Subtle scale bumps on click (`transform: scale(0.98)`), skeleton loaders during async state transitions, and smooth entrance transitions for modal dialogs and dropdown menus.

### 3. Responsive & Adaptive Layouts
- Design mobile-first using modern CSS Grid and Flexbox.
- Ensure fluid layouts that look balanced across mobile (375px), tablet (768px), desktop (1280px), and ultrawide displays.

---

## Step-by-Step UI Development Workflow

```
┌────────────────────────────────────────────────────────┐
│               Frontend Craftsmanship Flow             │
├──────────────┬──────────────┬─────────────┬────────────┤
│ 1. Design    │ 2. Component │ 3. Dynamic  │ 4. Polish  │
│    Tokens    │    Structure │    State    │    & A11y  │
└──────────────┴──────────────┴─────────────┴────────────┘
```

### Step 1: Establish Design Tokens (`index.css` / Theme)
Define global CSS variables before writing component markup:
```css
:root {
  /* Color Palette */
  --bg-primary: #0b0f17;
  --bg-surface: rgba(22, 27, 38, 0.75);
  --border-subtle: rgba(255, 255, 255, 0.08);
  --text-primary: #f8fafc;
  --text-muted: #94a3b8;
  --accent-primary: #6366f1;
  --accent-gradient: linear-gradient(135deg, #6366f1 0%, #a855f7 100%);

  /* Spacing & Radii */
  --radius-sm: 6px;
  --radius-md: 12px;
  --radius-lg: 20px;
  
  /* Transitions */
  --transition-smooth: 200ms cubic-bezier(0.16, 1, 0.3, 1);
}
```

### Step 2: Component Architecture
- Build small, reusable, single-responsibility components (Card, Button, Badge, Modal, Input).
- Isolate layout concerns: use Flexbox for 1D alignments, CSS Grid for 2D page layouts.
- Always handle empty states, loading states, and error states gracefully.

## Common Rationalizations

| Rationalization | Reality |
|---|---|
| *"Default browser fonts and plain blue/gray colors are fine for MVP."* | First impressions dictate product credibility; premium typography, sleek dark mode, and cohesive color palettes transform perception instantly. |
| *"We don't need to test mobile layout until the desktop version is done."* | Desktop-first layouts almost always require painful, destructive refactoring to support responsive mobile viewports. |
| *"Animations are just eye candy that slow down the interface."* | Subtle 150-250ms micro-interactions provide critical cognitive feedback on user actions and make interfaces feel alive and responsive. |
| *"Accessibility contrast checks can be skipped for dark mode."* | Low-contrast gray text on dark backgrounds causes severe eye strain and violates WCAG AA standards. |

## Red Flags

- Using generic browser defaults (Times New Roman, Arial, unstyled HTML buttons).
- Hardcoding ad-hoc hex colors across components instead of using a unified design token system.
- Layouts that break or require horizontal scrolling on viewports under 768px.
- Sluggish or jarring animations exceeding 350ms or triggering layout recalculations (animating `width`/`height` instead of `transform`/`opacity`).

## Verification

After completing the workflow, confirm:
- [ ] Design system defines tokens for colors, spacing, typography, and elevation.
- [ ] Color contrast ratios meet WCAG AA standards (>4.5:1 for normal text).
- [ ] Layout is verified responsive across mobile (375px), tablet (768px), and desktop (1440px).
- [ ] Interactive states (hover, active, focus-visible, disabled) are implemented with smooth transitions.
