# 🍷 Somm.dev - Brand Identity Guide

> **Domain:** somm.dev  
> **Service Name:** Somm.dev (pronounced "sohm dot dev")  
> **Tagline:** *"Every codebase has terroir. We're here to taste it."*  

---

## Overview

**Somm.dev** is a Multi-Agentic AI code evaluation service that brings the art of wine tasting to software engineering. Just as a sommelier evaluates wine across multiple dimensions—appearance, aroma, palate, finish—we evaluate code repositories with sophisticated AI agents, each bringing a unique perspective.

This guide ensures consistent branding across all touchpoints.

---

## Brand Identity

### Official Name

**Use:** "Somm.dev" (always include .dev)

```
✅ Somm.dev
✅ The Somm.dev platform

❌ Somm (without .dev)
❌ GitSomm (legacy name)
❌ Sommelier (too generic)
❌ CodeSomm (redundant)
```

### Usage Contexts

| Context | Usage | Example |
|---------|-------|---------|
| **All Contexts** | Somm.dev | "Try Somm.dev on your repo" |
| **Formal** | Somm.dev | "Visit Somm.dev to get started" |
| **Technical** | The Somm.dev platform | "The Somm.dev platform uses 6 AI sommeliers" |
| **Product** | Somm.dev Tasting | "Run a Somm.dev Tasting on your codebase" |

---

## Core Messaging

### Elevator Pitch
> "Somm.dev is a Multi-Agentic AI code evaluation platform that brings the expertise of a master sommelier to your repositories. Six specialized AI agents analyze your code from every angle—structure, quality, security, innovation—and deliver a comprehensive tasting note with actionable recommendations."

### One-Liner
> "AI code evaluation with sommelier sophistication."

### For Developers
> "Stop guessing about code quality. Get a multi-perspective evaluation from six AI experts, each specializing in different aspects of software engineering—from architecture to security to innovation."

### For Teams
> "Standardize code review with AI consistency. Somm.dev evaluates every repository with the same rigorous standards, helping your team identify risks and opportunities that human review might miss."

---

## Terminology Guide

### Wine-to-Code Metaphors

| Wine Term | Code Equivalent | Rationale |
|-----------|-----------------|-----------|
| **Terroir** | Repository context | Origin story, environment, ecosystem |
| **Tasting** | Code evaluation | Active analysis, expert assessment |
| **Tasting Notes** | Evaluation report | Structured feedback, scores |
| **Cellar** | Repository history | Collection, aging, provenance |
| **Vintage** | Created/modified date | When the "wine" was made |
| **Bottle** | Repository | The unit of evaluation |
| **Decanter** | Analysis pipeline | Process of "opening up" the code |
| **Pour** | Analysis start | Beginning the evaluation |
| **Aeration** | Code exploration | Letting the code "breathe" |

### UI Terminology

#### Page Names

| Before (Wine-heavy) | After (Developer-friendly) |
|---------------------|---------------------------|
| Tasting Page | **Evaluate** / New Tasting |
| Tasting Notes | **Report** / Evaluation Report |
| Cellar | **History** / Your Repos |
| Bottle Card | **Repo Card** |
| Decanter Animation | **Analysis Progress** |

#### Actions

| Before | After |
|--------|-------|
| "Start Tasting" | "Analyze" / "Begin Evaluation" |
| "Add to Cellar" | "Save to History" |
| "Re-taste" | "Re-analyze" |
| "Corked" (error) | "Analysis Failed" |

#### Status Labels

| Before | After |
|--------|-------|
| Decanting | Analyzing |
| Tasting | Evaluating |
| Complete | Ready / Complete |
| Corked | Failed / Error |

---

## The Six Sommeliers

Each AI agent evaluates from a unique perspective:

### 🏛️ Marcel - Cellar Master (Structure & Metrics)
- **Focus:** Repository structure, file organization, code metrics
- **Wine Metaphor:** "Cellar management" - organizing bottles, inventory
- **Dev Terms:** Architecture, file structure, complexity, LOC
- **Color:** #8B7355 (Aged oak)

