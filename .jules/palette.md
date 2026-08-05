## 2024-06-22 - Form Accessibility & ARIA Labels in Settings
**Learning:** Found instances of `<label>` tags not associated with inputs (`htmlFor` / `id` missing), and an icon-only button without an `aria-label`.
**Action:** Always verify `htmlFor` matching `id` for labels, and ensure all icon-only interactive elements (like the eye icon for passwords) have descriptive `aria-label` or `title` attributes.
## 2024-08-05 - Missing Checkbox Focus Indicators with Tailwind
**Learning:** Tailwind's preflight styles completely remove native focus outlines from standard form elements like checkboxes (`<input type="checkbox">`). Without explicitly redefining them, these critical input elements become completely invisible to users navigating via keyboard (tabbing).
**Action:** Always ensure that explicit focus styles (e.g., `focus:outline-none focus-visible:ring-2 focus-visible:ring-blue-500 focus-visible:ring-offset-2 focus-visible:ring-offset-slate-900`) are applied to `<input type="checkbox">` and `<input type="radio">` components, particularly in dark mode where contrast requirements for focus indicators can be harder to meet.
