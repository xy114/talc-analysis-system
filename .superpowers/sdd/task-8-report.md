# Task 8: Typography and Spacing Polish

**File**: `presentation/slides.html`
**Date**: 2026-06-27

## Changes Made

### 1. Font Size Consistency

| Element | Before | After | Notes |
|---------|--------|-------|-------|
| `.slide-title` (CSS) | 28pt | 28pt | Unchanged — was already correct |
| Cover `.slide-title` (inline) | 38pt | removed | Now inherits 36pt from `.slide-cover .slide-title` CSS rule |
| Closing `.slide-dark .slide-title` | (no rule) | `font-size: 36pt` | Added CSS rule; removed inline `font-size:40pt` override |
| `.card-header` (CSS) | 15pt | 15pt | Unchanged — was already correct |
| Slide 11 paper mini-card headers (inline) | 11pt | removed | Now inherits 15pt from CSS rule |
| Action plan card headers (inline) | 16pt | 15pt | Changed inline to match CSS rule |
| `body` (CSS) | 16pt | 16pt | Unchanged — was already correct |

### 2. Slide Padding (Whitespace)

| Property | Before | After |
|----------|--------|-------|
| `.slide` padding | `48px 64px 36px 64px` | `52px 72px 40px 72px` |

Increased top, right, and bottom padding for more breathing room.

### 3. Font Fallback Chains

Verified — already complete and matching requirements:

```
--font-title: 'Source Han Sans SC', 'Noto Sans SC', 'Microsoft YaHei', sans-serif;
--font-body: 'Source Han Serif SC', 'Noto Serif SC', 'SimSun', serif;
```

No changes needed.

### 4. Line Height

Added `line-height: 1.6` to `.content` class for better paragraph readability.

### 5. Card Padding / Gap

Verified — `.card` already has `padding: 20px` and `gap: 8px`. No changes needed.

### 6. Table Readability

Added alternating row background color for `.data-table`:
- Light theme: `tr:nth-child(even) td { background: #f9fafb; }`
- Dark theme: `tr:nth-child(even) td { background: rgba(255,255,255,0.04); }`

## Verification

- No slide content was changed — only CSS rules and inline style overrides
- All `.slide-title` elements use 28pt (base rule) or 36pt (cover/closing special slides)
- All `.card-header` elements use 15pt
- Slide 12 data table rows unaffected by nth-child rule (existing inline `style="background:..."` on section headers takes priority due to higher specificity)