### 🎭 Isabella - Wine Critic (Code Quality)
- **Focus:** Code quality, patterns, anti-patterns
- **Wine Metaphor:** "Critical tasting" - identifying flaws and excellence
- **Dev Terms:** Code review, best practices, refactoring opportunities
- **Color:** #C41E3A (Ruby red)

### 🔍 Heinrich - Quality Inspector (Testing & Security)
- **Focus:** Test coverage, security vulnerabilities, reliability
- **Wine Metaphor:** "Quality assurance" - ensuring consistency
- **Dev Terms:** Security audit, test coverage, CI/CD
- **Color:** #2F4F4F (Slate grey)

### 🌱 Sofia - Vineyard Scout (Innovation & Tech)
- **Focus:** Technology choices, modern practices, innovation
- **Wine Metaphor:** "New varietals" - exploring new territories
- **Dev Terms:** Tech stack, modern frameworks, innovation score
- **Color:** #DAA520 (Golden)

### 🛠️ Laurent - Winemaker (Implementation)
- **Focus:** Implementation quality, performance, maintainability
- **Wine Metaphor:** "Winemaking craft" - the art of production
- **Dev Terms:** Implementation patterns, performance, maintainability
- **Color:** #228B22 (Forest green)

### 🎯 Jean-Pierre - Master Sommelier (Synthesis)
- **Focus:** Final synthesis, overall assessment, recommendations
- **Wine Metaphor:** "Master verdict" - the final word
- **Dev Terms:** Overall score, final recommendations, pairing suggestions
- **Color:** #4169E1 (Royal blue)

---

## Scoring System

### Point Scale (0-100)

| Score Range | Badge | Description |
|-------------|-------|-------------|
| 95-100 | 🏆 **Legendary** | Exceptional, rare quality |
| 90-94 | 🥇 **Grand Cru** | Outstanding, highly recommended |
| 85-89 | 🥈 **Premier Cru** | Excellent, well-crafted |
| 80-84 | 🥉 **Village** | Good, solid quality |
| 70-79 | 🏅 **Table** | Acceptable, everyday quality |
| 60-69 | 🍷 **House Wine** | Light, enjoyable, casual use |
| <60 | ⚠️ **Corked** | Below standards, needs work |

### Alternative: Star Rating

```
★★★★★ (95-100) - Legendary
★★★★☆ (85-94)  - Excellent
★★★☆☆ (75-84)  - Good
★★☆☆☆ (65-74)  - Fair
★☆☆☆☆ (<65)    - Needs Work
```

---

## Visual Design System

### Color Palette

```css
:root {
  /* Primary Wine Colors */
  --somm-burgundy: #722F37;
  --somm-burgundy-dark: #5A252C;
  --somm-burgundy-light: #8B3A44;
  
  /* Champagne/Accent */
  --somm-champagne: #F7E7CE;
  --somm-gold: #DAA520;
  
  /* Cellar Atmosphere */
  --somm-cellar: #2E4A3F;
  --somm-cellar-dark: #1A2F26;
  --somm-parchment: #FAF4E8;
  
  /* Dark Mode Base */
  --somm-dark: #1A1A1D;
  --somm-dark-card: #252528;
  
  /* Sommelier Colors */
  --somm-marcel: #8B7355;      /* Oak */
  --somm-isabella: #C41E3A;    /* Ruby */
  --somm-heinrich: #2F4F4F;    /* Slate */
  --somm-sofia: #DAA520;       /* Gold */
  --somm-laurent: #228B22;     /* Forest */
  --somm-jeanpierre: #4169E1;  /* Royal */
}
```

### Typography

**Headings:** Playfair Display (serif)
- Elegant, sophisticated
- Page titles, major headings

**Body:** Inter (sans-serif)
- Modern, readable
- Body text, UI elements

**Accent:** Cormorant Garamond (serif)
- Classic, wine label aesthetic
- Quotes, special callouts

---

## Voice & Tone

### Brand Voice Characteristics

1. **Sophisticated but Approachable**
   - Wine expertise without pretension
   - Technical depth without jargon overload

2. **Confident but Humble**
   - Clear assessments without arrogance
   - AI-assisted, not AI-replacement

