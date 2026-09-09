---
name: frontend-design
description: >-
  Use this skill when designing, building, or refining web and mobile user interfaces.
  Enforces modern aesthetic excellence, responsive layouts, cohesive design systems,
  micro-animations, accessible typography, and distinctive visual polish.
---

# Frontend Design & UI/UX Craftsmanship

Guides the creation of visually stunning, highly interactive, and responsive user interfaces that deliver a premium first impression while adhering to accessibility and performance standards.

## When to Use This Skill
- When creating web applications, landing pages, dashboards, or mobile interfaces.
- When styling UI components, establishing CSS design tokens, or overhauling visual aesthetics.
- When transitioning rough wireframes or functional prototypes into polished, production-ready interfaces.
- Trigger phrases: `"build frontend"`, `"design UI"`, `"style this component"`, `"make it look modern"`, `"improve UI/UX"`.

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

## Anti-Patterns & Traps to Avoid

1. **Ad-Hoc Hex Code Sprawl**: Scattering uncoordinated arbitrary hex values (`#333`, `#007bff`, `#e2e8f0`) across multiple stylesheets instead of referencing semantic design tokens (`var(--bg-surface)`).
2. **Generic "90s Default" Styling**: Using browser-default system fonts, sharp unrounded borders, raw primary colors, and flat hover states. Premium modern interfaces require tailored font pairings (e.g., Inter, Outfit), subtle glassmorphism, and smooth cubic-bezier transitions.
3. **Animating Layout-Reflow Properties**: Animating `height`, `width`, `top`, or `margin` during transitions. This forces CPU browser reflows and drops frame rates below 60fps. Always animate GPU-accelerated `transform` (`translate`, `scale`) and `opacity`.
4. **The "Happy Path Only" Trap**: Designing solely for perfectly populated datasets. An interface is incomplete if it lacks polished skeleton loaders, zero-data empty states, and gracefully styled error alerts.

---

## Quality Checklist

- [ ] Central design tokens (`:root`) define colors, radii, spacing, and transition curves.
- [ ] Text contrast conforms strictly to WCAG AA guidelines (minimum 4.5:1 ratio).
- [ ] Micro-interactions (hover, active, focus-visible) are implemented on all interactive elements.
- [ ] Layout animations use GPU-accelerated properties (`transform`, `opacity`) with smooth easings.
- [ ] Empty states, loading skeletons, and error messages are explicitly styled.
- [ ] Mobile viewports are responsive with touch targets measuring at least $44 \times 44\text{px}$.