3. **Visual & Evocative**
   - Use sensory language
   - Paint pictures with words

### Tone by Context

| Context | Tone | Example |
|---------|------|---------|
| **Landing Page** | Inspiring | "Discover the terroir of your codebase" |
| **Analysis Progress** | Reassuring | "Jean-Pierre is preparing the final verdict..." |
| **Error Messages** | Helpful | "This bottle couldn't be opened. Let's try another." |
| **Results** | Celebratory | "A Grand Cru-worthy implementation!" |
| **Technical Docs** | Clear | "Rate limits: 10 evaluations per hour" |

---

## Implementation Checklist

### Code Changes

- [ ] `package.json`: `"name": "somm-dev"`
- [ ] Backend module names: `somm_dev/`
- [ ] Database collections: `somm_dev_*`
- [ ] Redis keys: `somm_dev:*` prefix
- [ ] Environment variables: `SOMM_DEV_*`

### Documentation

- [ ] README.md: All references updated
- [ ] API docs: Service name updated
- [ ] Code comments: Updated terminology

### UI/UX

- [ ] Page titles: `<title>Somm.dev - AI Code Evaluation</title>`
- [ ] Meta tags: Open Graph, Twitter cards
- [ ] Logo: Remove "Git" prefix if present
- [ ] Loading states: "Somm.dev is analyzing..."
- [ ] Error messages: "Somm.dev encountered an issue..."

### Marketing

- [ ] Social media handles: @sommdev
- [ ] Email templates: "Welcome to Somm.dev"
- [ ] Blog posts: Updated references

---

## Domain Strategy

| Domain | Purpose | Status |
|--------|---------|--------|
| **somm.dev** | Primary service | ✅ Active |
| api.somm.dev | Backend API | Planned |
| docs.somm.dev | Documentation | Planned |
| blog.somm.dev | Technical blog | Future |

---

## Competitor Differentiation

| Feature | Somm.dev | Traditional Code Review | Other AI Tools |
|---------|------|------------------------|----------------|
| **Perspective** | 6 specialized agents | 1-2 human reviewers | 1 general AI |
| **Metaphor** | Wine tasting | Checklist | Generic analysis |
| **Output** | Narrative + scores | Comments | Metrics only |
| **UX** | Immersive, visual | Text-heavy | Dashboard |
| **Memorable** | Unique concept | Standard | Forgettable |

---

## File Naming Conventions

### Components

```
somm-evaluate/          # Evaluation form
somm-report/            # Results page
somm-history/           # Repository history
somm-progress/          # Analysis progress indicator
```

### API Routes

```
POST /api/evaluate      # Start evaluation
GET /api/report/:id     # Get results
GET /api/history        # User history
GET /api/stream/:id     # SSE progress stream
```

### Database Collections

```javascript
somm_users              // User data
somm_evaluations        // Evaluation jobs
somm_results            // Evaluation results
somm_events             // SSE events
```

---

## Quick Reference Card

```
┌─────────────────────────────────────────────────┐
│  SOMM.DEV BRAND QUICK REFERENCE                 │
├─────────────────────────────────────────────────┤
│                                                 │
│  Name:        Somm.dev                          │
│  Domain:      somm.dev                          │
│  Tagline:     "Every codebase has terroir."     │
│                                                 │
│  Primary:     #722F37 (Burgundy)                │
│  Accent:      #F7E7CE (Champagne)               │
│  Background:  #FAF4E8 (Parchment)               │
│                                                 │
│  Evaluate → Report → History                    │
│                                                 │
│  6 Sommeliers:                                  │
│  Marcel (Structure)      #8B7355               │
│  Isabella (Quality)      #C41E3A               │
│  Heinrich (Security)     #2F4F4F               │
│  Sofia (Innovation)      #DAA520               │
│  Laurent (Implementation) #228B22              │
│  Jean-Pierre (Synthesis) #4169E1               │
│                                                 │
└─────────────────────────────────────────────────┘
```

---

*"In code as in wine, the finest qualities reveal themselves to those who know how to taste."*

— The Somm.dev Team 🍷
